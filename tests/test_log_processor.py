#Unit tests for LogProcessor: the data preprocessing kept out of the routes

from datetime import datetime

import pytest

from models.event_model import EventLog
from services.log_processor import LogProcessor


@pytest.fixture
def processor():
    return LogProcessor()

#Creates a test EventLog object
def event(username, time, status="SUCCESS", ip="10.0.0.1", reason=None):
    return EventLog(
        timestamp=datetime.strptime(f"2026-01-01 {time}", "%Y-%m-%d %H:%M"),
        username=username,
        ip_address=ip,
        status=status,
        failure_reason=reason,
        user_agent="Mozilla",
    )

#Tests for correct alert level
@pytest.mark.parametrize("failures, expected", [
    (0, "Info"),
    (1, "Warning"),
    (2, "Warning"),
    (3, "Critical"),
])
def test_alert_level_thresholds(processor, failures, expected):
    assert processor.alert_level(failures) == expected

def test_duplicate_events_are_counted_once(processor):
    records = [event("alice", "10:00"), event("alice", "10:00")]

    rows = processor.summarize_by_user(records)

    assert len(rows) == 1
    assert rows[0]["login_count"] == 1


def test_summary_per_user(processor):
    records = [
        event("alice", "08:00"),
        event("bob", "09:00", status="FAILED", ip="10.0.0.2", reason="Bad password"),
        event("bob", "09:30", status="FAILED", ip="10.0.0.3", reason="Locked"),
    ]

    rows = processor.summarize_by_user(records)
    bob, alice = rows  # most recently active first

    assert bob["username"] == "bob"
    assert bob["login_count"] == 2
    assert bob["alert_level"] == "Warning"
    assert bob["time_active"] == "30m"
    assert bob["more_info"] == "2 failed: Bad password, Locked · 2 IPs"

    assert alice["alert_level"] == "Info"
    assert alice["more_info"] == "No failed logins · 1 IP"
