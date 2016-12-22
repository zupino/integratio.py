from scapy.all import *
from common import *
from tcz import TCZee
from httz import HTTZee
from dnz import DNZee
import time
import sys
import signal
from functools import wraps
# Just a small utility to get from system the ip of a specific network interface
import socket
import fcntl
import struct
import threading
import inspect

from Queue import Queue
from threading import Thread

class Connector(Automaton):
    def parse_args(self, jsonConfig={}, **kargs):
        Automaton.parse_args(self, **kargs)
        self.config = jsonConfig
        self.lastReceived = ""
        # set listening port
        if 'listeningPort' in jsonConfig:
            self.localPort = int( jsonConfig['listeningPort'] )
        else:
            self.localPort = 80

        # TODO This is duplicate code, we can keep it only in the connector
        # and reference the local ip inform from the Connector in TCZee
        if 'listeningInterface' in self.config:
            self.interface = str( self.config['listeningInterface'] )
        else:
            self.interface = "wlan0"

        # We are assuming here that IntegratioWebServer is listening on wlan0 interface
        try:
            # TODO  This step define on which interface (and so IP address) the TCZ will listen
            #       to. Should not be hardcoded but should be part of the JSON configuration
            self.localAddr = get_ip_address(self.interface)
            #self.myIp = 0
            print "MyIP address: " + str(self.localAddr)
        except IOError:
            self.localAddr = 0
            print "\t[WARNING] 'wlan0' interface not available"
            print "not possible to get local IP address for master filter."
            pass

        self.connections = []

    # check only matching incoming packets
    def master_filter(self, pkt):
        if (self.localAddr != 0):
            return  ( IP in pkt and TCP in pkt \
                    and pkt[IP].dst == self.localAddr \
                    and pkt[TCP].dport == self.localPort
                    )
        else:
            return  ( IP in pkt and TCP in pkt \
                    and pkt[TCP].dport == self.localPort
                    )
    
    # This is a tool method used to recognized if 'pkt'
    # is a retransmitted packet or not.
    # This will be useful when we will implement different retransmission policies
    # for the moment we use to avoid increasing self.ack when we received a retransmitted packet
    def isRetransmit(self, pkt):
        if (self.lastReceived == ""):
            return False
        
        if(Padding in pkt):
            pkt[Padding] = None
        if(Padding in self.lastReceived):
            self.lastReceived[Padding] = None

        else:
            if(
                (self.lastReceived[TCP].ack == pkt[TCP].ack) and \
                (self.lastReceived[TCP].seq == pkt[TCP].seq) and \
                (self.lastReceived[TCP].payload == pkt[TCP].payload)
            ):
                return True
            else:
                return False



    # BEGIN state
    @ATMT.state(initial=1)
    def CON_BEGIN(self):
        # DNZee component for DNS look-up from browser 
        # DNS is using UDP-only implementation for the time-being.
        dnz = DNZee(self.config, debug=3)
        dnzThread = Thread(target=dnz.run, name='DNS_Thread')
        dnzThread.daemon = True
        # Starting the TCZ Threads
        dnzThread.start()
        raise self.CON_LISTEN()

    @ATMT.state()
    def CON_LISTEN(self):
        pass

    @ATMT.receive_condition(CON_LISTEN)
    def con_receive_syn(self, pkt):
        
        if( 'S' in flags(pkt[TCP].flags) and not self.isRetransmit(pkt) ):
            # tcz = TCZee(self.config, pkt, debug=3)
            # Check impact of DEBUG messages on performances

            # BD: issue#17: For creating a dummy Httz for time category
            # cases. status_http parameter is passed to HTTZee class.
            # status_http = 0 means dummy httz component used for time.
            # status_http = 1 means proper httz component used for content.
            if self.config['category']=='time':
                # MZ 22.12.2016 Still passing config, even if TCZ does not use it anymore.
                # For this reason we need to configure TCZ manually
                tcz = TCZee(self.config, pkt, debug=3)
                tcz.confTCZ(self.localPort, self.interface)
                cd = confDelay(self.config['state'], self.config['action'], self.config['parameter'])
                tcz.addDelayConf(cd)

                # Prepare only the Thread for TCZ
                # BD: removed the threading in my current testing
                tczThread = Thread(target=tcz.run, name='tcz_Thread_time')
                tczThread.daemon = True

                # Starting the TCZ Threads
                tczThread.start()

            elif self.config['category']=='content':
                # Create TCZ and HTTZ Objects
                tcz = TCZee(self.config, pkt, debug=3)
                httz = HTTZee(tcz)

                # Prepare HTTZ Thread
                httzThread = Thread(target=httz.run, name='httz_Thread_Content')
                httzThread.daemon = True

                # Prepare a separate thread for the TCZee run
                tczThread = Thread(target=httz.connection, name='tcz_Thread_Content')

                # Starting the respective Threads
                tczThread.start()
                httzThread.start()
            elif self.config['category'] == 'packet':
                # MZ 22.12.2016 Same as for the time category above
                tcz = TCZee(self.config, pkt, debug=3)
                tcz.confTCZ(self.localPort, self.interface)
                cp = confTCZ(self.config['state'], self.config['action'], self.config['parameter'])
                tcz.addPacketConf(cp)

                tczThread = Thread(target=tcz.run, name='tcz_Thread_Packet')
                tczThread.deamon = True
                tczThread.start()
                
            self.lastReceived = pkt
            self.connections.append(tcz)
            # TODO here we create a new instance of
            # HTTZee (that contains a TCZee).
            #
            # 1. TCZee need to start from SYN_ACK sent state
            #
            # 2. TCZee master_filter should be change to accept
            #    only packet that belongs to his connection
            #
            # 3. Connector needs to keep track of current open
            #    connections and avoid create new Thread for
            #    re-transmitted packets.
            #
            # 4. When connection is closed, HTTZ Thread should die
            #    and notify Connector

        raise self.CON_LISTEN()
