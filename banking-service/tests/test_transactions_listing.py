from fastapi.testclient import TestClient


def signup(client: TestClient, email: str, password: str) -> str:
    return client.post("/api/v1/auth/signup", json={"email": email, "password": password}).json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_account(client: TestClient, token: str, type_: str = "checking") -> int:
    return client.post("/api/v1/accounts", json={"type": type_}, headers=auth_headers(token)).json()["id"]


def test_transactions_newest_first_and_ownership(client: TestClient):
    token_a = signup(client, "tx_a@example.com", "pw")
    token_b = signup(client, "tx_b@example.com", "pw")

    acc_a = create_account(client, token_a)

    # Deposit then withdraw
    r1 = client.post(f"/api/v1/accounts/{acc_a}/deposit", json={"amount_cents": 1000, "description": "d1"}, headers=auth_headers(token_a))
    assert r1.status_code == 200
    r2 = client.post(f"/api/v1/accounts/{acc_a}/withdraw", json={"amount_cents": 300, "description": "w1"}, headers=auth_headers(token_a))
    assert r2.status_code == 200

    # List transactions for A, expect newest first (withdraw created after deposit)
    lst = client.get(f"/api/v1/transactions", params={"account_id": acc_a}, headers=auth_headers(token_a)).json()
    assert len(lst) == 2
    assert lst[0]["type"] == "withdraw"
    assert lst[1]["type"] == "deposit"

    # Ownership: user B cannot list A's transactions -> 404
    r_forbidden = client.get(f"/api/v1/transactions", params={"account_id": acc_a}, headers=auth_headers(token_b))
    assert r_forbidden.status_code == 404
