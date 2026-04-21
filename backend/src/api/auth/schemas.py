import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr,Field


# ─── Request Schemas (what the client sends) ──────────────────────────────────

class RegisterCandidateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    full_name: str
    phone: str
    linkedin_url: str


class RegisterCompanyRequest(BaseModel):
    email: EmailStr
    password: str
    name: str                        # company name
    industry: str
    website: str
    description: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ─── Response Schemas (what the server sends back) ────────────────────────────

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    password_hash: str # just for testing (to be removed)
    created_at: datetime


class CandidateProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    created_at: datetime


class CompanyProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: Optional[str]
    industry: Optional[str]
    website: Optional[str]
    description: Optional[str]
    created_at: datetime


class RegisterCandidateResponse(BaseModel):
    message: str
    user: UserResponse
    profile: CandidateProfileResponse


class RegisterCompanyResponse(BaseModel):
    message: str
    user: UserResponse
    profile: CompanyProfileResponse


class LoginResponse(BaseModel):
    message: str
    user: UserResponse


class MeResponse(BaseModel):
    user: UserResponse
    profile: CandidateProfileResponse | CompanyProfileResponse