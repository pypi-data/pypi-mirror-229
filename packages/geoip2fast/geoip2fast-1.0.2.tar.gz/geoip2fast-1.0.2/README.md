# GeoIP2Fast

GeoIP2Fast is the fastest GeoIP2 country lookup library. A search takes less than 0.00003 seconds. It has its own data file updated with Maxmind-Geolite2-CSV and is Pure Python!

**Even better with Python 3.11.5 >>> A simple search faster than 0.00002 second and over 100,000 lookups per second!**

With it´s own datafile (geoip2fast.dat.gz - 2.4Mb), can be loaded into memory in ~0.10 seconds and has a footprint of ~50mb of RAM for all data, so you don´t need to make requests to any webservices or connect to an external database.

GeoIP2Fast returns COUNTRY ISO CODE, COUNTRY NAME and CIDR. There is no external dependencies, you just need the ```geoip2fast.py``` file and the data file ```geoip2fast.dat.gz``` *(updated 01/Sep/2023)*.

```
What's new in v1.0.2 - 04/Sep/2023
- geoip2fast.dat.gz updated with MAXMIND:GeoLite2-Country-CSV_20230901
- fully tested with Python 3.11.5. Much faster than 3.10.12 >100K lookups/sec.
- fix encoding of pp_json() method. Now it's showing all chars as it is.
- in verbose mode it is now showing the memory footprint.
- new test files at /usr/local/lib/python3.10/dist-packages/geoip2fast/tests/
- new class CIDRDetail will be used to create geoip2fast.dat.gz file
- geoip2dat - a script to import Maxmind-Country-CSV into geoip2fast.dat.gz.
  You can update your geoip2fast.dat.gz file whenever you want. It should work 
  with paid version also. Please let me know if there are any problems.
- put some flowers;
```
## Installation
```bash
pip install geoip2fast
```
Or cloning from Github
```
git clone https://github.com/rabuchaim/geoip2fast.git
```
## How does it work?

GeoIP2Fast has a datafile **geoip2fast.dat.gz** (2.4Mb). This file is located into the library directory (usually ```/usr/local/lib/python3/dist-packages/geoip2fast```), but you can place this file into the same directory of your application. The library automatically checks both paths, And the directory of your application overlaps the directory of the library. You can use an specific location also. 

The ```bisect()``` function is used together with some ordered lists of integers to search the Network/CountryCode (Yes! an IP address has an integer representation, try to ping this number: ```ping 134744072``` or this ```ping 2130706433``` ).

If GeoIP2Fast does not have a network IP address that was requested, a "not found in database" error will be returned. Unlike many other libraries that when not finding a requested network, gives you the geographical location of the network immediately below. The result is not always correct. 

There are network gaps in the files we use as a source of data, and these missing networks are probably addresses that those responsible have not yet declared their location. It must be remembered that the geographical accuracy is the responsibility of the network block owners. If the owner (aka ASN) of the XXX.YYY.ZZZ.D/24 network range declares that his network range is located at "Foo Island", we must believe that an IP address of that network is there.

> *Don't go to Foo Island visit a girl you met on the internet just because you looked up her IP on GeoIP2Fast and the result indicated that she is there.*


## Quick Start

Once the object is created, GeoIP2Fast loads automatically all needed data into memory. The lookup function returns an object called ```GeoIPDetail```. And you can get the values of it's properties just calling the name of proprerty: ```result.ip, result.country_code, result.country_name, result.cidr, result.is_private and result.elapsed_time```. Or use the function ```to_dict()``` to get the result as a dict. You can get values like ```result.to_dict()['country_code']```


```python
from geoip2fast import GeoIP2Fast

GEOIP = GeoIP2Fast()
result = GEOIP.lookup("200.204.0.10")
print(result)

# to use the country_code property
print(result.country_code)

# Before call the function get_hostname(), the property hostname will always be empty.
print("Hostname: "+result.hostname)
result.get_hostname()
print("Hostname: "+result.hostname)

# to work with output as a dict, use the function to_dict()
print(result.to_dict()['country_code'],result.to_dict()['country_name'])

# to check the date of the CSV files used to create the .dat file
print(GEOIP.get_source_info())

# info about internal cache
print(GEOIP.cache_info())

# clear the internal cache
print(GEOIP.clear_cache())

# to see the difference after clear cache
print(GEOIP.cache_info())
```
There is a method to pretty print the result as json.dumps():
```python
>>> result = MyGeoIP.lookup("100.200.100.200")
>>> print(result.pp_json())
{
   "ip": "100.200.100.200",
   "country_code": "US",
   "country_name": "United States",
   "cidr": "100.128.0.0/9",
   "hostname": "",
   "is_private": false,
   "elapsed_time": "0.000023784 sec"
}
```
or simply: ```result.pp_json(print_result=True)```

To see the start-up line without set ```verbose=True``` :
```python
>>> from geoip2fast import GeoIP2Fast
>>> MyGeoIP = GeoIP2Fast()
>>> MyGeoIP.startup_line_text
'GeoIP2Fast v1.0.2 is ready! geoip2fast.dat.gz loaded with 434459 networks in 0.07092 seconds and using 53.74 MiB.'
```

Private/Reserved networks were included in the database just to be able to provide an answer if one of these IPs is searched. When it happens, the country_code will return "--", the "network name" will be displayed in the country_name and the range of that network will be displayed in the cidr property, and the property **is_private** is setted to **True**.

```python
>>> from geoip2fast import GeoIP2Fast
>>> geoip = GeoIP2Fast(verbose=True)
GeoIP2Fast is ready! Database file geoip2fast.dat.gz was loaded with 447841 records in 0.07677 seconds
>>>
>>> geoip.lookup("10.20.30.40")
{'ip': '10.20.30.40', 'country_code': '--', 'country_name': 'Private Network Class A', 'cidr': '10.0.0.0/8', 'hostname': '', 'is_private': True, 'elapsed_time': '0.000118687 sec'}
>>>
>>> geoip.lookup("169.254.10.20")
{'ip': '169.254.10.20', 'country_code': '--', 'country_name': 'APIPA - Automatic Private IP Addressing', 'cidr': '169.254.0.0/16', 'hostname': '', 'is_private': True, 'elapsed_time': '0.000123734 sec'}
```

You can change the behavior of what will be returned in country_code property of "private networks" and for "networks not found":

```python
>>> from geoip2fast import GeoIP2Fast
>>> MyGeoIP = GeoIP2Fast(verbose=True)
GeoIP2Fast is ready! geoip2fast.dat.gz loaded with 434459 networks in 0.08026 seconds and using 10.39 MiB.
>>>
>>> MyGeoIP.set_error_code_private_networks("@@")
'@@'
>>> MyGeoIP.lookup("10.20.30.40")
{'ip': '10.20.30.40', 'country_code': '@@', 'country_name': 'Private Network Class A', 'cidr': '10.0.0.0/8', 'hostname': '', 'is_private': True, 'elapsed_time': '0.000081486 sec'}
>>>
>>> MyGeoIP.set_error_code_network_not_found("##")
'##'
>>> MyGeoIP.lookup("57.242.128.144")
{'ip': '57.242.128.144', 'country_code': '##', 'country_name': '<network not found in database>', 'cidr': '', 'hostname': '', 'is_private': False, 'elapsed_time': '0.000071401 sec'}
>>>
```
You can use it as a CLI also:

```bash
# geoip2fast
GeoIP2Fast v1.0.2 Usage: geoip2fast [-d] <ip_address_1>,<ip_address_2>,<ip_address_N>,...
# geoip2fast 2.3.4.5
{
   "ip": "2.3.4.5",
   "country_code": "FR",
   "country_name": "France",
   "cidr": "2.0.0.0/12",
   "hostname": "",
   "is_private": false,
   "elapsed_time": "0.000016853 sec"
}
# geoip2fast -d 9.9.9.9             # '-d' get the hostname
{
   "ip": "9.9.9.9",
   "country_code": "US",
   "country_name": "United States",
   "cidr": "9.9.9.9/32",
   "hostname": "dns9.quad9.net",
   "is_private": false,
   "elapsed_time": "0.000020427 sec"
}
# geoip2fast "2.3.4.5, 4.5.6.7, 8.9.10.11" | jq -r '.country_code'
FR
US
US
```

## How fast is it?

With an virtual machine with 1 CPU and 4Gb of RAM, we have lookups **lower than 0,00003 seconds**. And if the lookup still in library´s internal cache, the elapsed time goes down to 0,000003 seconds. **GeoIP2Fast can do more than 60K queries per second, per core**. It takes less than 0,10 seconds to load the datafile into memory and get ready to lookup. Use ```verbose=True``` to create the object GeoIP2Fast to see the spent time to start.

![](https://raw.githubusercontent.com/rabuchaim/geoip2fast/main/images/geoip2fast_test.jpg)

Run the ```.../dist-packages/geoip2fast/tests/speed_test.py``` in your machine...

![](https://raw.githubusercontent.com/rabuchaim/geoip2fast/main/images/speed_test.jpg)

And there is coverage test also: ```.../dist-packages/geoip2fast/tests/coverage_test.py``` (run with -v to see more details)

![](https://raw.githubusercontent.com/rabuchaim/geoip2fast/main/images/coverage_test.jpg)

## geoip2fast.dat.gz file updates

The file ```geoip2fast.dat.gz``` ```v1.0.2```, has ```2419909 bytes```, ```md5sum 342408f7687a1b795ccdac6f2b78bf3b``` and was created based on ```Maxmind GeoLite2 CSV files from 1º/Sep/2023```, with 434446 networks from the CSV file plus 14 additions of special/private/reserved networks, totalizing ```434460 networks```.

You can check the date of CSV files used to create our .dat file with the function ```get_source_info()```

```
# python3
Python 3.10.12 (main, Jun 11 2023, 05:26:28) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
>>> from geoip2fast import GeoIP2Fast
>>> 
>>> MyGeoIP = GeoIP2Fast()
>>> 
>>> MyGeoIP.get_source_info()
'MAXMIND:GeoLite2-Country-CSV_20230109'
```
## GeoIP2Dat - update geoip2fast.dat.gz file anytime

Download the Geolite2 Country CSV files from Maxmind website and place it into some diretory (in this example, was placed into ```/opt/maxmind/```). Extract this zip file into this directory and run ```geoip2dat``` to see the options.

![](https://raw.githubusercontent.com/rabuchaim/geoip2fast/main/images/geoip2dat01.jpg)

The options ```--country-dir``` and ```--output-dir``` are mandatory. Specify the path of extracted files in ```--country-dir``` option. And for ```--output-dir```, put the current path ```./```. 

You can choose the language of country locations. The default is ```en```.

After creation of ```geoip2dat.dat.gz``` file, move this file to the directory of your application or to the directory of GeoIP2Fast library. You choose. 

![](https://raw.githubusercontent.com/rabuchaim/geoip2fast/main/images/geoip2dat02.jpg)

**From now you don't depend on anyone to have your data file updated.** There's no point the code being open-source if you're dependent of a single file. 

> *The Philosophers call it 'Libertas'* 


## Create your own GeoIP CLI with 6 lines

1. Create a file named ```geoipcli.py``` and save it in your home directory with the text below:
```python
#!/usr/bin/env python3
import os, sys, geoip2fast
if len(sys.argv) > 1 and sys.argv[1] is not None:
    geoip2fast.GeoIP2Fast().lookup(sys.argv[1]).pp_json(print_result=True)
else:
    print(f"Usage: {os.path.basename(__file__)} <ip_address>")
```
2. Give execution permisstion to your file and create a symbolic link to your new file into ```/usr/sbin``` folder, like this (let's assume that you saved the file into directory /root)
```bash
chmod 750 /root/geoipcli.py
ln -s /root/geoipcli.py /usr/sbin/geoipcli
```
3. Now, you just need to call ```geoipcli``` from any path.
```bash
# geoipcli
Usage: geoipcli <ip_address>

# geoipcli 1.2.3.4
{
   "ip": "1.2.3.4",
   "country_code": "AU",
   "country_name": "Australia",
   "cidr": "1.2.3.0/24",
   "hostname": "",
   "is_private": false,
   "elapsed_time": "0.000019727 sec"
}

# geoipcli x.y.z.w
{
   "ip": "x.y.z.w",
   "country_code": "",
   "country_name": "<invalid ip address>",
   "cidr": "",
   "hostname": "",
   "is_private": false,
   "elapsed_time": "0.000012493 sec"
}

# geoipcli 57.242.128.144
{
   "ip": "57.242.128.144",
   "country_code": "--",
   "country_name": "<network not found in database>",
   "cidr": "",
   "hostname": "",
   "is_private": false,
   "elapsed_time": "0.000019127 sec"
}
```

## GeoIP libraries that inspired me

**GeoIP2Nation - https://pypi.org/project/geoip2nation/** (Created by Avi Asher)

This library uses sqlite3 in-memory tables and use the same search concepts as GeoIP2Fast (based on search by the first´s IPs). Simple and fast! Until this date, the dump file that cames with pip install is corrupted, so use this link to download the complete SQL dump file http://www.ip2nation.com/ip2nation.zip. 

**GeoIP2 - https://pypi.org/project/geoip2/** (created by Maxmind)

This is the best library to work with Maxmind (paid subscription or with the free version). You can use http requests to Maxmind services or work with local Maxmind MMDB binary files. Pretty fast too. Sign-up to have access to all files of the free version https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

**\* Maxmind is a registered trademark** - https://www.maxmind.com

## TO DO list
- a pure-python version for REDIS with a very small footprint (pure protocol, won´t use any REDIS library) **<<< On the way**
- a Flask and FastAPI code;
- a mod_geoip2fast for NGINX;
- a better manual, maybe at readthedocs.io;
- a version with ASN and cities;
- **Done in v1.0.2** - *provide a script to update the base. If you have the paid subscription of Maxmind, you can download the files, extract into some directory and use this script to create your own geoip2fast.dat.gz file with the most complete, reliable and updated GeoIP information*.

## Sugestions, feedbacks, bugs, wrong locations...
E-mail me: ricardoabuchaim at gmail.com
