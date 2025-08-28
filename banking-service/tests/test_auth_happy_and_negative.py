from fastapi.testclient import TestClient


def signup(client: TestClient, email: str, password: str, full_name: str | None = None) -> str:
    payload = {"email": email, "password": password}
    if full_name is not None:
        payload["full_name"] = full_name
    resp = client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and data["token_type"] == "bearer"
    return data["access_token"]


def login(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and data["token_type"] == "bearer"
    return data["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_signup_and_login_return_tokens_and_me_works(client: TestClient):
    email = "auth_happy@example.com"
    pw = "pw123456"
    token = signup(client, email, pw, full_name="Auth Happy")
    token2 = login(client, email, pw)
    assert token and token2

    me = client.get("/api/v1/users/me", headers=auth_headers(token)).json()
    assert me["email"] == email
    assert "id" in me


def test_no_token_is_401(client: TestClient):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_garbage_token_is_401(client: TestClient):
    resp = client.get("/api/v1/users/me", headers=auth_headers("this.is.not.valid"))
    assert resp.status_code == 401


def test_wrong_password_401(client: TestClient):
    email = "auth_wrong_pw@example.com"
    signup(client, email, "correct")
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == 401


def test_email_resignup_400(client: TestClient):
    email = "auth_duplicate@example.com"
    signup(client, email, "pw1")
    resp = client.post("/api/v1/auth/signup", json={"email": email, "password": "pw1"})
    assert resp.status_code == 400
