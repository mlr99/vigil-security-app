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
        else:
            print("Admin user found. Updating password hash to pbkdf2:sha256...")
            admin.set_password('password')
            admin.failed_login_attempts = 0
            admin.is_active = True
            db.session.add(admin)  # Explicitly stage the modified model

        db.session.commit()
        
        # Verify directly from DB
        updated_admin = User.query.filter_by(username='admin').first()
        print(f"Verified! Stored hash prefix: {updated_admin.password_hash[:13]}")
        print("Admin user ready. Credentials -> Username: admin | Password: password")

if __name__ == '__main__':
    seed_admin()