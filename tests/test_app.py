"""
Test suite for Mergington High School API

Tests all endpoints with comprehensive coverage including:
- Happy path scenarios
- Error cases
- Edge cases
- Data isolation between tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the API."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities data to initial state before each test.
    This ensures test isolation for the in-memory database.
    """
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Learn swimming techniques and water safety",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in school concerts",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["liam@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore experiments and scientific discoveries",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["ava@mergington.edu", "lucas@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


# ==================== GET / Tests ====================

def test_root_redirect(client):
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# ==================== GET /activities Tests ====================

def test_get_activities_structure(client, reset_activities):
    """Test that activities endpoint returns proper structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # All activities present
    
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_get_activities_participant_counts(client, reset_activities):
    """Test that participant counts are accurate"""
    response = client.get("/activities")
    data = response.json()
    
    # Verify specific counts
    assert len(data["Chess Club"]["participants"]) == 2
    assert len(data["Programming Class"]["participants"]) == 2
    assert len(data["Gym Class"]["participants"]) == 2
    assert len(data["Basketball Team"]["participants"]) == 1
    assert len(data["Swimming Club"]["participants"]) == 2
    assert len(data["Art Studio"]["participants"]) == 1
    assert len(data["Music Band"]["participants"]) == 2
    assert len(data["Debate Team"]["participants"]) == 1
    assert len(data["Science Club"]["participants"]) == 2


def test_get_activities_data_integrity(client, reset_activities):
    """Test that activity data is not corrupted"""
    response = client.get("/activities")
    data = response.json()
    
    # Check specific known participants
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
    assert "emma@mergington.edu" in data["Programming Class"]["participants"]
    assert "alex@mergington.edu" in data["Basketball Team"]["participants"]


# ==================== POST /activities/{name}/signup Tests ====================

def test_signup_success(client, reset_activities):
    """Test successful signup to an activity"""
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_email(client, reset_activities):
    """Test that duplicate signup returns 400"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    
    # Second signup with same email
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signup to non-existent activity returns 404"""
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_empty_email(client, reset_activities):
    """Test signup with empty email"""
    response = client.post("/activities/Chess%20Club/signup?email=")
    assert response.status_code == 200  # Currently allows empty email
    
    # Verify empty email was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "" in activities_data["Chess Club"]["participants"]


def test_signup_special_characters_email(client, reset_activities):
    """Test signup with special characters in email"""
    response = client.post("/activities/Chess%20Club/signup?email=test+tag@mergington.edu")
    assert response.status_code == 200
    
    # Verify email was added (URL decoded: + becomes space)
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "test tag@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_case_sensitive_activity_name(client, reset_activities):
    """Test that activity names are case sensitive"""
    # Try with different case
    response = client.post("/activities/chess%20club/signup?email=test@mergington.edu")
    assert response.status_code == 404  # Should be case sensitive


def test_signup_case_sensitive_email(client, reset_activities):
    """Test that emails are case sensitive"""
    # Signup with lowercase
    client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    
    # Try signup with uppercase
    response = client.post("/activities/Chess%20Club/signup?email=TEST@mergington.edu")
    assert response.status_code == 200  # Currently allows case variants
    
    # Verify both were added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    participants = activities_data["Chess Club"]["participants"]
    assert "test@mergington.edu" in participants
    assert "TEST@mergington.edu" in participants


# ==================== DELETE /activities/{name}/participants Tests ====================

def test_remove_participant_success(client, reset_activities):
    """Test successful participant removal"""
    response = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "michael@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]  # Other remains


def test_remove_participant_nonexistent_activity(client, reset_activities):
    """Test removing from non-existent activity returns 404"""
    response = client.delete("/activities/NonExistent/participants?email=test@mergington.edu")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant_not_signed_up(client, reset_activities):
    """Test removing participant who is not signed up returns 404"""
    response = client.delete("/activities/Chess%20Club/participants?email=notsignedup@mergington.edu")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]


def test_remove_participant_case_sensitive_activity(client, reset_activities):
    """Test that activity names are case sensitive for removal"""
    response = client.delete("/activities/chess%20club/participants?email=michael@mergington.edu")
    assert response.status_code == 404  # Should be case sensitive


def test_remove_participant_case_sensitive_email(client, reset_activities):
    """Test that emails are case sensitive for removal"""
    # Add participant with mixed case
    client.post("/activities/Chess%20Club/signup?email=Test@mergington.edu")
    
    # Try to remove with different case
    response = client.delete("/activities/Chess%20Club/participants?email=test@mergington.edu")
    assert response.status_code == 404  # Currently case sensitive
    
    # Verify participant still exists
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "Test@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_remove_last_participant(client, reset_activities):
    """Test removing the last participant from an activity"""
    # Remove all participants from Basketball Team (has 1)
    response = client.delete("/activities/Basketball%20Team/participants?email=alex@mergington.edu")
    assert response.status_code == 200
    
    # Verify activity now has empty participants list
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert activities_data["Basketball Team"]["participants"] == []


# ==================== Integration Tests ====================

def test_signup_then_remove_workflow(client, reset_activities):
    """Test complete signup -> view -> remove workflow"""
    email = "workflow@mergington.edu"
    activity = "Programming Class"
    
    # Signup
    signup_response = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
    assert signup_response.status_code == 200
    
    # Verify in activities
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]
    
    # Remove
    remove_response = client.delete(f"/activities/{activity.replace(' ', '%20')}/participants?email={email}")
    assert remove_response.status_code == 200
    
    # Verify removed
    final_activities_response = client.get("/activities")
    final_activities_data = final_activities_response.json()
    assert email not in final_activities_data[activity]["participants"]