import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vigil_dev_secret_key_123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/vigil_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False