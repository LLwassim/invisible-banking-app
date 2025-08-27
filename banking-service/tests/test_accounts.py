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


def test_create_account(client: TestClient):
    """Test account creation."""
    headers = get_auth_header(client)
    
    account_data = {"type": "checking"}
    response = client.post("/api/v1/accounts", json=account_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "checking"
    assert data["balance_cents"] == 0
    assert "id" in data


def test_list_accounts(client: TestClient):
    """Test listing accounts."""
    headers = get_auth_header(client)
    
    # Create an account first
    account_data = {"type": "checking"}
    client.post("/api/v1/accounts", json=account_data, headers=headers)
    
    # List accounts
    response = client.get("/api/v1/accounts", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "checking"


def test_deposit_and_balance(client: TestClient):
    """Test deposit and balance update."""
    headers = get_auth_header(client)
    
    # Create account
    account_data = {"type": "checking"}
    response = client.post("/api/v1/accounts", json=account_data, headers=headers)
    account_id = response.json()["id"]
    
    # Deposit money
    deposit_data = {"amount_cents": 10000, "description": "Test deposit"}
    response = client.post(f"/api/v1/accounts/{account_id}/deposit", json=deposit_data, headers=headers)
    assert response.status_code == 200
    
    tx_data = response.json()
    assert tx_data["type"] == "deposit"
    assert tx_data["amount_cents"] == 10000
    
    # Check balance
    response = client.get("/api/v1/accounts", headers=headers)
    accounts = response.json()
    assert accounts[0]["balance_cents"] == 10000


def test_withdraw_insufficient_funds(client: TestClient):
    """Test withdrawal with insufficient funds fails."""
    headers = get_auth_header(client)
    
    # Create account
    account_data = {"type": "checking"}
    response = client.post("/api/v1/accounts", json=account_data, headers=headers)
    account_id = response.json()["id"]
    
    # Try to withdraw more than balance
    withdraw_data = {"amount_cents": 5000}
    response = client.post(f"/api/v1/accounts/{account_id}/withdraw", json=withdraw_data, headers=headers)
    assert response.status_code == 400
