"""CRUD operations for database models."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas, operations
from app.security import hash_password


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with hashed password."""
    hashed_password = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def create_calculation(
    db: Session,
    calc_in: schemas.CalculationCreate,
    user_id: Optional[int] = None
) -> models.Calculation:
    """
    Create a new calculation record.
    
    Args:
        db: Database session
        calc_in: Calculation input schema
        user_id: Optional user ID for ownership
        
    Returns:
        Created Calculation model instance
        
    Raises:
        ZeroDivisionError: If dividing by zero
        ValueError: If operation type is invalid
    """
    # Compute the result using operations module
    result = operations.compute(calc_in.a, calc_in.b, calc_in.type)
    
    # Create database record
    db_calculation = models.Calculation(
        a=calc_in.a,
        b=calc_in.b,
        type=calc_in.type,
        result=result,
        user_id=user_id
    )
    
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


def get_calculation(db: Session, calculation_id: int) -> Optional[models.Calculation]:
    """
    Get a calculation by ID.
    
    Args:
        db: Database session
        calculation_id: ID of the calculation
        
    Returns:
        Calculation model instance or None
    """
    return db.query(models.Calculation).filter(
        models.Calculation.id == calculation_id
    ).first()


def list_calculations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Calculation]:
    """
    List all calculations with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Calculation model instances
    """
    return db.query(models.Calculation).offset(skip).limit(limit).all()


def list_user_calculations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Calculation]:
    """
    List calculations for a specific user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Calculation model instances
    """
    return db.query(models.Calculation).filter(
        models.Calculation.user_id == user_id
    ).offset(skip).limit(limit).all()


def update_calculation(
    db: Session,
    calculation_id: int,
    calc_in: schemas.CalculationCreate
) -> Optional[models.Calculation]:
    """
    Update an existing calculation.
    
    Args:
        db: Database session
        calculation_id: ID of calculation to update
        calc_in: New calculation data
        
    Returns:
        Updated Calculation model instance or None if not found
        
    Raises:
        ZeroDivisionError: If dividing by zero
        ValueError: If operation type is invalid
    """
    # Get existing calculation
    db_calculation = get_calculation(db, calculation_id)
    if db_calculation is None:
        return None
    
    # Recompute result
    result = operations.compute(calc_in.a, calc_in.b, calc_in.type)
    
    # Update fields
    db_calculation.a = calc_in.a
    db_calculation.b = calc_in.b
    db_calculation.type = calc_in.type
    db_calculation.result = result
    
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


def delete_calculation(db: Session, calculation_id: int) -> bool:
    """
    Delete a calculation by ID.
    
    Args:
        db: Database session
        calculation_id: ID of calculation to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_calculation = get_calculation(db, calculation_id)
    if db_calculation is None:
        return False
    
    db.delete(db_calculation)
    db.commit()
    return True
