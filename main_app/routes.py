import os
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.db import db
from models.users_model import User
from models.event_model import EventLog
from services.log_processor import LogProcessor, DatasetValidationError

main_bp = Blueprint('main', __name__)

# Folder setup for CSV dataset processing
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'csv'}

log_processor = LogProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return view(*args, **kwargs)
    return wrapped

@main_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('main.about'))
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
            return redirect(url_for('main.about'))
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

@main_bp.route('/about')
@login_required
def about():
    return render_template('about.html')

@main_bp.route('/events')
@login_required
def events():
    # Oldest first, so each user's events are processed in order
    event_records = EventLog.query.order_by(EventLog.timestamp.asc()).all()
    logs = log_processor.summarize_by_user(event_records)
    return render_template('events.html', logs=logs)

@main_bp.route('/datasets/upload', methods=['POST'])
@login_required
def upload_dataset():
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

        try:
            new_events = log_processor.parse_csv(file_path)

            db.session.bulk_save_objects(new_events)
            db.session.commit()

            flash(f'Dataset "{file.filename}" successfully uploaded and ingested ({len(new_events)} records)!', 'success')
            return redirect(url_for('main.events'))

        except DatasetValidationError as e:
            os.remove(file_path)
            flash(str(e), 'danger')
            return redirect(url_for('main.events'))

        except Exception as e:
            db.session.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Error reading CSV file: {str(e)}', 'danger')
            return redirect(url_for('main.events'))
    else:
        flash('Invalid file extension! Please upload a .csv file.', 'danger')
        return redirect(url_for('main.events'))

@main_bp.route('/events/clear', methods=['POST'])
@login_required
def clear_events():
    try:
        num_deleted = db.session.query(EventLog).delete()
        db.session.commit()
        flash(f'Successfully cleared {num_deleted} event log records from the system.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing logs: {str(e)}', 'danger')

    return redirect(url_for('main.events'))