from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
import time

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


def test_confirm_booking_success(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    time.sleep(2)
    response = client.post(f"/bookings/{booking_id}/confirm")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == BookingStatus.confirmed.value
    assert (
        datetime.fromisoformat(data["created_at"]) + timedelta(seconds=1)
        < datetime.fromisoformat(data["updated_at"])
        < datetime.fromisoformat(data["created_at"]) + timedelta(seconds=3)
    )


def test_confirm_booking_not_found(client: TestClient):
    response = client.post("/bookings/999/confirm")
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_confirm_booking_invalid_status(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    confirmed = client.post(f"/bookings/{booking_id}/confirm")
    assert confirmed.status_code == 200

    response = client.post(f"/bookings/{booking_id}/confirm")
    assert response.status_code == 409
    assert response.json()["detail"] == "Only pending booking can be confirmed"


def test_confirm_booking_pending_exceeded(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(seconds=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    time.sleep(2)
    response = client.post(f"/bookings/{booking_id}/confirm")
    assert response.status_code == 400
    assert response.json()["detail"] == "Start time can not be in past"


def test_cancel_booking_pending_success(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    response = client.post(f"/bookings/{booking_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == BookingStatus.cancelled.value


def test_cancel_booking_canceled_unable(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    canceled = client.post(f"/bookings/{booking_id}/cancel")
    assert canceled.status_code == 200

    response = client.post(f"/bookings/{booking_id}/cancel")
    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Only pending and confirmed bookings can be canceled"
    )


def test_cancel_booking_confirmed_success(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    confirm = client.post(f"/bookings/{booking_id}/confirm")
    assert confirm.status_code == 200

    response = client.post(f"/bookings/{booking_id}/cancel")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == BookingStatus.cancelled.value


def test_cancel_booking_not_found(client: TestClient):
    response = client.post("/bookings/999/cancel")
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_complete_booking_pending_unable(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    response = client.post(f"/bookings/{booking_id}/complete")
    assert response.status_code == 409
    assert response.json()["detail"] == "Only confirmed bookings can be completed"


def test_complete_booking_canceled_unable(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    canceled = client.post(f"/bookings/{booking_id}/cancel")
    assert canceled.status_code == 200

    response = client.post(f"/bookings/{booking_id}/complete")
    assert response.status_code == 409
    assert response.json()["detail"] == "Only confirmed bookings can be completed"


def test_complete_booking_canfirmed_success(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    confirmed = client.post(f"/bookings/{booking_id}/confirm")
    assert confirmed.status_code == 200

    response = client.post(f"/bookings/{booking_id}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == BookingStatus.completed.value


def test_complete_booking_not_found(client: TestClient):
    response = client.post("/bookings/999/complete")
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_get_bookings_success(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    client.post("/bookings/", json=booking_data)

    response = client.get("/bookings/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_booking_success(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking_data = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start.isoformat(),
    }
    booking = client.post("/bookings/", json=booking_data)
    booking_id = booking.json()["id"]

    response = client.get(f"/bookings/{booking_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == booking_id
    assert data["status"] == BookingStatus.pending.value


def test_get_booking_not_found(client: TestClient):
    response = client.get("/bookings/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_patch_booking_notes_success(client: TestClient):
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
    booking = client.post("/bookings/", json=booking)
    booking_id = booking.json()["id"]
    assert booking.json()["notes"] is None

    response = client.patch(f"/bookings/{booking_id}", json={"notes": "Updated!"})
    assert response.status_code == 200
    assert response.json()["notes"] == "Updated!"


def test_patch_booking_start_time_success(client: TestClient):
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
    booking = client.post("/bookings/", json=booking)
    booking_id = booking.json()["id"]

    new_start = start + timedelta(minutes=1)
    response = client.patch(
        f"/bookings/{booking_id}", json={"start_time": new_start.isoformat()}
    )
    assert response.status_code == 200

    data = response.json()
    assert datetime.fromisoformat(data["start_time"]) > start + timedelta(seconds=30)


def test_patch_booking_no_update(client: TestClient):
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
    booking = client.post("/bookings/", json=booking)
    booking_id = booking.json()["id"]
    assert booking.json()["notes"] is None

    response = client.patch(f"/bookings/{booking_id}", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["notes"] is None
    assert datetime.fromisoformat(data["start_time"]) == start


def test_patch_booking_not_found(client: TestClient):
    response = client.patch("/bookings/999", json={})
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_patch_booking_time_in_past(client: TestClient):
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
    booking = client.post("/bookings/", json=booking)
    booking_id = booking.json()["id"]

    new_start = datetime.now(timezone.utc) - timedelta(minutes=10)
    response = client.patch(
        f"/bookings/{booking_id}", json={"start_time": new_start.isoformat()}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Start time can not be in past"


def test_patch_booking_overlaping(client: TestClient):
    user = client.post("/users/", json=USER)
    user_id = user.json()["id"]
    service = client.post("/services/", json=SERVICE)
    service_id = service.json()["id"]

    start1 = datetime.now(timezone.utc) + timedelta(minutes=1)
    booking1 = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start1.isoformat(),
    }
    booking1 = client.post("/bookings/", json=booking1)
    assert booking1.status_code == 201

    start2 = start1 + timedelta(minutes=35)
    booking2 = {
        "user_id": user_id,
        "service_id": service_id,
        "start_time": start2.isoformat(),
    }
    booking2 = client.post("/bookings/", json=booking2)
    assert booking2.status_code == 201
    booking2_id = booking2.json()["id"]

    new_start = start1 + timedelta(minutes=20)
    response = client.patch(
        f"/bookings/{booking2_id}", json={"start_time": new_start.isoformat()}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Time slot already occupied"
