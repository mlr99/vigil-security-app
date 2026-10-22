"""
Vigil: Synthetic login data generator
File location: main_app/datagen/events.py

Creates ordinary ("normal") login events that follow a user's habits.
"""

import math # log() for the session-length distribution

from .config import OFFICE_NET
from .utils import local_to_utc, random_ip


# Create one normal login
def normal_event(user, day, rng):

    # Pick a random moment inside this person's usual work window
    hour = rng.uniform(user["start_hour"], user["start_hour"] + user["shift_hours"])

    # Office or home? Uses the person's office_share probability
    ip = (random_ip(OFFICE_NET, rng) if rng.random() < user["office_share"]
          else rng.choice(user["home_ips"]))

    # Successful?
    success = rng.random() > user["fail_rate"]

    # Session length: "log-normal" distribution allows for an occasional long session.
    # max(1, ...) makes sure a successful session is at least 1 minute long.
    # A failed login never started a session, so it gets 0 minutes.
    minutes = (max(1, round(rng.lognormvariate(math.log(user["session_median_min"]), 0.5)))
               if success else 0)

    return {"ts": local_to_utc(day, hour),
            "ip": ip,
            "country": "US",
            "minutes": minutes,
            "success": success,
            "is_anomaly": False,  # answer key (this one is normal)
            "anomaly_type": ""}
