#Tests login failures, deactivated accounts, and logout

from models.db import db
from models.users_model import User

def login(client, password="testpassword"):
    return client.post(
        "/login",
        data={"username": "testuser", "password": password},
        follow_redirects=True,
    )

def get_user():
    return User.query.filter_by(username="testuser").first()

#Incorrect password is rejects a login and is recorded.
def test_wrong_password_is_rejected_and_counted(client):
    response = login(client, password="wrong")

    assert b"Invalid username or password." in response.data
    assert b"Log In to Vigil" in response.data
    assert get_user().failed_login_attempts == 1


def test_deactivated_account_cannot_log_in(client):
    user = get_user()
    user.is_active = False
    db.session.commit()

    response = login(client)

    assert b"Account is deactivated" in response.data
    assert client.get("/events").status_code == 302


def test_logout_ends_session(client):
    login(client)
    assert client.get("/events").status_code == 200

    client.get("/logout")
    response = client.get("/events")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
