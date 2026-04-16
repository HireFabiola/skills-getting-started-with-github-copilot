import pytest


def test_unregister_success(client):
    """Test successful unregister from an activity"""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]


def test_unregister_removes_participant(client):
    """Test that unregister actually removes the participant"""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    # Verify participant is there
    response = client.get("/activities")
    assert email in response.json()[activity]["participants"]
    
    # Unregister
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Verify participant was removed
    response = client.get("/activities")
    assert email not in response.json()[activity]["participants"]


def test_unregister_nonexistent_activity_fails(client):
    """Test that unregister from nonexistent activity returns 404"""
    email = "student@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_not_registered_fails(client):
    """Test that unregistering non-participant returns 400"""
    email = "notregistered@mergington.edu"
    activity = "Chess Club"
    
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()


def test_unregister_decreases_participant_count(client):
    """Test that unregister decreases the participant count"""
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()[activity]["participants"])
    
    # Unregister
    client.delete(
        f"/activities/{activity}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    
    # Get updated count
    response = client.get("/activities")
    updated_count = len(response.json()[activity]["participants"])
    
    assert updated_count == initial_count - 1


def test_unregister_one_participant_only(client):
    """Test that unregister only removes specified participant"""
    activity = "Basketball Team"
    remove_email = "james@mergington.edu"
    
    # Add another participant first
    other_email = "new@mergington.edu"
    client.post(
        f"/activities/{activity}/signup?email={other_email}",
        headers={"accept": "application/json"}
    )
    
    # Unregister one
    response = client.delete(
        f"/activities/{activity}/unregister?email={remove_email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Verify only that one was removed
    response = client.get("/activities")
    participants = response.json()[activity]["participants"]
    assert remove_email not in participants
    assert other_email in participants


def test_unregister_twice_fails(client):
    """Test that unregistering same person twice fails second time"""
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # First unregister
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Second unregister should fail
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 400
