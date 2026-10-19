from flask import Blueprint, render_template, request, redirect, url_for, flash, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('main.events'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user_id'] = 1
        flash("Logged in successfully!", "success")
        return redirect(url_for('main.events'))
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out.", "info")
    return redirect(url_for('main.login'))

@main_bp.route('/events')
def events():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    # Rich mock data passed directly from the backend
    logs = [
        {
            "username": "admin",
            "time_active": "1h 20m",
            "login_count": 5,
            "alert_level": "Info",
            "more_info": "Session initialized successfully",
            "date": "2026-10-19",
            "time": "12:25"
        },
        {
            "username": "marvin",
            "time_active": "45m",
            "login_count": 2,
            "alert_level": "Warning",
            "more_info": "Multiple failed attempts before success",
            "date": "2026-10-19",
            "time": "12:20"
        },
        {
            "username": "sarah_dev",
            "time_active": "3h 10m",
            "login_count": 8,
            "alert_level": "Info",
            "more_info": "DB migrations applied",
            "date": "2026-10-19",
            "time": "10:14"
        },
        {
            "username": "guest_user",
            "time_active": "10m",
            "login_count": 1,
            "alert_level": "Critical",
            "more_info": "Unauthorized route access attempt",
            "date": "2026-10-18",
            "time": "23:45"
        },
        {
            "username": "alex_m",
            "time_active": "2h 05m",
            "login_count": 3,
            "alert_level": "Info",
            "more_info": "Exported security audit report",
            "date": "2026-10-18",
            "time": "18:30"
        },
        {
            "username": "bot_service",
            "time_active": "0m",
            "login_count": 12,
            "alert_level": "Warning",
            "more_info": "High frequency API requests detected",
            "date": "2026-10-17",
            "time": "04:12"
        }
    ]

    return render_template('events.html', logs=logs)