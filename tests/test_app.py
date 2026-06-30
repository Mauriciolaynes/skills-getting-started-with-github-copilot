import sys
from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

# Add src directory to the import path so tests can import app.py directly.
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
sys.path.append(str(SRC_DIR))

import app as app_module  # noqa: E402

app = app_module.app
INITIAL_ACTIVITIES = deepcopy(app_module.activities)

client = TestClient(app)


def reset_activities() -> None:
    app_module.activities = deepcopy(INITIAL_ACTIVITIES)


def test_root_redirects_to_static_index():
    reset_activities()

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    reset_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    reset_activities()

    response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert "newstudent@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_already_signed_up_returns_400():
    reset_activities()

    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_nonexistent_activity_returns_404():
    reset_activities()

    response = client.post("/activities/Unknown/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_user():
    reset_activities()

    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    reset_activities()

    response = client.delete("/activities/Chess Club/participants/nonexistent@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_nonexistent_activity_returns_404():
    reset_activities()

    response = client.delete("/activities/Unknown/participants/student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
