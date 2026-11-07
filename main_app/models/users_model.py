from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db  # Imports the db instance from models/db.py

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    def set_password(self, password):
        # Force pbkdf2:sha256 to ensure compatibility across all Python builds
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except AttributeError:
            # Handles legacy scrypt hashes safely if OpenSSL scrypt is unavailable
            return False