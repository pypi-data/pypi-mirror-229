#!/usr/bin/env python3
# encoding: utf-8
# -*- coding: utf-8 -*-
"""
GeoIP2Fast - Version: v1.0.2 - 04/Sep/2023

Author: Ricardo Abuchaim - ricardoabuchaim@gmail.com
        https://github.com/rabuchaim/geoip2fast/

License: MIT
"""
"""                                                                  
.oPYo.               o  .oPYo. .oPYo.  ooooo                 o  
8    8               8  8    8     `8  8                     8  
8      .oPYo. .oPYo. 8 o8YooP'    oP' o8oo   .oPYo. .oPYo.  o8P 
8   oo 8oooo8 8    8 8  8      .oP'    8     .oooo8 Yb..     8  
8    8 8.     8    8 8  8      8'      8     8    8   'Yb.   8  
`YooP8 `Yooo' `YooP' 8  8      8ooooo  8     `YooP8 `YooP'   8  
:....8 :.....::.....:..:..:::::.......:..:::::.....::.....:::..:
:::::8 :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::..:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""
"""
What's new in v1.0.2 - 04/Sep/2023
- geoip2fast.dat.gz updated with MAXMIND:GeoLite2-Country-CSV_20230901
- fully tested with Python 3.11.5. Much faster than 3.10.12 >100K lookups/sec.
- fix encoding of pp_json() method. Now it's showing all chars as it is.
- in verbose mode it is now showing the memory footprint.
- new test files at /usr/local/lib/python3.10/dist-packages/geoip2fast/tests/
- new class CIDRDetail will be used to create gepip2fast.dat file
- geoip2dat - a script to import Maxmind-Country-CSV into geoip2fast.dat.gz.
  You can update your geoip2fast.dat.gz file whenever you want. It should work 
  with paid version also. Please let me know if there are any problems.
- put some flowers;

What's new in v1.0.1 - 1º/Sep/2023
- geoip2fast.dat.gz updated with MAXMIND:GeoLite2-Country-CSV_20230901
- improved speed in >20%! removed ipaddress module. Now we do some IP calcs.
- new methods to set the error code for the situations PRIVATE NETWORKS and for 
  NETWORKS NOT FOUND:
    GeoIP2Fast.set_error_code_private_networks(new_value) 
    GeoIP2Fast.set_error_code_network_not_found(new_value)
- new method to calculate the current speed. Returns a value of current lookups per 
  seconds or print a formatted result:
    GeoIP2Fast.calculate_speed(print_result=True)
- new method to calculate how many IPv4 of all internet are covered by geoip2fast.dat 
  file. Returns a percentage relative to all possible IPv4 on the internet or print a 
  formatted result. Useful to track the changes in getip2fast.dat.gz file:
    GeoIP2Fast.calculate_coverage(print_result=True)
"""

__version__ = "1.0.2"

import sys, os, json, gzip, pickle
from struct import unpack
from random import randrange
from time import perf_counter
from functools import lru_cache
from bisect import bisect as geoipBisect
from socket import inet_aton, setdefaulttimeout, gethostbyaddr

GEOIP2FAST_DAT_GZ_FILE = os.path.join(os.path.dirname(__file__),"geoip2fast.dat.gz")

##──── Define here what do you want to return as 'country_code' if one of these errors occurs ────────────────────────────────────
GEOIP_ECCODE_PRIVATE_NETWORKS      = "--"
GEOIP_ECCODE_NETWORK_NOT_FOUND     = "--"
GEOIP_ECCODE_INVALID_IP            = ""
GEOIP_ECCODE_LOOKUP_INTERNAL_ERROR = ""
##──── ECCODE = Error Country Code ───────────────────────────────────────────────────────────────────────────────────────────────

DEFAULT_LRU_CACHE_SIZE = 1000

sys.tracebacklimit = 0

##──── To enable DEBUG flag just export an environment variable GEOIP2FAST_DEBUG with any value ──────────────────────────────────
##──── Ex: export GEOIP2FAST_DEBUG=1 ─────────────────────────────────────────────────────────────────────────────────────────────
_DEBUG = bool(os.environ.get("GEOIP2FAST_DEBUG",False))

os.environ["PYTHONWARNINGS"]    = "ignore"
os.environ["PYTHONIOENCODING"]  = "UTF-8"        

reservedNetworks = {
    "0.0.0.0/8":         {"01":"Reserved for self identification"},
    "10.0.0.0/8":        {"02":"Private Network Class A"},
    "100.64.0.0/10":     {"03":"Reserved for Shared Address Space"},
    "127.0.0.0/8":       {"04":"Localhost"},
    "169.254.0.0/16":    {"05":"APIPA Automatic Priv.IP Addressing"},
    "172.16.0.0/12":     {"06":"Private Network Class B"},
    "192.0.0.0/29":      {"07":"Reserved IANA"},
    "192.0.2.0/24":      {"08":"Reserved for TEST-NET"},
    "192.88.99.0/24":    {"09":"Reserved for 6to4 Relay Anycast"},
    "192.168.0.0/16":    {"10":"Private Network Class C"},
    "198.18.0.0/15":     {"11":"Reserved for Network Benchmark"},
    "224.0.0.0/4":       {"12":"Reserved Multicast Networks"},
    "240.0.0.0/4":       {"13":"Reserved for future use"},
    "255.255.255.255/32":{"14":"Reserved for broadcast"}
    }

def print_elapsed_time(method):
    def decorated_method(self, *args, **kwargs):
        startTime = perf_counter()
        result = method(self, *args, **kwargs)  
        print(str(method)+" [%.9f sec]"%(perf_counter()-startTime))
        return result
    return decorated_method

##──── Function to check the memory use ────────────────────────────────────────────────────────────────────────────────────────
def get_mem_usage()->float:
    ''' Memory usage in MiB '''
    with open('/proc/self/status') as f:
        memusage = f.read().split('VmRSS:')[1].split('\n')[0][:-3]
    return float(memusage.strip()) / 1024
    
    
class GeoIPError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

@lru_cache(maxsize=DEFAULT_LRU_CACHE_SIZE)
class CIDRDetail(object):
    """An object to calculate some information about a CIDR, with some properties
       calculated on demand. This is necessary just because we need the first and last
       IP of a network converted to integer and the number of hosts used in coverage test.
       
       There are a lot of ways to get this information using ipaddress, netaddr, etc, but this
       is the fastest method tested.
    """   
    def __init__(self,CIDR):  # CIDR like 1.2.3.0/24, 10.0.0.0/8
        addr, nlen = CIDR.split('/')
        self.cidr = CIDR
        self.nlen = int(nlen)   # network length
        self.addr = [int(oct) for oct in addr.split(".")]
        self.mask = [( ((1<<32)-1) << (32-self.nlen) >> i ) & 255 for i in reversed(range(0, 32, 8))]
        self.netw = [self.addr[i] & self.mask[i] for i in range(4)]
        self.bcas = [(self.addr[i] & self.mask[i]) | (255^self.mask[i]) for i in range(4)]
    @property
    def first_ip(self)->str:
        return str(self.netw[0])+"."+str(self.netw[1])+"."+str(self.netw[2])+"."+str(self.netw[3])
    @property
    def last_ip(self)->str:
        return str(self.bcas[0])+"."+str(self.bcas[1])+"."+str(self.bcas[2])+"."+str(self.bcas[3])
    @property
    def first_ip2int(self)->int:
        return unpack(">L", inet_aton(str(self.netw[0])+"."+str(self.netw[1])+"."+str(self.netw[2])+"."+str(self.netw[3])))[0]
    @property
    def last_ip2int(self)->int:
        return unpack(">L", inet_aton(str(self.bcas[0])+"."+str(self.bcas[1])+"."+str(self.bcas[2])+"."+str(self.bcas[3])))[0]
    @property
    def num_hosts(self)->int:
        return (self.last_ip2int - self.first_ip2int) + 1

class GeoIPDetail(object):
    """Object to store the information obtained by searching an IP address
    """    
    def __init__(self, ip, country_code="", country_name="", cidr="", is_private=False, elapsed_time=""):
        self.ip = ip
        self.country_code = country_code
        self.country_name = country_name
        self.cidr = cidr
        self.hostname = ""
        self.is_private = is_private
        self.elapsed_time = elapsed_time
    def __str__(self):
        return f"{self.__dict__}"
    def __repr__(self):
        return f"{self.to_dict()}"
    def get_hostname(self,dns_timeout=0.1):
        """Call this function to set the property 'hostname' with a socket.gethostbyaddr(ipadr) dns lookup.

        Args:
            dns_timeout (float, optional): Defaults to 0.1.

        Returns:
            str: the hostname if success or an error message between < >
        """
        try:
            setdefaulttimeout(dns_timeout)
            result = gethostbyaddr(self.ip)[0]
            self.hostname = result if result != self.ip else ""
            return self.hostname
        except OSError as ERR:
            self.hostname = f"<{str(ERR.strerror)}>"
            return self.hostname
        except Exception as ERR:
            self.hostname = "<dns resolver error>"
            return self.hostname        
    def to_dict(self):
        """To use the result as a dict

        Returns:
            dict: a dictionary with result's properties 
        """
        try:
            d = {
                "ip": self.ip,
                "country_code": self.country_code,
                "country_name": self.country_name,
                "cidr": self.cidr,
                "hostname":self.hostname,
                "is_private": self.is_private,
                "elapsed_time": self.elapsed_time
                }
            return d
        except Exception as ERR:
            raise GeoIPError("Failed to_dict() %a"%(str(ERR)))
    def pp_json(self,indent=3,sort_keys=False,print_result=False):
        """ A pretty print for json

        If *indent* is a non-negative integer, then JSON array elements and object members will be pretty-printed with that indent level. An indent level of 0 will only insert newlines. None is the most compact representation.

        If *sort_keys* is true (default: False), then the output of dictionaries will be sorted by key.

        If *print_result* is True (default: False), then the output of dictionaries will be printed to stdout, otherwise a one-line string will be silently returned.

        Returns:
            string: returns a string to print.            
        """
        try:
            dump = json.dumps(self.to_dict(),sort_keys=sort_keys,indent=indent,ensure_ascii=False)
            if print_result == True:
                print(dump)
            return dump
        except Exception as ERR:
            raise GeoIPError("Failed pp_json() %a"%(str(ERR)))

class GeoIP2Fast(object):    
    """
    Creates the object that will load data from the database file and make the requested queries.

    - Usage:
        from geoip2fast import GeoIP2Fast
        
        myGeoIP = GeoIP2Fast(verbose=False,geoip2fast_data_file="")
        
        result = myGeoIP.lookup("8.8.8.8")
        
        print(result.country_code)
        
    - *geoip2fast_data_file* is used to specify a different path of file geoip2fast.dat.gz. If empty, the default paths will be used.
    
    - Returns *GEOIP_ECCODE_INVALID_IP* as country_code if the given IP is invalid

    - Returns *GEOIP_ECCODE_PRIVATE_NETWORKS* as country_code if the given IP belongs to a special/private/iana_reserved network
    
    - Returns *GEOIP_ECCODE_NETWORK_NOT_FOUND* as country_code if the network of the given IP wasn't found.

    - Returns *GEOIP_ECCODE_LOOKUP_INTERNAL_ERROR* as country_code if something eal bad occurs during the lookup function. Try again with verbose=True

    - To use the result as a dict: 
    
        result.to_dict()['country_code']
    """    
    def __init__(self, verbose=False, geoip2fast_data_file=""):
        global elapsedTimeToLocateDatabase, startMem  # declared as global to be used at function _load_data()
        startMem = get_mem_usage()
        self.verbose = verbose       
        self._load_data_text = "" 
        ##──── Swap functions code at __init__ to avoid "if verbose=True" and save time ──────────────────────────────────────────────────
        if _DEBUG == False:
            self._print_debug = self.__print_verbose_empty
        if verbose == False:
            self._print_verbose = self.__print_verbose_empty
        ##──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────        
        self.error_code_private_networks        = GEOIP_ECCODE_PRIVATE_NETWORKS
        self.error_code_network_not_found       = GEOIP_ECCODE_NETWORK_NOT_FOUND
        self.error_code_invalid_ip              = GEOIP_ECCODE_INVALID_IP
        self.error_code_lookup_internal_error   = GEOIP_ECCODE_LOOKUP_INTERNAL_ERROR
        
        ##──── Try to locate the database file in the directory of the application that called GeoIP2Fast() ─────────────────────────
        ##──── or in the directory of the GeoIP2Fast Library ────────────────────────────────────────────────────────────────────────
        try:
            start_time = perf_counter()
            if geoip2fast_data_file != "":
                self.data_file = geoip2fast_data_file
            else:
                self.data_file = GEOIP2FAST_DAT_GZ_FILE
                try:
                    databasePath = self._locate_database_file(os.path.basename(self.data_file))
                    if databasePath is False:
                        raise GeoIPError("Unable to find GeoIP2Fast database file %s"%(os.path.basename(self.data_file)))
                    else:
                        self.data_file = databasePath
                except Exception as ERR:
                    raise GeoIPError("Unable to find GeoIP2Fast database file %s"%(os.path.basename(self.data_file)))            
            # THE ELAPSED TIME TO LOCATE THE FILE WILL BE ADDED TO ELAPSED TIME TO OPEN AND LOAD THE FILE
            elapsedTimeToLocateDatabase = perf_counter()-start_time  
        except Exception as ERR:
            raise GeoIPError("Failed at locate data file %s"%(str(ERR)))
        ##──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        self.is_loaded = False
        self._load_data(self.data_file, verbose)
 
    ##──── Function used to avoid "if verbose == True". The code is swaped at __init__ ───────────────────────────────────────────────
    def __print_verbose_empty(self,msg):return
    def _print_debug(self,msg):
        print("[DEBUG] "+msg,flush=True)
    def _print_verbose(self,msg):
        print(msg,flush=True)
    ##──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    def _locate_database_file(self,filename):
        try:
            curDir = os.path.join(os.path.abspath(os.path.curdir),filename) # path of your application
            libDir = os.path.join(os.path.dirname(__file__),filename)       # path where the library is installed
        except Exception as ERR:
            raise GeoIPError("Unable to determine the path of application %s. %s"%(filename,str(ERR)))
        try:
            os.stat(curDir).st_mode
            return curDir
        except Exception as ERR:            
            try:
                os.stat(libDir).st_mode 
                return libDir
            except Exception as ERR:
                raise GeoIPError("Unable to determine the path of library %s - %s"%(filename,str(ERR)))
    
    def _load_data(self, gzip_data_file:str, verbose=False)->bool:
        global geoipSourceInfo, geoipListFirstIP, geoipLocationDict, geoipCIDRCountryCode
        startLoadData = perf_counter()
        if self.is_loaded == True:
            return True   

        try:
            try:
                inputFile = open(str(gzip_data_file).replace(".gz",""),'rb')
                self.data_file = self.data_file.replace(".gz","")
            except:
                try:
                    inputFile = gzip.open(str(gzip_data_file),'rb')
                except Exception as ERR:
                    raise GeoIPError(f"Unable to find {gzip_data_file} or {gzip_data_file} {str(ERR)}\n")
        except Exception as RR:
            raise GeoIPError(f"Failed to 'load' GeoIP2Fast! the data file {gzip_data_file} appears to be invalid or does not exist! {str(ERR)}\n")

        try:
            geoipListLocation, geoipCIDRCountryCode, geoipListFirstIP, geoipSourceInfo = pickle.load(inputFile)
                ##──── Structure model of GeoIP2Fast dat file ────────────────────────────────────────────────────────────────────────────────────                
                # database = [listLocation,       # list      "country_code:country_name"
                #             listCIDRCountryCode,# list      "cidr:country_code"
                #             listFirstIP,        # list of integers
                #             _SOURCE_INFO        # string
                #             ]
            geoipLocationDict = {item.split(":")[0]:item.split(":")[1] for item in geoipListLocation}
            del geoipListLocation
            inputFile.close()
            del inputFile
        except Exception as ERR:
            raise GeoIPError(f"Failed to pickle the data file {gzip_data_file} {str(ERR)}\n")

        try:    
            [self.lookup(ip) for ip in ['0.0.0.0','255.255.255.255']]   # warming-up
        except Exception as ERR:
            raise GeoIPError("Failed at warming-up... exiting... %s"%(str(ERR)))

        try:
            totalLoadTime = elapsedTimeToLocateDatabase + (perf_counter() - startLoadData)
            totalMemUsage = (get_mem_usage()-startMem)
            self._load_data_text = f"GeoIP2Fast v{__version__} is ready! {os.path.basename(gzip_data_file)} loaded with %s networks in %.5f seconds and using %.2f MiB."%(str(len(geoipListFirstIP)),totalLoadTime,totalMemUsage)
            self._print_verbose(self._load_data_text)
        except Exception as ERR:
            raise GeoIPError("Failed at the end of load data %s"%(str(ERR)))

        self.is_loaded = True
        return True

    @property
    def startup_line_text(self):
        ##──── Returns the text of _load_data() in case you want to know without set verbose=True ───────────────────────────────────────────
        ##──── Like: GeoIP2Fast v1.X.X is ready! geoip2fast.dat.gz loaded with XXXXXX networks in 0.0000 seconds and using YY.ZZ MiB. ───────
        return self._load_data_text

    @lru_cache(maxsize=DEFAULT_LRU_CACHE_SIZE, typed=True)
    def _bisect_lookup(self,iplong):
        try:
            return geoipBisect(geoipListFirstIP,iplong)-1
        except:
            return 0

    @lru_cache(maxsize=DEFAULT_LRU_CACHE_SIZE, typed=True)
    def _cidr_lookup(self,iplong):
        try:
            result = geoipCIDRCountryCode[iplong]
            return tuple(result.split(":"))
        except:
            return ("","")
    
    @lru_cache(maxsize=300, typed=True)
    def _locations_lookup(self,country_code):
        try:
            return geoipLocationDict[country_code]
        except:
            # this means that a country_code could not be located. maybe the country list location was modified.
            return "<unknown location>"
    
    @lru_cache(maxsize=DEFAULT_LRU_CACHE_SIZE, typed=True)
    def _ip2int(self,ipaddr:str)->int:
        """
        Convert an IP Address into an integer number
        """    
        try:
            return unpack(">L", inet_aton(ipaddr))[0]
        except Exception as ERR:
            raise GeoIPError("Failed to convert the IP address (%s) to integer. %s"%(ipaddr,str(ERR)))
    
    ##──── Decorator to set the property elapsed_time in class CIDRDetail ────────────────────────────────────────────────────────────
    @lru_cache(maxsize=DEFAULT_LRU_CACHE_SIZE)
    def _get_last_ip2int(self,CIDR):
        """Returns the last IP of a network with an integer representation. 
        To get a better speed for lookups, this function was separated from class CIDRDetails.

        Args:
            CIDR (str): A network range in CIDR representation

        Returns:
            int: the last IP of a network converted into integer
        """
        try:
            (addr, nlen) = CIDR.split('/')
            addr = [int(x) for x in addr.split(".")]
            mask = [( ((1<<32)-1) << (32-int(nlen)) >> i ) & 255 for i in reversed(range(0, 32, 8))]
            bcas = [(addr[i] & mask[i]) | (255^mask[i]) for i in range(4)]
            last_ip = str(bcas[0])+"."+str(bcas[1])+"."+str(bcas[2])+"."+str(bcas[3])
            return unpack(">L", inet_aton(last_ip))[0]
        except Exception as ERR:
            self._print_verbose(str(ERR))
            return 0
    
    def set_error_code_private_networks(self,new_value)->str:
        """Change the GEOIP_ECCODE_PRIVATE_NETWORKS. This value will be returned in country_code property.

        Returns:
            str: returns the new value setted
        """
        try:
            self.error_code_private_networks = new_value
            return new_value
        except Exception as ERR:
            raise GeoIPError("Unable to set a new value for GEOIP_ECCODE_PRIVATE_NETWORKS: %s "%(str(ERR)))
        
    def set_error_code_network_not_found(self,new_value)->str:
        """Change the GEOIP_ECCODE_NETWORK_NOT_FOUND. This value will be returned in country_code property.

        Returns:
            str: returns the new value setted
        """
        try:
            self.error_code_network_not_found = new_value
            return new_value
        except Exception as ERR:
            raise GeoIPError("Unable to set a new value for GEOIP_ECCODE_NETWORK_NOT_FOUND: %s "%(str(ERR)))
        
    ##──── NO-CACHE: This function cannot be cached to don´t cache the elapsed timer. ────────────────────────────────────────────────────────────
    def lookup(self,ipaddr:str)->GeoIPDetail:
        """
        Performs a search for the given IP address in the in-memory database

        - Returns *GEOIP_ECCODE_INVALID_IP* as country_code if the given IP is invalid

        - Returns *GEOIP_ECCODE_PRIVATE_NETWORKS* as country_code if the given IP belongs to a special/private/iana_reserved network
            
        - Returns *GEOIP_ECCODE_NETWORK_NOT_FOUND* as country_code if the network of the given IP wasn't found.

        - Returns *GEOIP_ECCODE_LOOKUP_INTERNAL_ERROR* as country_code if something eal bad occurs during the lookup function. Try again with verbose=True

        - Returns an object called GeoIPDetail withm its properties: ip, country_code, country_name, cidr, hostname, is_private and elapsed_time
            
        - Usage:

            from geoip2fast import GeoIP2Fast
    
            myGeoIP = GeoIP2Fast()
            
            result = myGeoIP.lookup("8.8.8.8")
            
            print(result.country_code)

        """                    
        startTime = perf_counter()
        try:
            iplong = self._ip2int(ipaddr)
        except Exception as ERR:
            return GeoIPDetail(ipaddr,country_code=self.error_code_invalid_ip,country_name="<invalid ip address>",elapsed_time='%.9f sec'%(perf_counter()-startTime))
        try:            
            match = self._bisect_lookup(iplong=iplong)
            cidr,country_code = self._cidr_lookup(match)
            ##──── IF YOU COMMENT THESE 2 LINES BELOW, YOU WILL GET 2x SPEED, BUT... YOUR SEARCH ACCURACY GOES DOWN TO ~99,5% ────────────────
            ##──── You can comment these 2 lines and execute the file ./tests/accuracy_check.py to see how many wrong locations could ────────
            ##──── be given in 1000000 lookups and check the difference of speed. Just for testing. ──────────────────────────────────────────
            if iplong > self._get_last_ip2int(cidr):
                return GeoIPDetail(ip=ipaddr,country_code=self.error_code_network_not_found,country_name="<network not found in database>",elapsed_time='%.9f sec'%(perf_counter()-startTime))
            ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
            country_name = self._locations_lookup(country_code)
            try:
                # On all reserved networks, we put a number as a "isocode". If is possible to convert to integer, the IP belongs to
                # a private/reserved network and does not have a country_code, so change the country_code to '--' (self.error_code_private_networks). 
                int(country_code)                                   
                country_code = self.error_code_private_networks 
                is_private = True
            except:
                is_private = False
            ##──── SUCCESS! ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
            return GeoIPDetail(ipaddr,country_code,country_name,cidr,is_private,elapsed_time='%.9f sec'%(perf_counter()-startTime))
            ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        except Exception as ERR:
            return GeoIPDetail(ip=ipaddr,country_code=self.error_code_lookup_internal_error,country_name="<internal lookup error>",hostname=str(ERR),elapsed_time='%.9f sec'%(perf_counter()-startTime))
    
    def clear_cache(self)->bool:
        """ 
        Clear the internal cache of lookup function
        
        Return: True or False
        """
        try:
            self._bisect_lookup.cache_clear()
            self._cidr_lookup.cache_clear()
            self._get_last_ip2int.cache_clear()
            self._locations_lookup.cache_clear()
            return True
        except Exception as ERR:
            return False
        
    def cache_info(self)->str:
        """ 
        Returns information about the internal cache of lookup function
        
        Usage: print(GeoIP2Fast.cache_info())
        
        Exemple output: CacheInfo(hits=18, misses=29, maxsize=10000, currsize=29)
        """
        try:
            return self._bisect_lookup.cache_info()
        except Exception as ERR:
            return False
    
    def get_source_info(self):
        """
        Returns the information of the data source of geoip data.
        """
        return geoipSourceInfo
            
    def _get_cidr_list(self):
        """
        Returns a list of all network ranges inside the .dat file. Used to check the total IP coverage.
        """
        return [item.split(":")[0] for item in geoipCIDRCountryCode]
                
    def calculate_coverage(self,print_result=False,verbose=False)->float:
        """
            Calculate how many IP addresses are in all networks covered by geoip2fast.dat and compare with all 4.294.967.296 
            possible IPv4 addresses on the internet. 
        
            This include all reserved/private networks also. If remove them, need to remove them from the total 4.2bi and 
            the percetage will be the same.
            
            Run this function with "verbose=True" to see all networks included in geoip2fast.dat.gz file.
        
        Method: Get a list of all CIDR from geoip2fast.dat.gz using the function self._get_cidr_list(). For each CIDR, 
                calculates the number of hosts using the function self._get_num_hosts(CIDR) and sum all of returned values.
                Finally, the proportion is calculated in relation to the maximum possible number of IPv4 (4294967296).
                GeoIP2Fast will return a response for XX.XX% of all IPv4 on the internet.
        
        Returns:
            float: Returns a percentage compared with all possible IPs.
        """
        try:
            startTime = perf_counter()
            cidrList = self._get_cidr_list()
            ipCounter = 0
            for CIDR in cidrList:
                startTimeCIDR = perf_counter()
                CIDRInfo = CIDRDetail(CIDR)
                ipCounter += CIDRInfo.num_hosts
                if verbose and print_result == True:
                    geoip = self.lookup(CIDRInfo.first_ip)
                    print(f"- Network: {CIDR.ljust(19)} IPs: {str(CIDRInfo.num_hosts).ljust(10)} {geoip.country_code} {geoip.country_name.ljust(30)} {'%.9f sec'%(perf_counter()-startTimeCIDR)}")
            ipCounter -= 1 # removing the last IP (255.255.255.255) that is already included in 240.0.0.0/4
            percentage = (ipCounter * 100) / 4294967296
            if print_result == True:
                print("\nCurrent IPv4 coverage: %.2f%% (%d IPs in %s networks) [%.5f sec]"%(percentage,ipCounter,len(cidrList),(perf_counter()-startTime)))
            return percentage
        except Exception as ERR:
            raise GeoIPError("Failed to calculate total IP coverage. %s"%(str(ERR)))
        
    def calculate_speed(self,print_result=False)->int:
        """Calculate how many lookups per second is possible.

        Method: generates a list of 1.000.000 of randomic IP addresses and do a GeoIP2Fast.lookup() on all IPs on this list. 
                It tooks a few seconds, less than a minute.

        Note: This function clear all cache before start the tests. And inside the loop generates a random IP address in runtime 
              and use the returned value to try to get closer a real situation of use. Could be 3 times faster if you prepare 
              a list of IPs before starts the loop and do a simple lookup(IP).
        
        Returns:
            float: Returns a value of lookups per seconds.
        """
        try:
            MAX_IPS = 1000000  # ONE MILLION
            self.clear_cache()   
            startTime = perf_counter()
            # COULD BE 3X FASTER IF YOU GENERATE A LIST WITH 1.000.000 IPs BEFORE LOOKUP.
            # BUT LET´S KEEP LIKE THIS TO SPEND SOME MILLISECONDS TO GET CLOSER A REAL SITUATION OF USE
            for NUM in range(MAX_IPS):
                IP = f"{randrange(0,254)}.{randrange(0,254)}.{randrange(0,254)}.{randrange(0,254)}"
                ipinfo = self.lookup(IP)
                XXXX = ipinfo.country_code # SIMULATE THE USE OF THE RETURNED VALUE
            total_time_spent = perf_counter() - startTime
            current_lookups_per_second = MAX_IPS / total_time_spent
            if print_result == True:
                print("Current speed: %.2f lookups per second (searched for %s IPs in %.9f seconds) [%.5f sec]"%(current_lookups_per_second,MAX_IPS,total_time_spent,perf_counter()-startTime))
            return current_lookups_per_second
        except Exception as ERR:
            raise GeoIPError("Failed to calculate current speed. %s"%(str(ERR)))
        
##──── A SIMPLE AND FAST CLI ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ncmd = len(sys.argv)
    resolve_hostname = False
    if '-d' in sys.argv: 
        resolve_hostname = True
        sys.argv.pop(sys.argv.index('-d'))
        ncmd -= 1
    if len(sys.argv) > 1 and sys.argv[1] is not None:
        a_list = sys.argv[1].replace(" ","").split(",")
        if len(a_list) > 0:
            geoip = GeoIP2Fast()
            for IP in a_list:
                result = geoip.lookup(IP)
                if resolve_hostname == True: result.get_hostname()
                result.pp_json(print_result=True)
    else:
        print(f"GeoIP2Fast v{__version__} Usage: {os.path.basename(__file__)} [-d] <ip_address_1>,<ip_address_2>,<ip_address_N>,...")