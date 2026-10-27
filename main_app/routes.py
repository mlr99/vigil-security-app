import os
from datetime import datetime
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.db import db
from models.users_model import User

main_bp = Blueprint('main', __name__)

# Folder setup for CSV dataset processing
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('main.events'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query MySQL for user
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Account is deactivated. Contact administrator.", "danger")
                return render_template('login.html')

            # Update login metrics in MySQL
            session['user_id'] = user.user_id
            session['username'] = user.username
            user.last_login = datetime.utcnow()
            user.failed_login_attempts = 0
            db.session.commit()

            flash("Logged in successfully!", "success")
            return redirect(url_for('main.events'))
        else:
            if user:
                user.failed_login_attempts += 1
                db.session.commit()

            flash("Invalid username or password.", "danger")

    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Logged out.", "info")
    return redirect(url_for('main.login'))

@main_bp.route('/events')
def events():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    # Query active registered users from MySQL
    users_in_db = User.query.all()

    # Format user data directly from the MySQL users table
    logs = [
        {
            "username": user.username,
            "time_active": "Active",
            "login_count": user.failed_login_attempts,
            "alert_level": "Warning" if user.failed_login_attempts > 2 else "Info",
            "more_info": f"Email: {user.email} | Active: {user.is_active}",
            "date": user.created_at.strftime('%Y-%m-%d') if user.created_at else "N/A",
            "time": user.last_login.strftime('%H:%M') if user.last_login else "Never"
        }
        for user in users_in_db
    ]

    return render_template('events.html', logs=logs)

@main_bp.route('/datasets/upload', methods=['POST'])
def upload_dataset():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if 'dataset_file' not in request.files:
        flash('No file part in request.', 'danger')
        return redirect(url_for('main.events'))

    file = request.files['dataset_file']

    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('main.events'))

    if file and allowed_file(file.filename):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Basic Schema Validation
        try:
            df = pd.read_csv(file_path, nrows=5)
            required_cols = {'timestamp', 'username', 'ip_address', 'status', 'failure_reason', 'user_agent'}

            if not required_cols.issubset(set(df.columns)):
                os.remove(file_path)
                flash(f'Invalid CSV schema! Headers must include: {", ".join(required_cols)}', 'danger')
                return redirect(url_for('main.events'))

            flash(f'Dataset "{file.filename}" successfully uploaded and validated!', 'success')
            return redirect(url_for('main.events'))

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Error reading CSV file: {str(e)}', 'danger')
            return redirect(url_for('main.events'))
    else:
        flash('Invalid file extension! Please upload a .csv file.', 'danger')
        return redirect(url_for('main.events'))