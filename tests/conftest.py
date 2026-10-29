#this file is ment to configure pytest so that test files are pre-configured.

import os
import sys

import pytest
from flask import Flask

MAIN_APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main_app"))
sys.path.insert(0, MAIN_APP_DIR)

from models.db import db
from models.users_model import User
from routes import main_bp


@pytest.fixture
def client():
    app = Flask(
        __name__,
        template_folder=os.path.join(MAIN_APP_DIR, "templates"),
        static_folder=os.path.join(MAIN_APP_DIR, "static"),
    )
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        user = User(username="testuser", email="testuser@vigil.local")
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()