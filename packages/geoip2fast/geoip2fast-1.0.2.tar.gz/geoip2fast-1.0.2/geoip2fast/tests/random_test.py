#!/usr/bin/env python3
from geoip2fast import GeoIP2Fast
from random import randrange
from time import sleep

MAX_IPS = 1000000
GeoIP = GeoIP2Fast(verbose=True)

print("\n- Starting a %d random IP test in"%(MAX_IPS),end="")
print(" 3...",end="")
sleep(1)
print(" 2...",end="")
sleep(1)
print(" 1...",end="")
sleep(1)
print("\n")

total = 0
while total < MAX_IPS:
    result = GeoIP.lookup(f"{randrange(0,254)}.{randrange(0,254)}.{randrange(0,254)}.{randrange(0,254)}")
    if result.country_code != "" and result.country_code != "--":
        total += 1
        print(f"IP {result.ip.ljust(20)}{result.country_code.ljust(4)}{result.country_name.ljust(40)}{result.elapsed_time}")
print("")

