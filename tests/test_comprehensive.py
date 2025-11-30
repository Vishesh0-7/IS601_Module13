"""Comprehensive tests for 100% code coverage including all auth features."""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
from app.main import app
from app.database import Base, get_db
from app import crud, schemas, models
from app.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    verify_token,
    get_current_user,
    security
)
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

# Test database setup
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_100.db")


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    connect_args = {"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
    engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
    
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_user_and_token(client):
    """Create a user and return user info with auth token."""
    response = client.post("/auth/register", json={
        "email": "authuser@example.com",
        "username": "authuser",
        "password": "AuthPass123"
    })
    token = response.json()["access_token"]
    return {
        "token": token,
        "email": "authuser@example.com",
        "username": "authuser",
        "password": "AuthPass123"
    }


class TestSecurityFunctions:
    """Test security utility functions for 100% coverage."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert isinstance(hashed, str)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "CorrectPassword"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "CorrectPassword"
        hashed = hash_password(password)
        
        assert verify_password("WrongPassword", hashed) is False
    
    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        token = create_access_token(data={"sub": "123"})
        
        assert token is not None
        assert isinstance(token, str)
        
        payload = verify_token(token)
        assert payload["sub"] == "123"
        assert "exp" in payload
    
    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        custom_delta = timedelta(minutes=10)
        token = create_access_token(
            data={"sub": "456", "custom": "data"},
            expires_delta=custom_delta
        )
        
        payload = verify_token(token)
        assert payload["sub"] == "456"
        assert payload["custom"] == "data"
        assert "exp" in payload
    
    def test_verify_token_valid(self):
        """Test verifying a valid token."""
        token = create_access_token(data={"sub": "789"})
        payload = verify_token(token)
        
        assert payload["sub"] == "789"
    
    def test_verify_token_invalid(self):
        """Test verifying an invalid token raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid.token.string")
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    def test_verify_token_malformed(self):
        """Test verifying malformed token raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("not-a-jwt")
        
        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    """Test get_current_user dependency for 100% coverage."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, test_db):
        """Test get_current_user with valid token."""
        # Create a user
        user_data = schemas.UserCreate(
            email="currentuser@example.com",
            username="currentuser",
            password="TestPass123"
        )
        user = crud.create_user(test_db, user_data)
        
        # Create token for this user
        token = create_access_token(data={"sub": str(user.id)})
        
        # Create credentials object
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        # Test get_current_user
        retrieved_user = await get_current_user(credentials=credentials, db=test_db)
        
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
        assert retrieved_user.username == user.username
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, test_db):
        """Test get_current_user with invalid token raises exception."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=test_db)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_token_without_sub(self, test_db):
        """Test get_current_user with token missing 'sub' claim."""
        # Create token without 'sub'
        token = create_access_token(data={"other": "data"})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=test_db)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, test_db):
        """Test get_current_user with token for non-existent user."""
        # Create token for user ID that doesn't exist
        token = create_access_token(data={"sub": "99999"})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=test_db)
        
        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail


class TestAuthRoutes:
    """Test authentication routes for 100% coverage."""
    
    def test_register_success(self, client):
        """Test successful registration."""
        response = client.post("/auth/register", json={
            "email": "register@example.com",
            "username": "registeruser",
            "password": "RegisterPass123"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        client.post("/auth/register", json={
            "email": "dup@example.com",
            "username": "user1",
            "password": "Pass123"
        })
        
        response = client.post("/auth/register", json={
            "email": "dup@example.com",
            "username": "user2",
            "password": "Pass123"
        })
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username."""
        client.post("/auth/register", json={
            "email": "user1@example.com",
            "username": "dupuser",
            "password": "Pass123"
        })
        
        response = client.post("/auth/register", json={
            "email": "user2@example.com",
            "username": "dupuser",
            "password": "Pass123"
        })
        
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()
    
    def test_login_with_email_success(self, client):
        """Test successful login with email."""
        # Register first
        client.post("/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "LoginPass123"
        })
        
        # Login
        response = client.post("/auth/login", json={
            "username_or_email": "login@example.com",
            "password": "LoginPass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_with_username_success(self, client):
        """Test successful login with username."""
        client.post("/auth/register", json={
            "email": "login2@example.com",
            "username": "loginuser2",
            "password": "LoginPass123"
        })
        
        response = client.post("/auth/login", json={
            "username_or_email": "loginuser2",
            "password": "LoginPass123"
        })
        
        assert response.status_code == 200
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        client.post("/auth/register", json={
            "email": "wrongpw@example.com",
            "username": "wrongpwuser",
            "password": "CorrectPass123"
        })
        
        response = client.post("/auth/login", json={
            "username_or_email": "wrongpw@example.com",
            "password": "WrongPass123"
        })
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post("/auth/login", json={
            "username_or_email": "nonexistent@example.com",
            "password": "SomePass123"
        })
        
        assert response.status_code == 401
    
    def test_login_inactive_user(self, client, test_db):
        """Test login with inactive user."""
        # Create and deactivate user
        user_data = schemas.UserCreate(
            email="inactive@example.com",
            username="inactiveuser",
            password="Pass123"
        )
        user = crud.create_user(test_db, user_data)
        user.is_active = 0
        test_db.commit()
        
        # Try to login
        response = client.post("/auth/login", json={
            "username_or_email": "inactive@example.com",
            "password": "Pass123"
        })
        
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()


class TestMainApp:
    """Test main app routes and middleware."""
    
    def test_index_route(self, client):
        """Test index route returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_add_operation(self, client):
        """Test add operation endpoint."""
        response = client.get("/add?a=5&b=3")
        assert response.status_code == 200
        assert response.json()["result"] == 8
    
    def test_sub_operation(self, client):
        """Test subtract operation endpoint."""
        response = client.get("/sub?a=10&b=4")
        assert response.status_code == 200
        assert response.json()["result"] == 6
    
    def test_mul_operation(self, client):
        """Test multiply operation endpoint."""
        response = client.get("/mul?a=6&b=7")
        assert response.status_code == 200
        assert response.json()["result"] == 42
    
    def test_div_operation(self, client):
        """Test divide operation endpoint."""
        response = client.get("/div?a=20&b=4")
        assert response.status_code == 200
        assert response.json()["result"] == 5.0
    
    def test_div_by_zero(self, client):
        """Test divide by zero returns error."""
        response = client.get("/div?a=10&b=0")
        assert response.status_code == 400
        assert "division by zero" in response.json()["detail"].lower()
    
    def test_calc_endpoint_add(self, client):
        """Test calc endpoint with add operation."""
        response = client.get("/calc?op=add&a=5&b=3")
        assert response.status_code == 200
        data = response.json()
        assert data["op"] == "add"
        assert data["result"] == 8
    
    def test_calc_endpoint_invalid_op(self, client):
        """Test calc endpoint with invalid operation."""
        response = client.get("/calc?op=invalid&a=5&b=3")
        assert response.status_code == 400
        assert "unsupported" in response.json()["detail"].lower()
    
    def test_calc_endpoint_div_by_zero(self, client):
        """Test calc endpoint division by zero."""
        response = client.get("/calc?op=div&a=10&b=0")
        assert response.status_code == 400
    
    def test_create_calculation_via_main_endpoint(self, client):
        """Test creating calculation via main.py endpoint."""
        response = client.post("/calculations/", json={
            "a": 15,
            "b": 5,
            "type": "Add"
        })
        assert response.status_code == 201
        assert response.json()["result"] == 20
    
    def test_create_calculation_with_user_id(self, client, test_db):
        """Test creating calculation with user_id via main.py."""
        # Create user first
        user_data = schemas.UserCreate(
            email="maintest@example.com",
            username="maintest",
            password="Pass123"
        )
        user = crud.create_user(test_db, user_data)
        
        # Create calculation with user_id
        response = client.post(f"/calculations/?user_id={user.id}", json={
            "a": 10,
            "b": 2,
            "type": "Multiply"
        })
        assert response.status_code == 201
        assert response.json()["user_id"] == user.id
    
    def test_create_calculation_valueerror_via_main(self, client):
        """Test creating calculation with ValueError via main.py endpoint."""
        # This would require a scenario where ValueError is raised but not caught by schema
        # Division by zero is caught by schema, so this path may not be reachable
        # We'll try an edge case
        response = client.post("/calculations/", json={
            "a": 10,
            "b": 0,
            "type": "Divide"
        })
        # Schema should catch this before CRUD
        assert response.status_code in [400, 422]
    
    def test_list_calculations_via_main(self, client):
        """Test listing calculations via main.py endpoint."""
        response = client.get("/calculations/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_calculation_by_id_via_main(self, client):
        """Test getting calculation by ID via main.py endpoint."""
        # Create first
        create_resp = client.post("/calculations/", json={
            "a": 7,
            "b": 3,
            "type": "Sub"
        })
        calc_id = create_resp.json()["id"]
        
        # Get it
        response = client.get(f"/calculations/{calc_id}")
        assert response.status_code == 200
        assert response.json()["id"] == calc_id
    
    def test_get_nonexistent_calculation_via_main(self, client):
        """Test getting non-existent calculation via main.py."""
        response = client.get("/calculations/99999")
        assert response.status_code == 404
    



class TestCalculationRoutes:
    """Test calculation CRUD routes."""
    
    def test_create_calculation(self, client):
        """Test creating a calculation."""
        response = client.post("/calculations/", json={
            "a": 10,
            "b": 5,
            "type": "Add"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 15
        assert "id" in data
    
    def test_list_calculations(self, client):
        """Test listing calculations."""
        # Create some calculations
        client.post("/calculations/", json={"a": 5, "b": 3, "type": "Add"})
        client.post("/calculations/", json={"a": 10, "b": 2, "type": "Sub"})
        
        response = client.get("/calculations/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_get_calculation_by_id(self, client):
        """Test getting specific calculation."""
        # Create calculation
        create_response = client.post("/calculations/", json={
            "a": 7,
            "b": 3,
            "type": "Multiply"
        })
        calc_id = create_response.json()["id"]
        
        # Get it
        response = client.get(f"/calculations/{calc_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == calc_id
        assert data["result"] == 21
    
    def test_get_nonexistent_calculation(self, client):
        """Test getting non-existent calculation returns 404."""
        response = client.get("/calculations/99999")
        assert response.status_code == 404
    
    def test_update_calculation(self, client):
        """Test updating a calculation."""
        # Create
        create_response = client.post("/calculations/", json={
            "a": 10,
            "b": 5,
            "type": "Add"
        })
        calc_id = create_response.json()["id"]
        
        # Update
        response = client.put(f"/calculations/{calc_id}", json={
            "a": 10,
            "b": 5,
            "type": "Multiply"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 50
    
    def test_update_nonexistent_calculation(self, client):
        """Test updating non-existent calculation returns 404."""
        response = client.put("/calculations/99999", json={
            "a": 10,
            "b": 5,
            "type": "Add"
        })
        assert response.status_code == 404
    
    def test_update_calculation_with_error(self, client):
        """Test updating calculation with invalid operation."""
        # Create first
        create_response = client.post("/calculations/", json={
            "a": 10,
            "b": 5,
            "type": "Add"
        })
        calc_id = create_response.json()["id"]
        
        # Try to update with division by zero
        response = client.put(f"/calculations/{calc_id}", json={
            "a": 10,
            "b": 0,
            "type": "Divide"
        })
        assert response.status_code == 422  # Schema validation
    
    def test_delete_calculation(self, client):
        """Test deleting a calculation."""
        # Create
        create_response = client.post("/calculations/", json={
            "a": 8,
            "b": 2,
            "type": "Divide"
        })
        calc_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/calculations/{calc_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/calculations/{calc_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_calculation(self, client):
        """Test deleting non-existent calculation returns 404."""
        response = client.delete("/calculations/99999")
        assert response.status_code == 404


class TestUserRoutes:
    """Test user routes."""
    
    def test_register_user(self, client):
        """Test user registration via /users/register."""
        response = client.post("/users/register", json={
            "email": "userroute@example.com",
            "username": "userrouteuser",
            "password": "UserPass123"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "userroute@example.com"
        assert "id" in data
    
    def test_login_user(self, client):
        """Test user login via /users/login."""
        # Register
        client.post("/users/register", json={
            "email": "userlogin@example.com",
            "username": "userloginuser",
            "password": "UserPass123"
        })
        
        # Login
        response = client.post("/users/login", json={
            "username_or_email": "userlogin@example.com",
            "password": "UserPass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "token" in data or "success" in str(data).lower()
    
    def test_login_inactive_user_via_users_route(self, client, test_db):
        """Test login with inactive user via /users/login."""
        # Create and deactivate user
        user_data = schemas.UserCreate(
            email="inactiveroute@example.com",
            username="inactiveroute",
            password="Pass123"
        )
        user = crud.create_user(test_db, user_data)
        user.is_active = 0
        test_db.commit()
        
        # Try to login
        response = client.post("/users/login", json={
            "username_or_email": "inactiveroute@example.com",
            "password": "Pass123"
        })
        
        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()


class TestCRUDFunctions:
    """Test CRUD functions for complete coverage."""
    
    def test_update_calculation(self, test_db):
        """Test updating calculation via CRUD."""
        # Create
        calc_in = schemas.CalculationCreate(a=10, b=5, type="Add")
        calc = crud.create_calculation(test_db, calc_in)
        
        # Update
        update_in = schemas.CalculationCreate(a=10, b=5, type="Multiply")
        updated = crud.update_calculation(test_db, calc.id, update_in)
        
        assert updated.result == 50
        assert updated.type == "Multiply"
    
    def test_delete_calculation(self, test_db):
        """Test deleting calculation via CRUD."""
        # Create
        calc_in = schemas.CalculationCreate(a=8, b=2, type="Divide")
        calc = crud.create_calculation(test_db, calc_in)
        calc_id = calc.id
        
        # Delete
        result = crud.delete_calculation(test_db, calc_id)
        assert result is True
        
        # Verify deleted
        deleted_calc = crud.get_calculation(test_db, calc_id)
        assert deleted_calc is None
    
    def test_delete_nonexistent_calculation(self, test_db):
        """Test deleting non-existent calculation returns False."""
        result = crud.delete_calculation(test_db, 99999)
        assert result is False
    
    def test_list_user_calculations(self, test_db):
        """Test listing calculations for specific user."""
        # Create user
        user_data = schemas.UserCreate(
            email="listtest@example.com",
            username="listuser",
            password="Pass123"
        )
        user = crud.create_user(test_db, user_data)
        
        # Create calculations
        calc1 = schemas.CalculationCreate(a=5, b=3, type="Add")
        calc2 = schemas.CalculationCreate(a=10, b=2, type="Sub")
        
        crud.create_calculation(test_db, calc1, user_id=user.id)
        crud.create_calculation(test_db, calc2, user_id=user.id)
        
        # List user calculations
        calcs = crud.list_user_calculations(test_db, user.id)
        assert len(calcs) == 2


class TestModels:
    """Test model initialization for complete coverage."""
    
    def test_calculation_model_init_with_result(self):
        """Test Calculation model initialization with result provided."""
        calc = models.Calculation(a=10, b=5, type="Add", result=15)
        assert calc.result == 15
    
    def test_calculation_model_init_without_result(self):
        """Test Calculation model initialization computes result."""
        calc = models.Calculation(a=10, b=5, type="Add")
        assert calc.result == 15
    
    def test_calculation_model_with_user_id(self):
        """Test Calculation model with user_id."""
        calc = models.Calculation(a=10, b=5, type="Multiply", user_id=1)
        assert calc.user_id == 1
        assert calc.result == 50
