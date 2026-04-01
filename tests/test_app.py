import pytest
import copy
from fastapi.testclient import TestClient

from src.app import app, activities as activities_dict

# Create a deep copy of the initial activities for resetting
initial_activities = copy.deepcopy(activities_dict)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dictionary to initial state before each test."""
    activities_dict.clear()
    activities_dict.update(initial_activities)


@pytest.fixture
def client():
    """Create a TestClient instance for the FastAPI app."""
    return TestClient(app, follow_redirects=False)


def test_get_activities(client):
    """Test GET /activities endpoint returns all activities."""
    # Arrange - no special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Based on initial data
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    # Verify the email was added
    assert email in activities_dict[activity]["participants"]


def test_signup_activity_not_found(client):
    """Test signup for a non-existent activity."""
    # Arrange
    activity = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_already_signed_up(client):
    """Test signup when student is already signed up."""
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unsignup_success(client):
    """Test successful unregistration from an activity."""
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    # Verify the email was removed
    assert email not in activities_dict[activity]["participants"]


def test_unsignup_activity_not_found(client):
    """Test unregistration from a non-existent activity."""
    # Arrange
    activity = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unsignup_not_signed_up(client):
    """Test unregistration when student is not signed up."""
    # Arrange
    activity = "Chess Club"
    email = "notsignedup@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()


def test_root_redirect(client):
    """Test GET / redirects to static index.html."""
    # Arrange - no special setup

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"