from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

PREGLED = {"name": "Pregled", "duration_minutes": 15}
PJESKARENJE = {
    "name": "Pjeskarenje",
    "description": "Čišćenje i poliranje zubi",
    "duration_minutes": 30,
}


def test_post_service_success(client: TestClient):
    response = client.post("/services/", json=PREGLED)
    assert response.status_code == 201

    data = response.json()
    assert isinstance(data["id"], int)
    assert data["name"] == "Pregled"
    assert data["description"] is None
    assert data["duration_minutes"] == 15
    assert data["is_active"]
    assert isinstance(data["created_at"], str)


def test_get_services_success(client: TestClient):
    client.post("/services/", json=PREGLED)
    client.post("/services/", json=PJESKARENJE)

    response = client.get("/services/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_services_by_user_and_date(client: TestClient):
    user1 = client.post(
        "/users/", json={"full_name": "First User", "email": "first.user@example.com"}
    )
    user1_id = user1.json()["id"]
    user2 = client.post(
        "/users/", json={"full_name": "Second User", "email": "second.user@example.com"}
    )
    user2_id = user2.json()["id"]
    service1 = client.post("/services/", json=PREGLED)
    service1_id = service1.json()["id"]
    service2 = client.post("/services/", json=PJESKARENJE)
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
        "service_id": service1_id,
        "start_time": start3.isoformat(),
    }
    client.post("/bookings/", json=booking1_data)
    client.post("/bookings/", json=booking2_data)
    client.post("/bookings/", json=booking3_data)

    start_date = start1 + timedelta(days=1)
    end_date = start1 + timedelta(days=3)
    response = client.get(
        f"/services/?user_id={user2_id}&start_date={start_date.replace(tzinfo=None).isoformat()}&end_date={end_date.replace(tzinfo=None).isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == service2_id


def test_get_service_success(client: TestClient):
    service = client.post("/services/", json=PREGLED)
    service_id = service.json()["id"]

    response = client.get(f"/services/{service_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == service_id
    assert data["is_active"]


def test_get_service_not_found(client: TestClient):
    client.post("/services/", json=PREGLED)

    response = client.get("/services/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


def test_patch_service_empty(client: TestClient):
    service = client.post("/services/", json=PREGLED)
    service_id = service.json()["id"]

    response = client.patch(f"/services/{service_id}", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == service_id
    assert data["name"] == PREGLED["name"]
    assert data["description"] is None
    assert data["duration_minutes"] == PREGLED["duration_minutes"]
    assert data["is_active"]
    assert data["created_at"] == service.json()["created_at"]


def test_patch_service_updates_is_active(client: TestClient):
    service = client.post("/services/", json=PREGLED)
    service_id = service.json()["id"]

    response = client.patch(f"/services/{service_id}", json={"is_active": False})
    assert response.status_code == 200
    assert not response.json()["is_active"]


def test_patch_service_updates_create_fields(client: TestClient):
    service = client.post("/services/", json=PREGLED)
    service_id = service.json()["id"]

    response = client.patch(f"/services/{service_id}", json=PJESKARENJE)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == PJESKARENJE["name"]
    assert data["description"] == PJESKARENJE["description"]
    assert data["duration_minutes"] == PJESKARENJE["duration_minutes"]
    assert data["is_active"]


def test_patch_service_not_found(client: TestClient):
    client.post("/services/", json=PREGLED)

    response = client.patch("/services/999", json={"is_active": False})
    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


def test_delete_service_success(client: TestClient):
    service = client.post("/services/", json=PREGLED)
    service_id = service.json()["id"]

    response = client.delete(f"/services/{service_id}")
    assert response.status_code == 204


def test_delete_service_already_deleted(client: TestClient):
    service = client.post("/services/", json=PREGLED)
    service_id = service.json()["id"]

    deactivated = client.patch(f"/services/{service_id}", json={"is_active": False})
    assert not deactivated.json()["is_active"]

    response = client.delete(f"/services/{service_id}")
    assert response.status_code == 204


def test_delete_service_not_found(client: TestClient):
    client.post("/services/", json=PREGLED)

    response = client.delete("/services/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"
