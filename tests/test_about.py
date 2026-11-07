#Tests about page is reachable from the navbar after a successful login

def login(client):
    return client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
    )


def test_about_page_displays_after_login(client):
    login(client)
    response = client.get("/about")

    assert response.status_code == 200
    assert b"What is Vigil?" in response.data
    assert b"Welcome to Vigil!" in response.data


def test_about_page_requires_login(client):
    response = client.get("/about")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
