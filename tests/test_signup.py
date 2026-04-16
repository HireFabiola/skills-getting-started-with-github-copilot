import pytest
from urllib.parse import quote


def test_signup_success(client):
    """Test successful signup for an activity"""
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]


def test_signup_adds_participant(client):
    """Test that signup actually adds the participant to the activity"""
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    # Signup
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Verify participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate_fails(client):
    """Test that duplicate signup returns 400 error"""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity_fails(client):
    """Test that signup for nonexistent activity returns 404"""
    email = "newstudent@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_increases_participant_count(client):
    """Test that signup increases the participant count"""
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()[activity]["participants"])
    
    # Signup
    client.post(
        f"/activities/{activity}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    
    # Get updated count
    response = client.get("/activities")
    updated_count = len(response.json()[activity]["participants"])
    
    assert updated_count == initial_count + 1


def test_signup_multiple_same_activity(client):
    """Test that multiple different users can sign up for same activity"""
    activity = "Programming Class"
    email1 = "user1@mergington.edu"
    email2 = "user2@mergington.edu"
    
    # First signup
    response1 = client.post(
        f"/activities/{activity}/signup?email={email1}",
        headers={"accept": "application/json"}
    )
    assert response1.status_code == 200
    
    # Second signup
    response2 = client.post(
        f"/activities/{activity}/signup?email={email2}",
        headers={"accept": "application/json"}
    )
    assert response2.status_code == 200
    
    # Verify both are registered
    response = client.get("/activities")
    participants = response.json()[activity]["participants"]
    assert email1 in participants
    assert email2 in participants


def test_signup_email_parameter_encoding(client):
    """Test that email with special characters is handled correctly"""
    email = "student+test@mergington.edu"
    activity = "Art Club"
    
    response = client.post(
        f"/activities/{activity}/signup?email={quote(email)}",
        headers={"accept": "application/json"}
    )
    
    assert response.status_code == 200
    
    # Verify in activities
    response = client.get("/activities")
    assert email in response.json()[activity]["participants"]
