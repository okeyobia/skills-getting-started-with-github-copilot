from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def _reset_activities_state(original_state: dict) -> None:
    activities.clear()
    activities.update(deepcopy(original_state))


class TestActivities:
    def setup_method(self) -> None:
        self._original_state = deepcopy(activities)

    def teardown_method(self) -> None:
        _reset_activities_state(self._original_state)

    def test_get_activities_returns_data(self) -> None:
        response = client.get("/activities")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data

    def test_signup_adds_participant(self) -> None:
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_rejects_duplicate(self) -> None:
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]

        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        assert response.status_code == 400

    def test_remove_participant(self) -> None:
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]

        response = client.delete(
            f"/activities/{activity_name}/participants", params={"email": email}
        )

        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_remove_participant_missing(self) -> None:
        activity_name = "Chess Club"
        email = "missing@mergington.edu"

        response = client.delete(
            f"/activities/{activity_name}/participants", params={"email": email}
        )

        assert response.status_code == 404
