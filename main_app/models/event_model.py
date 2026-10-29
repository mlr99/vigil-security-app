# models/event_model.py
from datetime import datetime
from models.db import db


class EventLog(db.Model):
    # New table name on purpose: your MySQL database already has an
    # "event_logs" table built from the old model, and db.create_all()
    # never adds columns to a table that exists. A new name lets
    # create_all() build this table fresh with every column below,
    # so no SQL or migration is needed. The old table is left untouched.
    __tablename__ = 'event_log_records'

    id = db.Column(db.Integer, primary_key=True)

    # Fields from the uploaded CSV (used by upload_dataset and /events)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    username = db.Column(db.String(150), nullable=False, index=True)
    ip_address = db.Column(db.String(45))            # 45 fits IPv6
    status = db.Column(db.String(20))
    failure_reason = db.Column(db.String(255), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)

    # Optional link to an app account. Nullable because the CSV
    # usernames don't have to exist in the users table.
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user = db.relationship('User', backref='event_logs')

    # Original summary fields, kept so nothing else that uses them breaks
    time_active = db.Column(db.String(50), default="0m")
    login_count = db.Column(db.Integer, default=1)
    alert_level = db.Column(db.String(20), default="Info")
    more_info = db.Column(db.String(255), nullable=True)