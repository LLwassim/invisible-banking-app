from fastapi.testclient import TestClient


def signup(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/signup", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_account(client: TestClient, token: str, type_: str) -> dict:
    resp = client.post("/api/v1/accounts", json={"type": type_}, headers=auth_headers(token))
    assert resp.status_code == 200
    return resp.json()


def test_create_two_accounts_and_list(client: TestClient):
    token = signup(client, "acc_two@example.com", "pw")
    a1 = create_account(client, token, "checking")
    a2 = create_account(client, token, "savings")
    assert a1["balance_cents"] == 0 and a2["balance_cents"] == 0

    lst = client.get("/api/v1/accounts", headers=auth_headers(token)).json()
    ids = [acc["id"] for acc in lst]
    assert a1["id"] in ids and a2["id"] in ids


def test_deposit_withdraw_and_balances(client: TestClient):
    token = signup(client, "acc_balance@example.com", "pw")
    acc = create_account(client, token, "checking")

    resp = client.post(f"/api/v1/accounts/{acc['id']}/deposit", json={"amount_cents": 15000, "description": "init"}, headers=auth_headers(token))
    assert resp.status_code == 200

    resp = client.post(f"/api/v1/accounts/{acc['id']}/withdraw", json={"amount_cents": 5000, "description": "atm"}, headers=auth_headers(token))
    assert resp.status_code == 200

    lst = client.get("/api/v1/accounts", headers=auth_headers(token)).json()
    assert any(a["id"] == acc["id"] and a["balance_cents"] == 10000 for a in lst)


def test_reject_non_positive_amounts(client: TestClient):
    token = signup(client, "acc_nonpos@example.com", "pw")
    acc = create_account(client, token, "checking")

    for bad in [0, -1]:
        r1 = client.post(f"/api/v1/accounts/{acc['id']}/deposit", json={"amount_cents": bad}, headers=auth_headers(token))
        r2 = client.post(f"/api/v1/accounts/{acc['id']}/withdraw", json={"amount_cents": bad}, headers=auth_headers(token))
        assert r1.status_code == 400
        assert r2.status_code == 400


def test_withdraw_insufficient_funds(client: TestClient):
    token = signup(client, "acc_insufficient@example.com", "pw")
    acc = create_account(client, token, "checking")

    resp = client.post(f"/api/v1/accounts/{acc['id']}/withdraw", json={"amount_cents": 5000}, headers=auth_headers(token))
    assert resp.status_code == 400


def test_ownership_enforcement(client: TestClient):
    token_a = signup(client, "owner_a@example.com", "pw")
    token_b = signup(client, "owner_b@example.com", "pw")

    acc_a = create_account(client, token_a, "checking")

    # User B cannot list A's accounts via any path; listing is scoped to current user only
    # So create an account for B and ensure A's ID is not visible
    acc_b = create_account(client, token_b, "checking")
    lst_b = client.get("/api/v1/accounts", headers=auth_headers(token_b)).json()
    assert all(a["id"] != acc_a["id"] for a in lst_b)

    # User B cannot deposit/withdraw on A's account (404 expected)
    r1 = client.post(f"/api/v1/accounts/{acc_a['id']}/deposit", json={"amount_cents": 1000}, headers=auth_headers(token_b))
    r2 = client.post(f"/api/v1/accounts/{acc_a['id']}/withdraw", json={"amount_cents": 1000}, headers=auth_headers(token_b))
    assert r1.status_code == 404
    assert r2.status_code == 404
