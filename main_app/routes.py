import os
from datetime import datetime
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.db import db
from models.users_model import User
from models.event_model import EventLog

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
def about():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('about.html')

@main_bp.route('/events')
def events():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    # Query ingested EventLog records from MySQL (oldest first, so each
    # user's events are processed in order)
    event_records = EventLog.query.order_by(EventLog.timestamp.asc()).all()

    # Group raw login events into one summary per user
    users = {}
    seen = set()
    for log in event_records:
        # Skip exact duplicates (e.g. the same CSV uploaded twice)
        key = (log.timestamp, log.username, log.ip_address, log.status, log.failure_reason, log.user_agent)
        if key in seen:
            continue
        seen.add(key)
        name = log.username or "unknown"
        u = users.setdefault(name, {
            "first": None, "last": None, "attempts": 0,
            "failures": 0, "reasons": [], "ips": set(),
        })
        if log.timestamp:
            if u["first"] is None or log.timestamp < u["first"]:
                u["first"] = log.timestamp
            if u["last"] is None or log.timestamp > u["last"]:
                u["last"] = log.timestamp
        u["attempts"] += 1
        if log.ip_address:
            u["ips"].add(log.ip_address)
        if str(log.status or "").upper() in ['FAILED', 'FAILURE', 'CRITICAL']:
            u["failures"] += 1
            reason = log.failure_reason or "Unknown reason"
            if reason not in u["reasons"]:
                u["reasons"].append(reason)

    logs = []
    for name, u in users.items():
        # Time Active: span between the user's first and last event
        if u["first"] and u["last"]:
            minutes = int((u["last"] - u["first"]).total_seconds() // 60)
            time_active = f"{minutes // 60}h {minutes % 60}m" if minutes >= 60 else f"{minutes}m"
        else:
            time_active = "0m"

        # Alerts: 3+ failed logins = Critical, 1-2 = Warning, none = Info
        if u["failures"] >= 3:
            alert_level = "Critical"
        elif u["failures"] >= 1:
            alert_level = "Warning"
        else:
            alert_level = "Info"

        ip_text = f"{len(u['ips'])} IP" + ("s" if len(u["ips"]) != 1 else "")
        if u["failures"]:
            more_info = f"{u['failures']} failed: {', '.join(u['reasons'])} · {ip_text}"
        else:
            more_info = f"No failed logins · {ip_text}"

        logs.append({
            "username": name,
            "time_active": time_active,
            "login_count": u["attempts"],
            "alert_level": alert_level,
            "more_info": more_info,
            "last_seen": u["last"],
            "date": u["last"].strftime('%Y-%m-%d') if u["last"] else "N/A",
            "time": u["last"].strftime('%H:%M:%S') if u["last"] else "N/A",
        })

    # Most recently active users first
    logs.sort(key=lambda r: r["last_seen"] or datetime.min, reverse=True)

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

        try:
            df = pd.read_csv(file_path)
            required_cols = {'timestamp', 'username', 'ip_address', 'status', 'failure_reason', 'user_agent'}

            if not required_cols.issubset(set(df.columns)):
                os.remove(file_path)
                flash(f'Invalid CSV schema! Headers must include: {", ".join(required_cols)}', 'danger')
                return redirect(url_for('main.events'))

            # Parse CSV rows into EventLog objects
            new_events = []
            for _, row in df.iterrows():
                raw_ts = row['timestamp']
                try:
                    parsed_ts = datetime.strptime(str(raw_ts), '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    parsed_ts = datetime.utcnow()

                event = EventLog(
                    timestamp=parsed_ts,
                    username=str(row['username']),
                    ip_address=str(row['ip_address']),
                    status=str(row['status']),
                    failure_reason=str(row['failure_reason']) if pd.notnull(row['failure_reason']) else None,
                    user_agent=str(row['user_agent']) if pd.notnull(row['user_agent']) else None
                )
                new_events.append(event)

            db.session.bulk_save_objects(new_events)
            db.session.commit()

            flash(f'Dataset "{file.filename}" successfully uploaded and ingested ({len(new_events)} records)!', 'success')
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
def clear_events():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    try:
        num_deleted = db.session.query(EventLog).delete()
        db.session.commit()
        flash(f'Successfully cleared {num_deleted} event log records from the system.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing logs: {str(e)}', 'danger')

    return redirect(url_for('main.events'))