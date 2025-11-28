"""User authentication and management routes."""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.security import verify_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: User's email address (must be unique)
    - **username**: User's username (must be unique)
    - **password**: Plain text password (will be hashed)
    
    Raises:
        400: If email or username already exists
    """
    # Check if email already exists
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    return crud.create_user(db, user)


@router.post("/login")
def login_user(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user with username/email and password.
    
    - **username_or_email**: User's username or email
    - **password**: Plain text password
    
    Returns:
        Success message with user information
        
    Raises:
        401: If credentials are invalid
    """
    # Try to find user by email first, then by username
    user = crud.get_user_by_email(db, credentials.username_or_email)
    if not user:
        user = crud.get_user_by_username(db, credentials.username_or_email)
    
    # Check if user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }
