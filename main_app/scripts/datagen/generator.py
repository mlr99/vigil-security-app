"""
Vigil: Synthetic login data generator
File location: main_app/datagen/generator.py

Builds the whole day-by-day dataset.

The date range is split into a clean period (normal logins only) and an
anomaly window (normal logins plus randomly planted suspicious ones,
used to test scoring).
"""

import random
from datetime import datetime, timedelta

from .anomalies import anomaly_events
from .config import COMPANY_TZ
from .events import normal_event
from .users import make_users
from .utils import poisson


# Work out the first day, last day, and first day of the anomaly window.
# The last day is end_date, or today.
def date_range(days, anomaly_days, end_date=None):
    end = (datetime.fromisoformat(end_date).date() if end_date
           else datetime.now(COMPANY_TZ).date())
    start = end - timedelta(days=days - 1)
    anomaly_start = end - timedelta(days=anomaly_days - 1)
    return start, end, anomaly_start


# All the (user, event) pairs for one user on one day.
def events_for_day(user, day, anomaly_start, anomaly_rate, rng):
    pairs = []

    # Normal logins for this user on this day.
    # Skip weekends unless this person works weekends.
    is_weekend = day.weekday() >= 5  # Saturday = 5, Sunday = 6
    if not is_weekend or user["works_weekends"]:
        for _ in range(poisson(user["logins_per_day"], rng)):
            pairs.append((user, normal_event(user, day, rng)))

    # Maybe plant an anomaly
    # Only inside the anomaly window, and with a small chance per user per day (--anomaly-rate, default 3%).
    if day >= anomaly_start and rng.random() < anomaly_rate:
        injected = anomaly_events(user, day, rng)

        # Skip case for a normal weekend worker
        is_weekend_kind = any(e["anomaly_type"] == "weekend_login" for e in injected)
        if not (is_weekend_kind and user["works_weekends"]):
            pairs.extend((user, ev) for ev in injected)

    return pairs


# Build the full dataset.
# Each item in 'events' is a (user, event) pair sorted by event time.
def generate(num_users=50, days=60, anomaly_days=14, anomaly_rate=0.03,
             end_date=None, seed=42):
    rng = random.Random(seed)
    users = make_users(num_users, rng)
    start, end, anomaly_start = date_range(days, anomaly_days, end_date)

    events = []
    for user in users:
        day = start
        while day <= end:
            events.extend(events_for_day(user, day, anomaly_start, anomaly_rate, rng))
            day += timedelta(days=1)

    # Sort log by event time
    events.sort(key=lambda pair: pair[1]["ts"])
    return users, events, start, end, anomaly_start