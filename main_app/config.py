import os
from dotenv import load_dotenv

# Load variables from your .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'vigil-dev-secret-key')
    
    # Reads your MySQL connection string from .env
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'mysql+pymysql://root:password@localhost:3306/vigil_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False