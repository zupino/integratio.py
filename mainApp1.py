#! /usr/bin/python

from scapy.all import *
from testerApp1 import *
from functools import wraps
import json
import glob # file fetching
import sys

# To be used when working on local interface l0
conf.L3socket = L3RawSocket
sys.path.append('.')

log_scapy = logging.getLogger("scapy")
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
log_scapy.addHandler(console_handler)
log_runtime = logging.getLogger("scapy.runtime")          # logs at runtime
log_runtime.addFilter(ScapyFreqFilter())
log_interactive = logging.getLogger("scapy.interactive")  # logs in interactive functions
log_loading = logging.getLogger("scapy.loading")          # logs when loading scapy

if __name__=='__main__':
    
    log_scapy.setLevel(1)
    log_interactive.setLevel(1)
    log_runtime.setLevel(1)
    log_loading.setLevel(1)

    processedJson={}
    plainJson={}
    # creating Test Server Factory 
       
    #create Configuration Expert
    configExpert = ConfigExpertApp1()
    
    # Poll the json files from the config folder
    for fileName in glob.glob('./configs/test.json'):
        with open(fileName) as dataFile:
            plainJson = json.load(dataFile)
        # call the configuration expert to normalize the- json dict
        processedJson = configExpert.process(plainJson)
        comp = TesterApp1(jsonDict=processedJson)
        comp.runComponent()
    