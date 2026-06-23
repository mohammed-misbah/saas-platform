from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role_id: int


class UserUpdate(BaseModel):
    email: EmailStr
    role_id: int

class UserResponse(BaseModel):
    id: int
    email: str
    role_id: int
    company_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True