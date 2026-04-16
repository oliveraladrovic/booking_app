from fastapi.testclient import TestClient


def test_post_user_success(client: TestClient):
    response = client.post(
        "/users/", json={"full_name": "Test User", "email": "test.user@example.com"}
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["full_name"] == "Test User"
    assert data["email"] == "test.user@example.com"
    assert data["is_active"] is True
    assert "created_at" in data
    assert isinstance(data["created_at"], str)


def test_post_user_duplicate_mail(client: TestClient):
    payload = {"full_name": "Test User", "email": "test.user@example.com"}

    response1 = client.post("/users/", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/users/", json=payload)
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
