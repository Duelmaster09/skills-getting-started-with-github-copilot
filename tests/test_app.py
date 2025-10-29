import uuid

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check for a known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = unique_email()
    activity = "Chess Club"

    # Ensure not already registered
    data = client.get("/activities").json()
    assert email not in data[activity]["participants"]

    # Sign up
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Confirm present
    data = client.get("/activities").json()
    assert email in data[activity]["participants"]

    # Unregister
    r = client.delete(f"/activities/{activity}/participants?email={email}")
    assert r.status_code == 200
    assert "Unregistered" in r.json().get("message", "")

    # Confirm removed
    data = client.get("/activities").json()
    assert email not in data[activity]["participants"]


def test_signup_duplicate_fails():
    email = unique_email()
    activity = "Chess Club"

    # First signup should succeed
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # Second signup should fail with 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # Cleanup
    client.delete(f"/activities/{activity}/participants?email={email}")
