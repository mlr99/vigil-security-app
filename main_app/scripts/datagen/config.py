"""
Vigil: Synthetic login data generator
File location: main_app/datagen/config.py

"""

import ipaddress     # builds IP addresses from a network range
from zoneinfo import ZoneInfo  # defining time zones (needs tzdata on Windows)

# Pool of random first and last names for user generation.
FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie",
               "Avery", "Quinn", "Drew", "Sam", "Cameron", "Reese", "Parker",
               "Dakota", "Hayden", "Emerson", "Rowan", "Skyler", "Logan"]
LAST_NAMES = ["Smith", "Nguyen", "Garcia", "Patel", "Johnson", "Lee", "Brown",
              "Davis", "Martinez", "Wilson", "Clark", "Lewis", "Walker", "Hall",
              "Young", "King", "Wright", "Scott", "Green", "Baker"]

# Pools of IP addresses to pick from.
# 10.20.0.x is a private range, used here for the "office network".
# 198.51.100.x and 203.0.113.x are ranges officially reserved for documentation and examples, used for 'home' and 'foreign' logins.
OFFICE_NET = ipaddress.ip_network("10.20.0.0/24")
HOME_NET = ipaddress.ip_network("198.51.100.0/24")
FOREIGN_NET = ipaddress.ip_network("203.0.113.0/24")

# Pool of foreign country codes (Russia, China, Brazil, Nigeria, Romania, Vietnam, North Korea, Iran)
FOREIGN_COUNTRIES = ["RU", "CN", "BR", "NG", "RO", "VN", "KP", "IR"]

COMPANY_TZ = ZoneInfo("America/Chicago")
DOMAIN = "example.com"

# The order of this list matters
# rng.choice() picks from it, so reordering it changes which anomaly a given seed produces.
ANOMALY_TYPES = ["odd_hour", "new_country", "brute_force",
                 "impossible_travel", "long_session", "weekend_login"]
