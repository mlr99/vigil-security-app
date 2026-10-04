import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'vigil-dev-secret-key')
    
    # Check for DATABASE_URL environment variable (e.g. for MySQL on Dell).
    # If not found, default to zero-config SQLite file on Mac/team machines.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///vigil.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False