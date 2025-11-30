"""Calculation BREAD (Browse, Read, Edit, Add, Delete) routes."""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.get("/", response_model=List[schemas.CalculationRead])
def browse_calculations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Browse all calculations (list with pagination).
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100)
    """
    return crud.list_calculations(db, skip=skip, limit=limit)


@router.get("/{calculation_id}", response_model=schemas.CalculationRead)
def read_calculation(calculation_id: int, db: Session = Depends(get_db)):
    """
    Read a specific calculation by ID.
    
    - **calculation_id**: ID of the calculation to retrieve
    
    Raises:
        404: If calculation not found
    """
    calculation = crud.get_calculation(db, calculation_id)
    if calculation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    return calculation


@router.post("/", response_model=schemas.CalculationRead, status_code=status.HTTP_201_CREATED)
async def add_calculation(
    calculation: schemas.CalculationCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Add a new calculation.
    
    - **a**: First number
    - **b**: Second number
    - **type**: Operation type (Add, Sub, Multiply, Divide)
    
    If authenticated, automatically associates calculation with the logged-in user.
    
    Raises:
        400: If validation fails (e.g., division by zero)
        422: If invalid operation type
    """
    # Try to get user from Authorization header
    from app.security import verify_token
    
    user_id = None
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            user_id_str = payload.get("sub")  # JWT standard uses "sub" for subject (user ID)
            if user_id_str:
                user_id = int(user_id_str)
    except:
        pass
    
    try:
        return crud.create_calculation(db, calculation, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ZeroDivisionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{calculation_id}", response_model=schemas.CalculationRead)
def edit_calculation(
    calculation_id: int,
    calculation: schemas.CalculationCreate,
    db: Session = Depends(get_db)
):
    """
    Edit an existing calculation.
    
    Updates the calculation values and recomputes the result.
    
    - **calculation_id**: ID of the calculation to update
    - **a**: New first number
    - **b**: New second number
    - **type**: New operation type
    
    Raises:
        404: If calculation not found
        400: If validation fails (e.g., division by zero)
    """
    try:
        updated_calc = crud.update_calculation(db, calculation_id, calculation)
        if updated_calc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calculation not found"
            )
        return updated_calc
    except ValueError as e:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ZeroDivisionError as e:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calculation_id: int, db: Session = Depends(get_db)):
    """
    Delete a calculation by ID.
    
    - **calculation_id**: ID of the calculation to delete
    
    Raises:
        404: If calculation not found
    """
    success = crud.delete_calculation(db, calculation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    return None
