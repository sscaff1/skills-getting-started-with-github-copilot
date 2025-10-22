import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Test structure of response
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test a specific activity structure
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_success():
    """Test successful activity signup"""
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify student was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_already_registered():
    """Test signup when student is already registered"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered in this activity
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_nonexistent_activity():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_success():
    """Test successful activity unregistration"""
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"  # Known to be registered
    
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    
    # Verify student was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_registered():
    """Test unregister when student is not registered"""
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()


def test_unregister_nonexistent_activity():
    """Test unregister from non-existent activity"""
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.parametrize("activity_name", [
    "Chess Club",
    "Programming Class",
    "Gym Class",
    "Soccer Team",
    "Basketball Club"
])
def test_activity_structure(activity_name):
    """Test the data structure of specific activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    activity = activities[activity_name]
    assert isinstance(activity["description"], str)
    assert isinstance(activity["schedule"], str)
    assert isinstance(activity["max_participants"], int)
    assert isinstance(activity["participants"], list)
    assert activity["max_participants"] > 0
    assert all(isinstance(p, str) for p in activity["participants"])