from fastapi.testclient import TestClient


def get_auth_header(client: TestClient, email: str = None) -> dict:
    """Get authorization header for test user."""
    import uuid
    if email is None:
        email = f"testuser{uuid.uuid4().hex[:8]}@example.com"
    
    signup_data = {
        "email": email,
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/signup", json=signup_data)
    if response.status_code != 200:
        print(f"Signup failed: {response.status_code} - {response.text}")
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_transfer_between_accounts(client: TestClient):
    """Test transfer between two accounts."""
    import uuid
    # Create user A
    headers_a = get_auth_header(client, f"usera{uuid.uuid4().hex[:8]}@example.com")
    
    # Create user B
    headers_b = get_auth_header(client, f"userb{uuid.uuid4().hex[:8]}@example.com")
    
    # Create accounts for both users
    response = client.post("/api/v1/accounts", json={"type": "checking"}, headers=headers_a)
    account_a_id = response.json()["id"]
    
    response = client.post("/api/v1/accounts", json={"type": "checking"}, headers=headers_b)
    account_b_id = response.json()["id"]
    
    # Deposit money into account A
    deposit_data = {"amount_cents": 20000}
    client.post(f"/api/v1/accounts/{account_a_id}/deposit", json=deposit_data, headers=headers_a)
    
    # Transfer from A to B
    transfer_data = {
        "from_account_id": account_a_id,
        "to_account_id": account_b_id,
        "amount_cents": 5000,
        "description": "Test transfer"
    }
    response = client.post("/api/v1/transfers", json=transfer_data, headers=headers_a)
    assert response.status_code == 200
    
    # Response should contain both transactions
    transactions = response.json()
    assert len(transactions) == 2
    
    # Find transfer_out and transfer_in transactions
    transfer_out = next(tx for tx in transactions if tx["type"] == "transfer_out")
    transfer_in = next(tx for tx in transactions if tx["type"] == "transfer_in")
    
    assert transfer_out["amount_cents"] == 5000
    assert transfer_in["amount_cents"] == 5000
    
    # Check balances
    response = client.get("/api/v1/accounts", headers=headers_a)
    account_a_balance = response.json()[0]["balance_cents"]
    assert account_a_balance == 15000  # 20000 - 5000
    
    response = client.get("/api/v1/accounts", headers=headers_b)
    account_b_balance = response.json()[0]["balance_cents"]
    assert account_b_balance == 5000  # 0 + 5000


def test_transfer_insufficient_funds(client: TestClient):
    """Test transfer with insufficient funds fails."""
    headers = get_auth_header(client)
    
    # Create two accounts for same user
    response = client.post("/api/v1/accounts", json={"type": "checking"}, headers=headers)
    account1_id = response.json()["id"]
    
    response = client.post("/api/v1/accounts", json={"type": "savings"}, headers=headers)
    account2_id = response.json()["id"]
    
    # Try to transfer without sufficient funds
    transfer_data = {
        "from_account_id": account1_id,
        "to_account_id": account2_id,
        "amount_cents": 1000
    }
    response = client.post("/api/v1/transfers", json=transfer_data, headers=headers)
    assert response.status_code == 400


def test_transfer_same_account_fails(client: TestClient):
    """Test transfer to same account fails."""
    headers = get_auth_header(client)
    
    # Create account
    response = client.post("/api/v1/accounts", json={"type": "checking"}, headers=headers)
    account_id = response.json()["id"]
    
    # Try to transfer to same account
    transfer_data = {
        "from_account_id": account_id,
        "to_account_id": account_id,
        "amount_cents": 1000
    }
    response = client.post("/api/v1/transfers", json=transfer_data, headers=headers)
    assert response.status_code == 400
