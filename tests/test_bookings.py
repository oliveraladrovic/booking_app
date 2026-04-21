from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

from booking_app.shared.enums import BookingStatus

USER = {"full_name": "Testuser 1", "email": "testuser1@test.com"}
SERVICE = {"name": "Test Service", "duration_minutes": 30}


def test_post_booking_success(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    response = client.post("/bookings/", json=booking)
    assert response.status_code == 201

    data = response.json()
    assert isinstance(data["id"], int)
    assert data["user_id"] == user_id
    assert data["service_id"] == service_id
    assert datetime.fromisoformat(data["start_time"]) == start
    assert datetime.fromisoformat(data["end_time"]) == start + timedelta(
        minutes=SERVICE["duration_minutes"]
    )
    assert data["status"] == BookingStatus.pending.value
    assert "notes" in data
    assert isinstance(data["created_at"], str)
    assert (
        datetime.fromisoformat(data["created_at"])
        <= datetime.fromisoformat(data["updated_at"])
        <= datetime.fromisoformat(data["created_at"]) + timedelta(seconds=1)
    )


def test_post_booking_user_not_found(client: TestClient):
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking = {
        "user_id": 999,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    response = client.post("/bookings/", json=booking)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_post_booking_service_not_found(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking = {
        "user_id": user_id,
        "service_id": 999,
        "start_time": start.isoformat(),
    }
    response = client.post("/bookings/", json=booking)
    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


def test_post_booking_time_in_past(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) - timedelta(minutes=10)
    booking = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    response = client.post("/bookings/", json=booking)
    assert response.status_code == 400
    assert response.json()["detail"] == "Start time can not be in past"


def test_post_booking_overlaping(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    response = client.post("/bookings/", json=booking)
    assert response.status_code == 201

    start2 = datetime.now(timezone.utc) + timedelta(minutes=20)
    booking2 = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start2.isoformat(),
    }
    response = client.post("/bookings/", json=booking2)
    assert response.status_code == 409
    assert response.json()["detail"] == "Time slot already occupied"
