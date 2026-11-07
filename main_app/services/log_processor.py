"""Data preprocessing for login event logs.

Routes should only handle HTTP concerns (auth checks, reading the request,
choosing a template). Everything turns raw CSV rows or EventLog
records into something displayable.
"""

from datetime import datetime
import pandas as pd
from models.event_model import EventLog

class DatasetValidationError(ValueError):
    """Raised when an uploaded dataset doesn't match the expected schema."""

class LogProcessor:
    REQUIRED_COLUMNS = ('timestamp', 'username', 'ip_address', 'status', 'failure_reason', 'user_agent')
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
    FAILURE_STATUSES = {'FAILED', 'FAILURE', 'CRITICAL'}

    # alert thresholds: this many failed logins or more triggers the level
    CRITICAL_THRESHOLD = 3
    WARNING_THRESHOLD = 1

    # Ingestion: CSV file -> EventLog objects
    def parse_csv(self, file_path):
        """Read a CSV file and return a list of unsaved EventLog objects.

           Raises DatasetValidationError if required columns are missing.
        """
        df = pd.read_csv(file_path)

        missing = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise DatasetValidationError(
                f'Invalid CSV schema! Headers must include: {", ".join(self.REQUIRED_COLUMNS)}'
            )

        return [self._row_to_event(row) for _, row in df.iterrows()]

    def _row_to_event(self, row):
        return EventLog(
            timestamp=self._parse_timestamp(row['timestamp']),
            username=str(row['username']),
            ip_address=str(row['ip_address']),
            status=str(row['status']),
            failure_reason=self._optional_str(row['failure_reason']),
            user_agent=self._optional_str(row['user_agent']),
        )

    def _parse_timestamp(self, raw):
        try:
            return datetime.strptime(str(raw), self.TIMESTAMP_FORMAT)
        except ValueError:
            return datetime.utcnow()

    @staticmethod
    def _optional_str(value):
        return str(value) if pd.notnull(value) else None

    # Reporting: EventLog records -> per-user summary rows
    def summarize_by_user(self, records):
        """Group raw login events into one summary dict per user.

        `records` should be ordered oldest-first. Exact duplicate events
        (e.g. the same CSV uploaded twice) are counted once. Returns a list
        sorted with the most recently active users first.
        """
        users = self._aggregate(records)
        rows = [self._build_row(name, stats) for name, stats in users.items()]
        rows.sort(key=lambda r: r['last_seen'] or datetime.min, reverse=True)
        return rows

    def _aggregate(self, records):
        users = {}
        seen = set()
        for log in records:
            key = (log.timestamp, log.username, log.ip_address, log.status, log.failure_reason, log.user_agent)
            if key in seen:
                continue
            seen.add(key)

            stats = users.setdefault(log.username or 'unknown', {
                'first': None, 'last': None, 'attempts': 0,
                'failures': 0, 'reasons': [], 'ips': set(),
            })

            if log.timestamp:
                if stats['first'] is None or log.timestamp < stats['first']:
                    stats['first'] = log.timestamp
                if stats['last'] is None or log.timestamp > stats['last']:
                    stats['last'] = log.timestamp

            stats['attempts'] += 1
            if log.ip_address:
                stats['ips'].add(log.ip_address)

            if self.is_failure(log.status):
                stats['failures'] += 1
                reason = log.failure_reason or 'Unknown reason'
                if reason not in stats['reasons']:
                    stats['reasons'].append(reason)
        return users

    def _build_row(self, name, stats):
        last = stats['last']
        return {
            'username': name,
            'time_active': self.format_duration(stats['first'], last),
            'login_count': stats['attempts'],
            'alert_level': self.alert_level(stats['failures']),
            'more_info': self._more_info(stats),
            'last_seen': last,
            'date': last.strftime('%Y-%m-%d') if last else 'N/A',
            'time': last.strftime('%H:%M:%S') if last else 'N/A',
        }

    # Small helpers (public so we can unit test them directly)
    def is_failure(self, status):
        return str(status or '').upper() in self.FAILURE_STATUSES

    def alert_level(self, failures):
        if failures >= self.CRITICAL_THRESHOLD:
            return 'Critical'
        if failures >= self.WARNING_THRESHOLD:
            return 'Warning'
        return 'Info'

    @staticmethod
    def format_duration(first, last):
        """Time span between first and last event, e.g. '45m' or '2h 5m'."""
        if not (first and last):
            return '0m'
        minutes = int((last - first).total_seconds() // 60)
        return f'{minutes // 60}h {minutes % 60}m' if minutes >= 60 else f'{minutes}m'

    @staticmethod
    def _more_info(stats):
        ip_count = len(stats['ips'])
        ip_text = f"{ip_count} IP" + ('s' if ip_count != 1 else '')
        if stats['failures']:
            return f"{stats['failures']} failed: {', '.join(stats['reasons'])} · {ip_text}"
        return f'No failed logins · {ip_text}'
