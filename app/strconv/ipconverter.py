import re
import asyncio
import logging 
from txtproc.abc import TextProcessor

#from mac_vendor_lookup import MacLookup
#from .util.mac_vendor_lookup_sync import *


import ipaddress



class IpConverter(TextProcessor):
    def __init__(self):
        pass
        #self.ip_addr = SyncMacLookup()

    def is_ipv4(string):
        try:
            ipaddress.ip_interface(string)
            return True
        except ValueError:
            return False


    @classmethod
    def can_process(cls, query: str):
        logging.debug("Check: "+query)
        if cls.is_ipv4(query):
            logging.debug("Pass:"+query)
            return True
        return False

    def process(self, query: str) -> str:
        if self.can_process(query):
            ipi = ipaddress.ip_interface(query)
            result = "Address {} Mask {} Cidr {} Network {} Broadcast {}".format(ipi.ip, ipi.netmask, str(ipi.network).split('/')[1],str(ipi.network).split('/')[0],ipi.network.broadcast_address )
            return result
        return "Unknown"
