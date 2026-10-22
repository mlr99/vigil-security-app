"""
Vigil: Synthetic login data generator
File location: main_app/datagen/anomalies.py

Plants suspicious logins for testing Vigil's scoring.

Each anomaly type has its own small function. They all take the same
arguments (user, day, base, rng) and return a list of event dicts.
'base' is a normal login already marked as an anomaly.

"""

from datetime import timedelta
from .config import ANOMALY_TYPES, FOREIGN_COUNTRIES, FOREIGN_NET
from .events import normal_event
from .utils import local_to_utc, random_ip


# A login about 12 hours away from the user's usual start time (e.g. 3 AM).
def odd_hour(user, day, base, rng):
    base["ts"] = local_to_utc(day, (user["start_hour"] + 12 + rng.uniform(-1.5, 1.5)) % 24)
    return [base]


# A login from a foreign country this user has never logged in from.
def new_country(user, day, base, rng):
    base["ip"], base["country"] = random_ip(FOREIGN_NET, rng), rng.choice(FOREIGN_COUNTRIES)
    return [base]


# 6 - 20 failed logins in a row a few seconds apart from one foreign IP at any hour.
def brute_force(user, day, base, rng):
    kind = base["anomaly_type"]
    ip, country = random_ip(FOREIGN_NET, rng), rng.choice(FOREIGN_COUNTRIES)
    start = local_to_utc(day, rng.uniform(0, 24))
    events = []
    for i in range(rng.randint(6, 20)):
        events.append({"ts": start + timedelta(seconds=i * rng.randint(2, 15)),
                       "ip": ip, "country": country, "minutes": 0, "success": False,
                       "is_anomaly": True, "anomaly_type": kind})

    # 40% of the time, the attacker eventually guesses right and successfully logs in
    if rng.random() < 0.4:
        events.append({"ts": events[-1]["ts"] + timedelta(seconds=5), "ip": ip,
                       "country": country, "minutes": rng.randint(2, 30),
                       "success": True, "is_anomaly": True, "anomaly_type": kind})
    return events


# User shouldn't log in from two different countries within a short time
def impossible_travel(user, day, base, rng):
    first = normal_event(user, day, rng)
    second = dict(base, ts=first["ts"] + timedelta(minutes=rng.randint(5, 40)),
                  ip=random_ip(FOREIGN_NET, rng),
                  country=rng.choice(FOREIGN_COUNTRIES))
    return [first, second]


# A session 6 to 12 times longer than this person's usual
def long_session(user, day, base, rng):
    base["minutes"] = round(user["session_median_min"] * rng.uniform(6, 12))
    return [base]


# Move the login to the next Saturday (weekday 5).
# Days of week are numbered Monday=0 through Sunday=6
# (5 - weekday) % 7  =  how many days until Saturday.
# It happens near the user's usual start time, only the day is unusual
def weekend_login(user, day, base, rng):
    shift = (5 - day.weekday()) % 7
    base["ts"] = local_to_utc(day + timedelta(days=shift),
                              rng.uniform(user["start_hour"], user["start_hour"] + 3))
    return [base]


# Maps each anomaly name to the function that builds it.
ANOMALY_BUILDERS = {
    "odd_hour": odd_hour,
    "new_country": new_country,
    "brute_force": brute_force,
    "impossible_travel": impossible_travel,
    "long_session": long_session,
    "weekend_login": weekend_login,
}


# Plant one randomly chosen suspicious login (or group of logins).
def anomaly_events(user, day, rng):
    kind = rng.choice(ANOMALY_TYPES)
    base = normal_event(user, day, rng)
    base.update(is_anomaly=True, anomaly_type=kind, success=True)

    builder = ANOMALY_BUILDERS.get(kind)

    # Safety net (should never be reached since every type is handled)
    if builder is None:
        return [base]
    return builder(user, day, base, rng)
