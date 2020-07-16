import re
import asyncio
from txtproc.abc import TextProcessor

#from mac_vendor_lookup import MacLookup
from .util.mac_vendor_lookup_sync import *



class MacConverter(TextProcessor):
    def __init__(self):
        self.mac = SyncMacLookup()



    @classmethod
    def can_process(cls, query: str):
        mac = query.replace(":", "").replace("-", "").replace(".","").upper()
        try:
            int(mac, 16)
        except ValueError:
            return False
        if len(mac) > 12 or len(mac) < 6:
            return False
        return True

    def process(self, query: str) -> str:
        if self.can_process(query):
            result = self.mac.lookup(query)
            return result
        return "Unknown"
