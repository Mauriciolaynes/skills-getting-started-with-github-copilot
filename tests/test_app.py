from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_remove_participant_from_activity():
    activity_name = "Chess Club"
    email = "test.student@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    remove_response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )
    assert remove_response.status_code == 200

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]
