from fastapi.testclient import TestClient


def signup(client: TestClient, email: str, password: str) -> str:
    return client.post("/api/v1/auth/signup", json={"email": email, "password": password}).json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_account(client: TestClient, token: str, type_: str = "checking") -> int:
    return client.post("/api/v1/accounts", json={"type": type_}, headers=auth_headers(token)).json()["id"]


def get_balances(client: TestClient, token: str) -> dict[int, int]:
    resp = client.get("/api/v1/accounts", headers=auth_headers(token)).json()
    return {a["id"]: a["balance_cents"] for a in resp}


def fund(client: TestClient, token: str, account_id: int, amount: int):
    r = client.post(f"/api/v1/accounts/{account_id}/deposit", json={"amount_cents": amount}, headers=auth_headers(token))
    assert r.status_code == 200


def test_transfer_success_and_invariants(client: TestClient):
    token = signup(client, "tf_inv@example.com", "pw")
    a1 = create_account(client, token)
    a2 = create_account(client, token)

    fund(client, token, a1, 10_000)
    before = get_balances(client, token)

    r = client.post(
        "/api/v1/transfers",
        json={"from_account_id": a1, "to_account_id": a2, "amount_cents": 2_500, "description": "t"},
        headers=auth_headers(token),
    )
    assert r.status_code == 200
    txs = r.json()
    assert len(txs) == 2
    types = [t["type"] for t in txs]
    assert types == ["transfer_out", "transfer_in"] or types == ["transfer_in", "transfer_out"]
    assert all(t["amount_cents"] == 2_500 for t in txs)

    after = get_balances(client, token)
    assert sum(before.values()) == sum(after.values())


def test_transfer_same_account_400(client: TestClient):
    token = signup(client, "tf_same@example.com", "pw")
    a1 = create_account(client, token)
    fund(client, token, a1, 1_000)

    r = client.post(
        "/api/v1/transfers",
        json={"from_account_id": a1, "to_account_id": a1, "amount_cents": 100},
        headers=auth_headers(token),
    )
    assert r.status_code == 400


def test_transfer_insufficient_funds_400(client: TestClient):
    token = signup(client, "tf_insuf@example.com", "pw")
    a1 = create_account(client, token)
    a2 = create_account(client, token)

    r = client.post(
        "/api/v1/transfers",
        json={"from_account_id": a1, "to_account_id": a2, "amount_cents": 1000},
        headers=auth_headers(token),
    )
    assert r.status_code == 400


def test_transfer_non_positive_amount_400(client: TestClient):
    token = signup(client, "tf_nonpos@example.com", "pw")
    a1 = create_account(client, token)
    a2 = create_account(client, token)

    for bad in [0, -1]:
        r = client.post(
            "/api/v1/transfers",
            json={"from_account_id": a1, "to_account_id": a2, "amount_cents": bad},
            headers=auth_headers(token),
        )
        assert r.status_code == 400


def test_cross_user_cannot_transfer_from_others_source(client: TestClient):
    token_a = signup(client, "tf_user_a@example.com", "pw")
    token_b = signup(client, "tf_user_b@example.com", "pw")

    a1 = create_account(client, token_a)
    b1 = create_account(client, token_b)

    fund(client, token_a, a1, 5_000)

    # User B attempts transfer from A's account -> 404 (source account not found for B)
    r = client.post(
        "/api/v1/transfers",
        json={"from_account_id": a1, "to_account_id": b1, "amount_cents": 1000},
        headers=auth_headers(token_b),
    )
    assert r.status_code in (403, 404)
