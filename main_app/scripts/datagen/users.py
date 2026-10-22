"""
Vigil: Synthetic login data generator
File location: main_app/data-generator/users.py

Creates the employees. Each one gets a persona:
their habits, such as what time they start work, whether they work weekends,
and which IP addresses they normally log in from.
"""

from .config import DOMAIN, FIRST_NAMES, HOME_NET, LAST_NAMES
from .utils import random_ip

# Build a unique email address for a first/last name pair.
# Issue: Two generated users could get the same full name
# Solution: emails must be unique
# if a duplicate is found, add a number to the end of the email address
def unique_email(first, last, used_emails):
    email = f"{first}.{last}".lower()
    suffix = 1
    while f"{email}@{DOMAIN}" in used_emails:
        suffix += 1
        email = f"{first}.{last}{suffix}".lower()
    email = f"{email}@{DOMAIN}"
    used_emails.add(email)
    return email


# Create one user and their habits for the baseline.
def make_user(uid, rng, used_emails):
    first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
    email = unique_email(first, last, used_emails)

    # Work pattern by role
    # Weights mean about 75% standard day workers, 10% night shift, and 15% remote.
    role = rng.choices(["standard", "night_shift", "remote"],
                       weights=[75, 10, 15])[0]

    # Typical start-of-work hour, picked from a bell curve
    # (rng.gauss(average, spread)) so people vary a little:
    #   standard:    around 8 AM, give or take around 45 minutes
    #   night shift: around 9 PM
    #   remote:      around 9:30 AM, with more variation
    # All three gauss() calls run, matching the original, so the
    # random sequence (and therefore the output for a given seed) is unchanged.
    start = {"standard": rng.gauss(8, 0.75),
             "night_shift": rng.gauss(21, 1.0),
             "remote": rng.gauss(9.5, 1.25)}[role]

    return {
        "user_id": uid,
        "name": f"{first} {last}",
        "email": email,
        "role": role,

        # "% 24" wraps hours past midnight back to 0-23
        "start_hour": start % 24,

        # How long their normal workday lasts (7.5 to 9.5 hours).
        "shift_hours": rng.uniform(7.5, 9.5),

        # Does this person normally work Saturday/Sunday?
        # 35% of night shift workers do; only 8% of everyone else.
        "works_weekends": rng.random() < (0.35 if role == "night_shift" else 0.08),

        # Average number of logins per workday (1 to 4).
        # Fed into poisson() each day.
        "logins_per_day": rng.uniform(1.0, 4.0),

        # Each person has 1 or 2 home IP addresses they use when not in the office.
        "home_ips": [random_ip(HOME_NET, rng) for _ in range(rng.randint(1, 2))],

        # Chance a given login comes from the office network rather than home.
        # Remote workers are mostly at home (20% office). Everyone else (80%) is mostly in the office.
        "office_share": 0.2 if role == "remote" else 0.8,

        # This person's typical session length, 25 to 120 minutes.
        "session_median_min": rng.uniform(25, 120),

        # How often they mistype their password (1% to 6% of logins).
        # A few failed logins are normal, a burst of them is not.
        "fail_rate": rng.uniform(0.01, 0.06),
    }


# create 'n' users and return a list of dictionaries, one per user
def make_users(n, rng):
    used_emails = set()
    return [make_user(uid, rng, used_emails) for uid in range(1, n + 1)]
