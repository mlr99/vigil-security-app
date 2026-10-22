from datetime import datetime
from app import create_app
from models.db import db
from models.users_model import User

def seed_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            admin = User(
                username='admin',
                email='admin@vigil.io',
                is_active=True,
                failed_login_attempts=0,
                created_at=datetime.utcnow()
            )
            admin.set_password('password')
            db.session.add(admin)
            print("Creating 'admin' user...")
        else:
            # Reset password to ensure it matches 'password'
            admin.set_password('password')
            admin.failed_login_attempts = 0
            admin.is_active = True
            print("Updating existing 'admin' user password...")

        db.session.commit()
        print("✅ Admin user ready! Username: admin | Password: password")

if __name__ == '__main__':
    seed_admin_user()