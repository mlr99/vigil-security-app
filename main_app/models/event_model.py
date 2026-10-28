# models/event_model.py
from datetime import datetime
from models.db import db

class EventLog(db.Model):
    __tablename__ = 'event_logs'

    id = db.Column(db.Integer, primary_key=True)
    
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    time_active = db.Column(db.String(50), default="0m")
    login_count = db.Column(db.Integer, default=1)
    alert_level = db.Column(db.String(20), default="Info")
    more_info = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

   
    user = db.relationship('User', backref='event_logs')