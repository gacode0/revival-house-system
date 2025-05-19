from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal
from pydantic_extra_types.phone_numbers import PhoneNumber

class DiscipleshipStatus(str, Enum):
    yes = "yes"
    no = "no"

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[PhoneNumber] = None
    has_taken_discipleship: DiscipleshipStatus
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[PhoneNumber] = None
    has_taken_discipleship: Optional[Literal["yes", "no"]] = None
    password: Optional[str] = Field(None, min_length=8)
    department: Optional[str] = None

class UserInDB(UserBase):
    id: str
    password_hash: str
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True