import pytest


def test_signup_then_unregister_lifecycle(client):
    """Test complete signup and unregister lifecycle"""
    email = "lifecycle@mergington.edu"
    activity = "Chess Club"
    
    # Initial state - not registered
    response = client.get("/activities")
    assert email not in response.json()[activity]["participants"]
    
    # Sign up
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Verify registered
    response = client.get("/activities")
    assert email in response.json()[activity]["participants"]
    
    # Unregister
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Verify unregistered
    response = client.get("/activities")
    assert email not in response.json()[activity]["participants"]


def test_multiple_participants_different_activities(client):
    """Test that multiple users can participate in different activities"""
    user1 = "user1@mergington.edu"
    user2 = "user2@mergington.edu"
    
    # User 1 signs up for Chess Club
    response = client.post(
        f"/activities/Chess Club/signup?email={user1}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # User 2 signs up for Programming Class
    response = client.post(
        f"/activities/Programming Class/signup?email={user2}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Verify both are registered in their respective activities
    response = client.get("/activities")
    activities = response.json()
    
    assert user1 in activities["Chess Club"]["participants"]
    assert user2 in activities["Programming Class"]["participants"]
    assert user1 not in activities["Programming Class"]["participants"]
    assert user2 not in activities["Chess Club"]["participants"]


def test_same_user_multiple_activities(client):
    """Test that same user can sign up for multiple activities"""
    email = "multiactivity@mergington.edu"
    
    # Sign up for Chess Club
    response = client.post(
        f"/activities/Chess Club/signup?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Sign up for Art Club
    response = client.post(
        f"/activities/Art Club/signup?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Verify registered in both
    response = client.get("/activities")
    activities = response.json()
    
    assert email in activities["Chess Club"]["participants"]
    assert email in activities["Art Club"]["participants"]


def test_signup_and_unregister_from_multiple_activities(client):
    """Test signing up and unregistering from multiple activities"""
    email = "multi@mergington.edu"
    activity1 = "Drama Club"
    activity2 = "Science Club"
    activity3 = "Debate Team"
    
    # Sign up for all three
    for activity in [activity1, activity2, activity3]:
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"accept": "application/json"}
        )
        assert response.status_code == 200
    
    # Verify registered in all
    response = client.get("/activities")
    activities = response.json()
    for activity in [activity1, activity2, activity3]:
        assert email in activities[activity]["participants"]
    
    # Unregister from middle activity
    response = client.delete(
        f"/activities/{activity2}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
    
    # Verify still registered in other two but not middle
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity1]["participants"]
    assert email not in activities[activity2]["participants"]
    assert email in activities[activity3]["participants"]


def test_concurrent_participant_tracking(client):
    """Test that participant counts remain consistent across operations"""
    # Get initial participant counts
    response = client.get("/activities")
    initial_activities = response.json()
    initial_chess_count = len(initial_activities["Chess Club"]["participants"])
    initial_drama_count = len(initial_activities["Drama Club"]["participants"])
    
    email1 = "concurrent1@mergington.edu"
    email2 = "concurrent2@mergington.edu"
    
    # Sign up both for Chess Club
    client.post(f"/activities/Chess Club/signup?email={email1}")
    client.post(f"/activities/Chess Club/signup?email={email2}")
    
    # Sign up email1 for Drama Club
    client.post(f"/activities/Drama Club/signup?email={email1}")
    
    # Unregister email1 from Chess Club
    client.delete(f"/activities/Chess Club/unregister?email={email1}")
    
    # Verify final counts
    response = client.get("/activities")
    final_activities = response.json()
    
    # Chess Club should have increased by 1 (email2 added, email1 removed = net +1)
    assert len(final_activities["Chess Club"]["participants"]) == initial_chess_count + 1
    # Drama Club should have increased by 1 (email1 added)
    assert len(final_activities["Drama Club"]["participants"]) == initial_drama_count + 1


def test_operations_preserve_other_participants(client):
    """Test that operations don't affect other participants"""
    activity = "Soccer Club"
    
    # Get initial participants
    response = client.get("/activities")
    initial_participants = set(response.json()[activity]["participants"])
    
    new_email = "newsoccer@mergington.edu"
    
    # Sign up new person
    client.post(f"/activities/{activity}/signup?email={new_email}")
    
    # Get participants after signup
    response = client.get("/activities")
    after_signup_participants = set(response.json()[activity]["participants"])
    
    # Original participants should still be there
    assert initial_participants.issubset(after_signup_participants)
    # Plus the new one
    assert new_email in after_signup_participants
    
    # Unregister the new person
    client.delete(f"/activities/{activity}/unregister?email={new_email}")
    
    # Get participants after unregister
    response = client.get("/activities")
    final_participants = set(response.json()[activity]["participants"])
    
    # Should be back to initial state
    assert final_participants == initial_participants
