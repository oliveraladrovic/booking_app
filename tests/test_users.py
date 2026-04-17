from fastapi.testclient import TestClient

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
