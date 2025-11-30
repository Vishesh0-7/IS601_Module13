"""Authentication routes for user registration and login."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app import crud, schemas
from app.database import get_db
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    JWT_EXPIRE_MINUTES
)
import logging

log = logging.getLogger("calculator.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and return a JWT access token.
    
    Args:
        user: User registration data (email, username, password)
        db: Database session
        
    Returns:
        Dictionary with access_token and token_type
        
    Raises:
        HTTPException 400: If user with email or username already exists
    """
    # Check if user with email already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        log.warning("Registration failed: email %s already exists", user.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if user with username already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        log.warning("Registration failed: username %s already exists", user.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    new_user = crud.create_user(db=db, user=user)
    log.info("User created: id=%s, email=%s, username=%s", new_user.id, new_user.email, new_user.username)
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=access_token_expires
    )
    
    log.info("JWT token generated for user_id=%s", new_user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return a JWT access token.
    
    Args:
        credentials: Login credentials (username_or_email and password)
        db: Database session
        
    Returns:
        Dictionary with access_token and token_type
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Try to find user by email or username
    user = crud.get_user_by_email(db, email=credentials.username_or_email)
    if not user:
        user = crud.get_user_by_username(db, username=credentials.username_or_email)
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        log.warning("Login failed for: %s", credentials.username_or_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        log.warning("Login attempt for inactive user: %s", credentials.username_or_email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    log.info("User logged in: id=%s, email=%s", user.id, user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
