from fastapi.testclient import TestClient


def signup(client: TestClient, email: str, password: str) -> str:
    return client.post("/api/v1/auth/signup", json={"email": email, "password": password}).json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_account(client: TestClient, token: str) -> int:
    return client.post("/api/v1/accounts", json={"type": "checking"}, headers=auth_headers(token)).json()["id"]


def test_issue_card_and_listing_without_sensitive_fields(client: TestClient):
    token = signup(client, "card_a@example.com", "pw")
    acc_id = create_account(client, token)

    payload = {
        "account_id": acc_id,
        "holder_name": "Card A",
        "exp_month": 12,
        "exp_year": 2030,
        "cvv": "123",
    }
    resp = client.post("/api/v1/cards", json=payload, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    for k in ["id", "brand", "holder_name", "last4", "card_token", "exp_month", "exp_year"]:
        assert k in data
    # Ensure cvv/cvv_hash are not present
    assert "cvv" not in data and "cvv_hash" not in data

    # Listing returns the issued card
    lst = client.get("/api/v1/cards", params={"account_id": acc_id}, headers=auth_headers(token)).json()
    assert len(lst) == 1
    assert lst[0]["id"] == data["id"]


def test_cards_ownership_enforced(client: TestClient):
    token_a = signup(client, "card_owner_a@example.com", "pw")
    token_b = signup(client, "card_owner_b@example.com", "pw")

    acc_a = create_account(client, token_a)

    # User B cannot list A's cards -> 404
    resp = client.get("/api/v1/cards", params={"account_id": acc_a}, headers=auth_headers(token_b))
    assert resp.status_code == 404
