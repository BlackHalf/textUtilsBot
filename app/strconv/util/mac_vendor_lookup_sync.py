#import asyncio
import http.client
import os
import io
import logging
import sys
from datetime import datetime

import aiofiles
import aiohttp

#from urllib.parse import urlparse
import urllib.request

OUI_URL = "http://standards-oui.ieee.org/oui.txt"


class InvalidMacError(Exception):
    pass


class BaseMacLookup(object):
    cache_path = os.path.expanduser('~/.cache/mac-vendors.txt')

    @staticmethod
    def sanitise(_mac):
        mac = _mac.replace(":", "").replace("-", "").replace(".","").upper()
        try:
            int(mac, 16)
        except ValueError:
            raise InvalidMacError("{} contains unexpected character".format(_mac))
        if len(mac) > 12:
            raise InvalidMacError("{} is not a valid MAC address (too long)".format(_mac))
        return mac

    def get_last_updated(self):
        vendors_location = self.find_vendors_list()
        if vendors_location:
            return datetime.fromtimestamp(os.path.getmtime(vendors_location))

    def find_vendors_list(self):
        possible_locations = [
            BaseMacLookup.cache_path,
            sys.prefix + "/cache/mac-vendors.txt",
            os.path.dirname(__file__) + "/../../cache/mac-vendors.txt",
            os.path.dirname(__file__) + "/../../../cache/mac-vendors.txt",
        ]

        for location in possible_locations:
            if os.path.exists(location):
                return location


class SyncMacLookup(BaseMacLookup):
    def __init__(self):
        self.prefixes = None

    def update_vendors(self, url=OUI_URL):
        logging.log(logging.DEBUG, "Downloading MAC vendor list")
        with urllib.request.urlopen(url) as handle:
            #response = handle.read().decode('utf-8')
            #buf = io.StringIO(response)
            print(SyncMacLookup.cache_path)
            with open(SyncMacLookup.cache_path, mode='wb') as f:
                    self.prefixes = {}
                    while True:
                        line = handle.readline()
                        if not line:
                            break
                        if b"(base 16)" in line:
                            prefix, vendor = (i.strip() for i in line.split(b"(base 16)", 1))
                            self.prefixes[prefix] = vendor
                            f.write(prefix + b":" + vendor + b"\n")

    def load_vendors(self):
        self.prefixes = {}

        vendors_location = self.find_vendors_list()
        if vendors_location:
            logging.log(logging.DEBUG, "Loading vendor list from {}".format(vendors_location))
            print("Loading vendor list from {}".format(vendors_location))
            with open(vendors_location, mode='rb') as f:
                # Loading the entire file into memory, then splitting is
                # actually faster than streaming each line. (> 1000x)
                for l in (f.read()).splitlines():
                    prefix, vendor = l.split(b":", 1)
                    self.prefixes[prefix] = vendor
        else:
            try:
                os.makedirs("/".join(SyncMacLookup.cache_path.split("/")[:-1]))
            except OSError:
                pass
            self.update_vendors()
        logging.log(logging.DEBUG, "Vendor list successfully loaded: {} entries".format(len(self.prefixes)))

    def lookup(self, mac):
        mac = self.sanitise(mac)
        if not self.prefixes:
            self.load_vendors()
        if type(mac) == str:
            mac = mac.encode("utf8")
        try:
            result = self.prefixes[mac[:6]].decode("utf8")
            return result
        except KeyError:
            return "Prefix is not registered"


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: {} [MAC-Address]".format(sys.argv[0]))
        sys.exit()
    try:
        print(SyncMacLookup().lookup(sys.argv[1]))
    except KeyError:
        print("Prefix is not registered")
    except InvalidMacError as e:
        print("Invalid MAC address:", e)


if __name__ == "__main__":
    main()
