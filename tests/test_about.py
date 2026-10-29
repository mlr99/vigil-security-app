#Tests about page displays after successful login

def test_about_page_displays_after_login(client):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"What is Vigil?" in response.data
    assert b"Welcome to Vigil!" in response.data


def test_login_redirects_to_about(client):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/about")


def test_about_page_requires_login(client):
    response = client.get("/about")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]