import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers.get("location", "")

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]

def test_signup_success():
    # Test successful signup
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Programming%20Class/signup?email=duplicate@example.com")
    # Second signup should fail
    response = client.post("/activities/Programming%20Class/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student is already signed up" in data["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unsubscribe_success():
    # First signup
    client.post("/activities/Gym%20Class/signup?email=unsub@example.com")
    # Then unsubscribe
    response = client.post("/activities/Gym%20Class/unsubscribe?email=unsub@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unsubscribed unsub@example.com from Gym Class" in data["message"]

    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "unsub@example.com" not in data["Gym Class"]["participants"]

def test_unsubscribe_not_found():
    response = client.post("/activities/Gym%20Class/unsubscribe?email=notfound@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]