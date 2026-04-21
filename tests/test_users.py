from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

FIRST_USER = {"full_name": "First User", "email": "first.user@example.com"}
SECOND_USER = {"full_name": "Second User", "email": "second.user@example.com"}


def test_post_user_success(client: TestClient):
    response = client.post("/users/", json=FIRST_USER)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["full_name"] == "First User"
    assert data["email"] == "first.user@example.com"
    assert data["is_active"] is True
    assert "created_at" in data
    assert isinstance(data["created_at"], str)


def test_post_user_duplicate_email(client: TestClient):
    response1 = client.post("/users/", json=FIRST_USER)
    assert response1.status_code == 201

    response2 = client.post("/users/", json=FIRST_USER)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Email already exists"


def test_post_user_invalid_email(client: TestClient):
    response = client.post(
        "/users/", json={"full_name": "Test User", "email": "test.user"}
    )
    assert response.status_code == 422


def test_post_user_missing_field(client: TestClient):
    response = client.post("/users/", json={"email": "test.user@example.com"})
    assert response.status_code == 422


def test_get_users_empty_list(client: TestClient):
    response = client.get("/users/")
    assert response.json() == []


def test_get_users_populated_list(client: TestClient):
    client.post("/users/", json=FIRST_USER)
    client.post("/users/", json=SECOND_USER)

    response = client.get("/users/")
    data = response.json()
    assert len(data) == 2


def test_get_user_success(client: TestClient):
    user = client.post("/users/", json=FIRST_USER)
    user_id = user.json()["id"]
    client.post("/users/", json=SECOND_USER)

    response = client.get(f"/users/{user_id}")
    data = response.json()
    assert data["id"] == user_id
    assert data["full_name"] == "First User"


def test_get_user_not_found(client: TestClient):
    client.post("/users/", json=FIRST_USER)
    client.post("/users/", json=SECOND_USER)

    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_patch_user_both_fields(client: TestClient):
    user = client.post("/users/", json=FIRST_USER)
    user_id = user.json()["id"]

    response = client.patch(f"/users/{user_id}", json=SECOND_USER)
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == SECOND_USER["full_name"]
    assert data["email"] == SECOND_USER["email"]


def test_patch_user_email_exists(client: TestClient):
    client.post("/users/", json=FIRST_USER)
    user = client.post("/users/", json=SECOND_USER)
    user_id = user.json()["id"]

    response = client.patch(f"/users/{user_id}", json=FIRST_USER)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"


def test_patch_user_full_name(client: TestClient):
    user = client.post("/users/", json=FIRST_USER)
    user_id = user.json()["id"]

    response = client.patch(f"/users/{user_id}", json={"full_name": "Second User"})
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == SECOND_USER["full_name"]
    assert data["email"] == FIRST_USER["email"]


def test_patch_user_email(client: TestClient):
    user = client.post("/users/", json=FIRST_USER)
    user_id = user.json()["id"]

    response = client.patch(
        f"/users/{user_id}", json={"email": "second.user@example.com"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == FIRST_USER["full_name"]
    assert data["email"] == SECOND_USER["email"]


def test_patch_user_same_email(client: TestClient):
    user = client.post("/users/", json=FIRST_USER)
    user_id = user.json()["id"]

    response = client.patch(
        f"/users/{user_id}",
        json={"full_name": "Second User", "email": "first.user@example.com"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == SECOND_USER["full_name"]
    assert data["email"] == FIRST_USER["email"]


def test_patch_user_not_found(client: TestClient):
    client.post("/users/", json=FIRST_USER)

    response = client.patch("/users/999", json=SECOND_USER)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_patch_user_empty_payload(client: TestClient):
    user = client.post("/users/", json=FIRST_USER)
    user_id = user.json()["id"]

    response = client.patch(f"/users/{user_id}", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == FIRST_USER["full_name"]
    assert data["email"] == FIRST_USER["email"]


def test_delete_user_success(client: TestClient):
    user = client.post("/users/", json=FIRST_USER)
    user_id = user.json()["id"]

    response1 = client.delete(f"/users/{user_id}")
    assert response1.status_code == 204

    response2 = client.get(f"/users/{user_id}")
    data = response2.json()
    assert data["full_name"] == "Deleted User"
    assert data["email"] == f"user{user_id}@deleted-user.com"
    assert data["is_active"] is False


def test_delete_user_not_found(client: TestClient):
    response = client.delete("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_users_by_service_and_date(client: TestClient):
    user1 = client.post("/users/", json=FIRST_USER)
    user1_id = user1.json()["id"]
    user2 = client.post("/users/", json=SECOND_USER)
    user2_id = user2.json()["id"]
    service1 = client.post(
        "/services/", json={"name": "Pregled", "duration_minutes": 15}
    )
    service1_id = service1.json()["id"]
    service2 = client.post(
        "/services/",
        json={
            "name": "Pjeskarenje",
            "description": "Čišćenje i poliranje zubi",
            "duration_minutes": 30,
        },
    )
    service2_id = service2.json()["id"]

    start1 = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking1_data = {
        "user_id": user1_id,
        "service_id": service1_id,
        "start_time": start1.isoformat(),
    }
    start2 = start1 + timedelta(days=2)
    booking2_data = {
        "user_id": user2_id,
        "service_id": service2_id,
        "start_time": start2.isoformat(),
    }
    start3 = start1 + timedelta(days=4)
    booking3_data = {
        "user_id": user2_id,
        "service_id": service2_id,
        "start_time": start3.isoformat(),
    }
    client.post("/bookings/", json=booking1_data)
    client.post("/bookings/", json=booking2_data)
    client.post("/bookings/", json=booking3_data)

    start_date = (start1 + timedelta(days=1)).date()
    end_date = (start1 + timedelta(days=3)).date()
    response = client.get(
        f"/users/?service_id={service2_id}&start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == user2_id
