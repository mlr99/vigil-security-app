from flask import Flask
from config import Config
from models.db import db
from routes import main_bp  # Import the blueprint

app = Flask(__name__)
app.config.from_object(Config)

# Attach SQLAlchemy to the Flask app
db.init_app(app)

# Register the routes blueprint
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)