"""
Vigil: Synthetic login data generator
File location: main_app/datagen/writer.py

Writes the generated data to CSV files that match Vigil's database tables.

  users.csv: rows for the MONITORED_USER table
  login_events.csv: rows for the LOGIN_EVENT table + two extra "answer key"
  columns (is_anomaly, anomaly_type)
"""

import csv # writes the output .csv files

# users.csv: one row per monitored user. Nobody starts blocked.
def write_users(users, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["user_id", "name", "email", "is_blocked"])
        for u in users:
            w.writerow([u["user_id"], u["name"], u["email"], False])

# login_events.csv: one row per login, in time order.
def write_events(events, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "user_id", "ip_address", "timestamp", "session_minutes",
                    "success", "country", "is_anomaly", "anomaly_type"])

        # event_id counts up from 1 in time order.
        for i, (u, ev) in enumerate(events, start=1):
            w.writerow([i, u["user_id"], ev["ip"],
                        # ISO 8601 format in UTC, e.g. 2026-09-14T03:12:44Z
                        # (the trailing Z means UTC). SQL reads this directly into a timestamptz column.
                        ev["ts"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                        ev["minutes"], ev["success"], ev["country"],
                        ev["is_anomaly"], ev["anomaly_type"]])

# Write both CSV files
def write_outputs(users, events, users_out="users.csv", events_out="login_events.csv"):
    write_users(users, users_out)
    write_events(events, events_out)