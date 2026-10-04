from flask import Flask
from config import Config
from models.db import db
from models.users_model import User  
from routes import main_bp  

app = Flask(__name__)
app.config.from_object(Config)

# Attach SQLAlchemy to the Flask app
db.init_app(app)

# Register the routes blueprint
app.register_blueprint(main_bp)

# Automatically create tables and seed default data on startup
with app.app_context():
    db.create_all()

    
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@vigil.local')
        admin.set_password('password')  
        db.session.add(admin)
        db.session.commit()
        print("Created default admin user (admin / password)")

if __name__ == '__main__':
    app.run(debug=True)