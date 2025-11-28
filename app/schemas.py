"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import Optional, Literal


class CalculationCreate(BaseModel):
    """Schema for creating a new calculation."""
    a: float
    b: float
    type: Literal["Add", "Sub", "Multiply", "Divide"]
    # Note: Literal type provides validation, no need for additional validator

    @model_validator(mode='after')
    def validate_division_by_zero(self):
        """Prevent division by zero."""
        if self.type == "Divide" and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self


class CalculationRead(BaseModel):
    """Schema for reading a calculation from database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    a: float
    b: float
    type: str
    result: float
    user_id: Optional[int]


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: str
    username: str
    password: str


class UserRead(BaseModel):
    """Schema for reading user data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    username: str
    is_active: int


class UserLogin(BaseModel):
    """Schema for user login."""
    username_or_email: str
    password: str
