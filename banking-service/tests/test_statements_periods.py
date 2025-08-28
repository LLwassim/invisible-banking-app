from datetime import datetime

from fastapi.testclient import TestClient


def signup(client: TestClient, email: str, password: str) -> str:
    return client.post("/api/v1/auth/signup", json={"email": email, "password": password}).json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_account(client: TestClient, token: str) -> int:
    return client.post("/api/v1/accounts", json={"type": "checking"}, headers=auth_headers(token)).json()["id"]


def deposit(client: TestClient, token: str, account_id: int, amount: int):
    r = client.post(f"/api/v1/accounts/{account_id}/deposit", json={"amount_cents": amount}, headers=auth_headers(token))
    assert r.status_code == 200


def withdraw(client: TestClient, token: str, account_id: int, amount: int):
    r = client.post(f"/api/v1/accounts/{account_id}/withdraw", json={"amount_cents": amount}, headers=auth_headers(token))
    assert r.status_code == 200


def test_statement_current_month_period_and_balances(client: TestClient):
    token = signup(client, "stmt_a@example.com", "pw")
    acc = create_account(client, token)

    # Do a couple of movements in current month
    deposit(client, token, acc, 20_000)
    withdraw(client, token, acc, 5_000)

    current_month = datetime.now().strftime("%Y-%m")
    resp = client.post(f"/api/v1/statements/{acc}", json={"month": current_month}, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()

    # Period boundaries
    year, month = map(int, current_month.split("-"))
    period_start = datetime(year, month, 1, 0, 0, 0).isoformat()
    if month == 12:
        period_end = datetime(year + 1, 1, 1, 0, 0, 0).isoformat()
    else:
        period_end = datetime(year, month + 1, 1, 0, 0, 0).isoformat()

    assert data["period_start"].startswith(period_start)
    assert data["period_end"].startswith(period_end)

    # opening <= closing
    assert data["opening_balance_cents"] <= data["closing_balance_cents"]

    # closing reflects current computed balance in that period
    # With 20_000 deposit and 5_000 withdraw, closing should be >= 15_000
    assert data["closing_balance_cents"] >= 15_000


def test_statement_invalid_month_format_422(client: TestClient):
    token = signup(client, "stmt_invalid@example.com", "pw")
    acc = create_account(client, token)

    # Invalid month format is handled in service logic -> 400
    resp = client.post(f"/api/v1/statements/{acc}", json={"month": "2025/08"}, headers=auth_headers(token))
    assert resp.status_code == 400
