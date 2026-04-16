import pytest


def test_get_activities(client):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Verify expected activities are returned
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    assert "Basketball Team" in activities
    assert "Soccer Club" in activities
    assert "Art Club" in activities
    assert "Drama Club" in activities
    assert "Debate Team" in activities
    assert "Science Club" in activities


def test_get_activities_count(client):
    """Test that GET /activities returns correct number of activities"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Should return exactly 9 activities
    assert len(activities) == 9


def test_get_activities_structure(client):
    """Test that activity objects have correct structure"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Check structure of an activity
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_get_activities_initial_participants(client):
    """Test that activities have correct initial participant data"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Verify specific participant data
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
    assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == 2
