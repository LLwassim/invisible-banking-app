from fastapi.testclient import TestClient


def test_signup_login_flow(client: TestClient):
    """Test user signup and login happy path."""
    # Signup
    signup_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Login with same credentials
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_signup_duplicate_email(client: TestClient):
    """Test signup with duplicate email fails."""
    signup_data = {
        "email": "duplicate@example.com",
        "password": "testpassword"
    }
    
    # First signup should succeed
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 200
    
    # Second signup with same email should fail
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 400


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials fails."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
