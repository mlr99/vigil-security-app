from app import app
from models.db import db
from models.users_model import User

def seed_admin():
    with app.app_context():
        
        db.create_all()

        
        admin = User.query.filter_by(username='admin').first()

        if not admin:
            print("Creating default admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                is_active=True
            )
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()
            print("Successfully created 'admin' user with password 'password'!")
        else:
            print("Admin user already exists. Resetting password to 'password'...")
            admin.set_password('password')
            admin.failed_login_attempts = 0
            admin.is_active = True
            db.session.commit()
            print("Admin password reset to 'password'!")

if __name__ == '__main__':
    seed_admin()