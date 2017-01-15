#!/usr/bin/python

import json
from scapy.all import *
import sys
sys.path.append('.')
from libs.connector import Connector
import socket
from libs.common import *

log_interactive.setLevel(1)

jconfig = {\
    "test-id"   : "General test 1",\
    "interface" : "eth0",\
    "tcp-port"  : 80,\
    "configs"     : [\
        {\
            "category"  : "content",\
            "parameters": [\
                {\
                        "resource"  : "/",\
                        "http-status" : "HTTP/1.1 200 OK\r\n",\
                        "body"      : "Response for the main resource /",\
                        "headers"   : "Connection: close\r\nDate: Sat, 27 Aug 2016 18:51:19 GMT\r\nServer: Apache/2.4.10 (Unix)\r\n"\
                },\
                {\
                        "resource"      : "/500",\
                        "http-status"   : "HTTP/1.1 500 Internal Server error\r\n",\
                        "body"          : "Response for the 500 error",\
                        "headers"       : "Connection: close\r\nDate: Sat, 27 Aug 2016 18:51:19 GMT\r\nServer: Apache/2.4.10 (Unix)\r\n"\
                },\
                {\
                        "resource"      : "/404",\
                        "body"          : "Response for the 404 error",\
                        "http-status" : "HTTP/1.1 404 Resource Not Found\r\n",\
                        "headers"       : "Connection: close\r\nDate: Sat, 27 Aug 2016 18:51:19 GMT\r\nServer: Apache/2.4.10 (Unix)\r\n"\
                },\
                {\
                        "resource"      : "/favicon.ico",\
                        "http-status"   : "HTTP/1.1 200 OK\r\n",\
                        "body"          : "FavICO",\
                        "headers"       : "Connection: close\r\nDate: Sat, 27 Aug 2016 18:51:19 GMT\r\nServer: Apache/2.4.10 (Unix)\r\n"\
                }\
            ]\
        }\
    ]\
} 

jjconfig = {\
    "test-id"   : "General test 1",\
    "interface" : "eth0",\
    "tcp-port"  : 80,\
    "configs"     : [\
        {
            "category"  : "packet",
            "parameters":[
                {
                    "sub-category":"tcz",
                    "state"     : "BEGIN",
                    "action"    : "BEGIN",
                    "flags"      : 'RP'
                }
            ]
        },
        {
            "category"  : "time",
            "parameters": [
                {
                    "state"     : "ESTABLISHED",
                    "action"    : "sendAck",
                    "delay"     : 0.1
                },
                {
                    "state"     : "ESTABLISHED",
                    "action"    : "send_response",
                    "delay"     : 0.1
                }
            ]
        },
        {\
            "category"  : "content",\
            "parameters": [\
                {\
                    "resource"    : "/",\
                    "http-status" : "HTTP/1.1 200 OK\r\n",\
                    "body"        : "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",\
                    "headers"     : "Connection: close\r\nDate: Sat, 27 Aug 2016 18:51:19 GMT\r\nServer: Apache/2.4.10 (Unix)\r\n"\
                },\
                {\
                                        "resource"      : "/500",\
                                        "http-status"   : "HTTP/1.1 500 Internal Server Error\r\n",\
                                        "body"          : "Response for the 500 error",\
                                        "headers"       : "Connection: close\r\nDate: Sat, 27 Aug 2016 18:51:19 GMT\r\nServer: Apache/2.4.10 (Unix)\r\n"\
                                },\
                {\
                                        "resource"      : "/404",\
                                        "http-status"   : "HTTP/1.1 404 Resource Not Found\r\n",\
                                        "body"          : "Response for the 404 error",\
                                        "headers"       : "Connection: close\r\nDate: Sat, 27 Aug 2016 18:51:19 GMT\r\nServer: Apache/2.4.10 (Unix)\r\n"\
                                },\
                {\
                                        "resource"      : "/favicon.ico",\
                                        "http-status"   : "HTTP/1.1 200 OK\r\n",\
                                        "body"          : "<html><body><img src='data:image/png;base64,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' alt=''/></body></html>\r\n\r\n",\
                                        "headers"       : "Connection: close\r\nDate: Sat, 27 Aug 2016 18:51:19 GMT\r\nServer: Apache/2.4.10 (Unix)\r\n"\
                                }\
            ]\
        }\
    ]\
} 

if(len(sys.argv) > 1 and sys.argv[1] == "remote"):    
    
    cmd = ""
    #c = Connector(jconfig, debug=4)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind( (get_ip_address(jconfig['interface']), 6565) )
    s.listen(1)
    sc,caddr = s.accept()
    
    print "Connection accepted, ready for command"
    while (s):
        cmd = sc.recv(10)
        print "Received data: " + str(cmd)
        if cmd == "start\n":
            c = Connector(jconfig, debug=3)
            c.run()
        elif cmd == "stop\n":
            c.stop()
            print "\n\n\n======= 8< ======== Config file ======== 8< ==========\n"
            print json.dumps(jconfig, indent=2, sort_keys=False)
            print "\n========= 8< ======== END Config file ========== 8< ==========\n"
            s.close()
            exit()

elif (len(sys.argv) > 1 and sys.argv[1] != "remote"):
    with open(sys.argv[1]) as data_file:
        jconfig = json.load(data_file)

    c = Connector(jconfig, debug=3)
    c.run()
    print "\n\n\n======= 8< ======== Config file ======== 8< ==========\n"
    print json.dumps(jconfig, indent=2, sort_keys=False)
    print "\n========= 8< ======== END Config file ========== 8< ==========\n"

        

else:
    c = Connector(jconfig, debug=3)
    c.run()
    print "\n\n\n======= 8< ======== Config file ======== 8< ==========\n"
    print json.dumps(jconfig, indent=2, sort_keys=False)
    print "\n========= 8< ======== END Config file ========== 8< ==========\n"
