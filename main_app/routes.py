from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import db
from models.users_model import User

# Define the blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('main.home'))
        else:
            if user:
                user.failed_login_attempts += 1
                db.session.commit()

            flash('Invalid username or password', 'error')
            return redirect(url_for('main.login'))

    return render_template('login.html')