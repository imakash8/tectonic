"""
Test authentication endpoints
"""

def test_register(client, db_session):
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        params={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "access_token" in data

def test_login(client, db_session):
    """Test user login"""
    # First register
    client.post(
        "/api/auth/register",
        params={
            "email": "login@example.com",
            "password": "testpass123"
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_health(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
