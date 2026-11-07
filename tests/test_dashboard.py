#Tests the dashboard: landing page after login, and removing ingested data

import io

import pytest
import routes


@pytest.fixture(autouse=True)
def temp_upload_folder(tmp_path, monkeypatch):
    # Creates a temporary upload folder to keep test uploads (and the clear button's file cleanup) out of main_app/uploads
    monkeypatch.setattr(routes, "UPLOAD_FOLDER", str(tmp_path))
    monkeypatch.setattr(routes.dataset_service, "upload_folder", str(tmp_path))
    return tmp_path

#Sample CSV data
CSV = (
    b"timestamp,username,ip_address,status,failure_reason,user_agent\n"
    b"2026-01-01 10:00:00,alice,10.0.0.1,SUCCESS,,Mozilla\n"
    b"2026-01-01 10:05:00,bob,10.0.0.2,FAILED,Bad password,Mozilla\n"
)


def login(client):
    return client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
    )

def upload(client):
    return client.post(
        "/datasets/upload",
        data={"dataset_file": (io.BytesIO(CSV), "pytest_logs.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

def test_login_redirects_to_dashboard(client):
    response = login(client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/events")

# Without data, the table shows “No events ingested yet” and hides the 'Remove Ingested Data' button
def test_dashboard_empty_state(client):
    login(client)
    response = client.get("/events")

    assert b"No events ingested yet" in response.data
    assert b"Remove Ingested Data" not in response.data

#A valid CSV adds its users to the activity table and shows the Remove Ingested Data button.
def test_remove_ingested_data(client, temp_upload_folder):
    login(client)
    response = upload(client)
    assert b'data-username="alice"' in response.data
    assert b"Remove Ingested Data" in response.data
    assert (temp_upload_folder / "pytest_logs.csv").exists()

    response = client.post("/events/clear", follow_redirects=True)

    assert not (temp_upload_folder / "pytest_logs.csv").exists()

    assert b"Cleared 2 event records" in response.data
    assert b"No events ingested yet" in response.data
    assert b'data-username="alice"' not in response.data

# CSV with the wrong columns is rejected with “Invalid CSV schema!” and nothing is added
def test_upload_rejects_wrong_columns(client):
    login(client)
    response = client.post(
        "/datasets/upload",
        data={"dataset_file": (io.BytesIO(b"name,age\nalice,30\n"), "bad_columns.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Invalid CSV schema!" in response.data
    assert b"No events ingested yet" in response.data

# Only ingest CSV files (.txt files are rejected)
def test_upload_rejects_non_csv_file(client):
    login(client)
    response = client.post(
        "/datasets/upload",
        data={"dataset_file": (io.BytesIO(CSV), "logs.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Invalid file extension!" in response.data
    assert b"No events ingested yet" in response.data


def test_clear_requires_login(client):
    response = client.post("/events/clear")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]