"""
Vigil: Synthetic login data generator
File location: main_app/generate_logins.py

to run:
py generate_logins.py
py generate_logins.py --users 100 --days 90 --anomaly-days 20 --seed 7

This file handles the command line from the datagen package.

  datagen/config.py     - constants (names, IP ranges, countries, time zone)
  datagen/utils.py      - poisson(), random_ip(), local_to_utc()
  datagen/users.py      - fake employees and their habits
  datagen/events.py     - one normal login
  datagen/anomalies.py  - planted suspicious logins (one function per type)
  datagen/generator.py  - builds the day-by-day dataset
  datagen/writer.py     - writes the CSV files

The following files are created from output:
  users.csv: rows for the MONITORED_USER table
  login_events.csv: rows for the LOGIN_EVENT table + two extra "answer key" columns (is_anomaly, anomaly_type)

The answer key columns are only for checking how well Vigil's scoring
works ("we caught 20 of the 25 planted anomalies"). LogIngestor should
ignore them, because real logs never come with labels.

Using tzdata
"""
from pathlib import Path
import argparse # reads CLI options like --users 100
from datetime import timedelta

from datagen import generate, write_outputs


DATA_DIR = Path(__file__).resolve().parent.parent / "scripts" / "data"


def parse_args():
    p = argparse.ArgumentParser(description="Generate synthetic login data for Vigil.")
    p.add_argument("--users", type=int, default=50,help="number of monitored users")
    p.add_argument("--days", type=int, default=60,help="total days of history")
    p.add_argument("--anomaly-days", type=int, default=14, help="final N days that may contain anomalies; "
                    "earlier days are clean and can be used to train the baseline")
    p.add_argument("--anomaly-rate", type=float, default=0.03,
                   help="chance per user per day (in the anomaly window) of an anomaly")
    p.add_argument("--end-date", help="last day of data, YYYY-MM-DD (default: today)")
    p.add_argument("--seed", type=int, default=42, help="random seed for reproducible data")

    p.add_argument("--users-out", default=str(DATA_DIR / "users.csv"))
    p.add_argument("--events-out", default=str(DATA_DIR / "login_events.csv"))

    return p.parse_args()


# Print a short summary so you can see what was made.
# The anomaly count > number of separate incidents since it includes every row of a brute force burst.
def print_summary(users, events, start, end, anomaly_start, users_out, events_out):
    n_anom = sum(1 for _, ev in events if ev["is_anomaly"])
    print(f"Users:        {len(users)}")
    print(f"Events:       {len(events)}  ({n_anom} labeled anomalous)")
    print(f"Clean period: {start} to {anomaly_start - timedelta(days=1)}  (use for baseline)")
    print(f"Test period:  {anomaly_start} to {end}")
    print(f"Wrote {users_out} and {events_out}")


def main():
    args = parse_args()

    users, events, start, end, anomaly_start = generate(
        num_users=args.users,
        days=args.days,
        anomaly_days=args.anomaly_days,
        anomaly_rate=args.anomaly_rate,
        end_date=args.end_date,
        seed=args.seed,
    )
    write_outputs(users, events, args.users_out, args.events_out)
    print_summary(users, events, start, end, anomaly_start, args.users_out, args.events_out)


if __name__ == "__main__":
    main()
