"""Integration tests for REST API endpoints."""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Test database setup
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_api_endpoints.db")


@pytest.fixture(scope="function")
def test_db_session():
    """Create a fresh test database for each test."""
    connect_args = {"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
    engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db_session):
    """Create a test client with overridden database."""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ========== USER ENDPOINT TESTS ==========

class TestUserEndpoints:
    """Test suite for user registration and login endpoints."""
    
    def test_register_new_user(self, client):
        """Test registering a new user."""
        response = client.post(
            "/users/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] == 1
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password
    
    def test_register_duplicate_email(self, client):
        """Test registering with existing email returns 400."""
        # Register first user
        client.post(
            "/users/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "pass123"
            }
        )
        
        # Try to register with same email
        response = client.post(
            "/users/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "pass456"
            }
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_duplicate_username(self, client):
        """Test registering with existing username returns 400."""
        # Register first user
        client.post(
            "/users/register",
            json={
                "email": "user1@example.com",
                "username": "sameusername",
                "password": "pass123"
            }
        )
        
        # Try to register with same username
        response = client.post(
            "/users/register",
            json={
                "email": "user2@example.com",
                "username": "sameusername",
                "password": "pass456"
            }
        )
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]
    
    def test_login_with_correct_credentials_email(self, client):
        """Test login with correct email and password."""
        # Register user
        client.post(
            "/users/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "mypassword"
            }
        )
        
        # Login with email
        response = client.post(
            "/users/login",
            json={
                "username_or_email": "login@example.com",
                "password": "mypassword"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert "user" in data
        assert data["user"]["email"] == "login@example.com"
        assert data["user"]["username"] == "loginuser"
    
    def test_login_with_correct_credentials_username(self, client):
        """Test login with correct username and password."""
        # Register user
        client.post(
            "/users/register",
            json={
                "email": "test@example.com",
                "username": "testusername",
                "password": "testpass"
            }
        )
        
        # Login with username
        response = client.post(
            "/users/login",
            json={
                "username_or_email": "testusername",
                "password": "testpass"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["username"] == "testusername"
    
    def test_login_with_wrong_password(self, client):
        """Test login with incorrect password returns 401."""
        # Register user
        client.post(
            "/users/register",
            json={
                "email": "wrong@example.com",
                "username": "wrongpass",
                "password": "correctpassword"
            }
        )
        
        # Try to login with wrong password
        response = client.post(
            "/users/login",
            json={
                "username_or_email": "wrong@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user returns 401."""
        response = client.post(
            "/users/login",
            json={
                "username_or_email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


# ========== CALCULATION ENDPOINT TESTS ==========

class TestCalculationEndpoints:
    """Test suite for calculation BREAD endpoints."""
    
    def test_post_calculation_success(self, client):
        """Test POST /calculations with valid data computes result correctly."""
        response = client.post(
            "/calculations/",
            json={"a": 15, "b": 5, "type": "Add"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["a"] == 15
        assert data["b"] == 5
        assert data["type"] == "Add"
        assert data["result"] == 20
        assert "id" in data
    
    def test_post_calculation_subtract(self, client):
        """Test subtraction calculation."""
        response = client.post(
            "/calculations/",
            json={"a": 20, "b": 8, "type": "Sub"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 12
    
    def test_post_calculation_multiply(self, client):
        """Test multiplication calculation."""
        response = client.post(
            "/calculations/",
            json={"a": 6, "b": 7, "type": "Multiply"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 42
    
    def test_post_calculation_divide(self, client):
        """Test division calculation."""
        response = client.post(
            "/calculations/",
            json={"a": 100, "b": 4, "type": "Divide"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 25
    
    def test_post_calculation_invalid_type(self, client):
        """Test POST with invalid operation type returns 422."""
        response = client.post(
            "/calculations/",
            json={"a": 10, "b": 5, "type": "Power"}
        )
        assert response.status_code == 422  # Pydantic validation error
    
    def test_post_calculation_division_by_zero(self, client):
        """Test POST with division by zero returns 400 validation error."""
        response = client.post(
            "/calculations/",
            json={"a": 10, "b": 0, "type": "Divide"}
        )
        assert response.status_code == 422  # Pydantic validation catches this
        assert "Division by zero" in str(response.json())
    
    def test_get_calculations_list(self, client):
        """Test GET /calculations returns list of calculations."""
        # Create some calculations
        client.post("/calculations/", json={"a": 5, "b": 3, "type": "Add"})
        client.post("/calculations/", json={"a": 10, "b": 2, "type": "Sub"})
        
        # Get list
        response = client.get("/calculations/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_get_calculation_by_id(self, client):
        """Test GET /calculations/{id} returns specific calculation."""
        # Create a calculation
        create_response = client.post(
            "/calculations/",
            json={"a": 12, "b": 4, "type": "Multiply"}
        )
        calc_id = create_response.json()["id"]
        
        # Get by ID
        response = client.get(f"/calculations/{calc_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == calc_id
        assert data["a"] == 12
        assert data["b"] == 4
        assert data["type"] == "Multiply"
        assert data["result"] == 48
    
    def test_get_calculation_not_found(self, client):
        """Test GET /calculations/{id} with non-existent id returns 404."""
        response = client.get("/calculations/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_put_calculation_update(self, client):
        """Test PUT /calculations/{id} updates and recomputes result."""
        # Create a calculation
        create_response = client.post(
            "/calculations/",
            json={"a": 10, "b": 5, "type": "Add"}
        )
        calc_id = create_response.json()["id"]
        assert create_response.json()["result"] == 15
        
        # Update it
        response = client.put(
            f"/calculations/{calc_id}",
            json={"a": 20, "b": 4, "type": "Multiply"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == calc_id
        assert data["a"] == 20
        assert data["b"] == 4
        assert data["type"] == "Multiply"
        assert data["result"] == 80  # Recomputed
    
    def test_put_calculation_not_found(self, client):
        """Test PUT /calculations/{id} with non-existent id returns 404."""
        response = client.put(
            "/calculations/99999",
            json={"a": 5, "b": 3, "type": "Add"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_put_calculation_division_by_zero(self, client):
        """Test PUT with division by zero returns validation error."""
        # Create a calculation
        create_response = client.post(
            "/calculations/",
            json={"a": 10, "b": 5, "type": "Add"}
        )
        calc_id = create_response.json()["id"]
        
        # Try to update with division by zero
        response = client.put(
            f"/calculations/{calc_id}",
            json={"a": 10, "b": 0, "type": "Divide"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_delete_calculation(self, client):
        """Test DELETE /calculations/{id} removes record and returns 204."""
        # Create a calculation
        create_response = client.post(
            "/calculations/",
            json={"a": 7, "b": 3, "type": "Add"}
        )
        calc_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/calculations/{calc_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/calculations/{calc_id}")
        assert get_response.status_code == 404
    
    def test_delete_calculation_not_found(self, client):
        """Test DELETE /calculations/{id} with non-existent id returns 404."""
        response = client.delete("/calculations/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_calculation_pagination(self, client):
        """Test GET /calculations with pagination parameters."""
        # Create multiple calculations
        for i in range(10):
            client.post("/calculations/", json={"a": i, "b": 1, "type": "Add"})
        
        # Test skip and limit
        response = client.get("/calculations/?skip=3&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


# ========== INTEGRATION TESTS ==========

class TestIntegrationFlow:
    """Test complete integration flows."""
    
    def test_full_calculation_lifecycle(self, client):
        """Test complete BREAD operations on a calculation."""
        # 1. Create (Add)
        create_response = client.post(
            "/calculations/",
            json={"a": 100, "b": 50, "type": "Add"}
        )
        assert create_response.status_code == 201
        calc_id = create_response.json()["id"]
        assert create_response.json()["result"] == 150
        
        # 2. Read (Get by ID)
        read_response = client.get(f"/calculations/{calc_id}")
        assert read_response.status_code == 200
        assert read_response.json()["result"] == 150
        
        # 3. Browse (List)
        list_response = client.get("/calculations/")
        assert list_response.status_code == 200
        assert any(calc["id"] == calc_id for calc in list_response.json())
        
        # 4. Edit (Update)
        update_response = client.put(
            f"/calculations/{calc_id}",
            json={"a": 10, "b": 5, "type": "Divide"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["result"] == 2
        
        # 5. Delete
        delete_response = client.delete(f"/calculations/{calc_id}")
        assert delete_response.status_code == 204
        
        # 6. Verify deletion
        verify_response = client.get(f"/calculations/{calc_id}")
        assert verify_response.status_code == 404
