def test_get_activities_returns_all_activities_with_participants(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_signup_adds_new_student(client):
    response = client.post(
        "/activities/Chess Club/signup", params={"email": "new@mergington.edu"}
    )

    assert response.status_code == 200
    assert "new@mergington.edu" in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_email(client):
    response = client.post(
        "/activities/Chess Club/signup", params={"email": "michael@mergington.edu"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_duplicate_with_different_case_and_whitespace(client):
    response = client.post(
        "/activities/Chess Club/signup", params={"email": "  MICHAEL@mergington.edu "}
    )

    assert response.status_code == 400
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert len(participants) == 2


def test_signup_unknown_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown/signup", params={"email": "new@mergington.edu"}
    )

    assert response.status_code == 404


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants", params={"email": "michael@mergington.edu"}
    )

    assert response.status_code == 200
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants == ["daniel@mergington.edu"]


def test_unregister_matches_email_case_insensitively(client):
    response = client.delete(
        "/activities/Chess Club/participants", params={"email": " Daniel@Mergington.edu "}
    )

    assert response.status_code == 200
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants == ["michael@mergington.edu"]


def test_unregister_student_not_signed_up_returns_404(client):
    response = client.delete(
        "/activities/Chess Club/participants", params={"email": "nobody@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete(
        "/activities/Unknown/participants", params={"email": "michael@mergington.edu"}
    )

    assert response.status_code == 404


def test_signup_then_unregister_allows_signing_up_again(client):
    client.delete(
        "/activities/Chess Club/participants", params={"email": "michael@mergington.edu"}
    )

    response = client.post(
        "/activities/Chess Club/signup", params={"email": "michael@mergington.edu"}
    )

    assert response.status_code == 200


def test_static_assets_are_served_with_no_cache(client):
    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache"
