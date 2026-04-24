from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class CandidateRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class CompanyRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    experience_years: Optional[int] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
