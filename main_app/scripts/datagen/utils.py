"""
Vigil: Synthetic login data generator
File location: main_app/datagen/utils.py

Small helper functions used by several modules.
"""

import math # exp() used by poisson()
from datetime import datetime, timedelta, timezone  # dates and times

from .config import COMPANY_TZ


# Knuth's algorithm for generating a random number of events from a Poisson distribution
# This is used to determine how many times a user logs in on a given day, based on their average login rate.
def poisson(lam, rng):
    probability_threshold, event_count, random_product = math.exp(-lam), 0, 1.0
    while True:
        random_product *= rng.random()
        if random_product <= probability_threshold:
            return event_count
        event_count += 1


# Return a random usable IP address from the network 'net'.
# One /24 network has 256 addresses, with 254 available
def random_ip(net, rng):
    hosts = int(net.num_addresses) - 2
    return str(net.network_address + rng.randint(1, hosts))


# Convert a local date and hour CST to a UTC datetime.
def local_to_utc(day, hour_float):
    base = datetime(day.year, day.month, day.day, tzinfo=COMPANY_TZ)  # midnight CST
    return (base + timedelta(hours=hour_float)).astimezone(timezone.utc)
