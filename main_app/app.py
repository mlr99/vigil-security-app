from flask import Flask
from config import Config
from models.db import db
from models.users_model import User  
from routes import main_bp  
from flask_migrate import Migrate  

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)  

app.register_blueprint(main_bp)

with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@vigil.local')
        admin.set_password('password')  
        db.session.add(admin)
        db.session.commit()
        print("Created default admin user (admin / password)")

if __name__ == '__main__':
    app.run(debug=True)