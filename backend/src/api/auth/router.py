import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.db import get_db
from src.models import User, Candidate, Company
from src.api.auth.schemas import (
    RegisterCandidateRequest, RegisterCandidateResponse,
    RegisterCompanyRequest, RegisterCompanyResponse,
    LoginRequest, LoginResponse,
    UserResponse, CandidateProfileResponse, CompanyProfileResponse,
    MeResponse
)
from src.api.auth.utils import hash_password, verify_password, create_access_token
from src.api.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

COOKIE_NAME = "access_token"
COOKIE_SETTINGS = {
    "httponly": True,    # JS cannot read this cookie — prevents XSS
    "secure": False,     # set True in production (requires HTTPS)
    "samesite": "lax",   # prevents CSRF attacks
    "max_age": 86400     # 24 hours in seconds
}


# ─── Register Candidate ───────────────────────────────────────────────────────

@router.post("/register/candidate", response_model=RegisterCandidateResponse, status_code=status.HTTP_201_CREATED)
async def register_candidate(body: RegisterCandidateRequest, db: AsyncSession = Depends(get_db)):
    # check if email already exists
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    print(result)
    # create user
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        role="candidate"
    )

    db.add(user)
    await db.flush()   # flush to get user.id without committing yet

    # create candidate profile
    candidate = Candidate(
        user_id=user.id,
        full_name=body.full_name,
        phone=body.phone,
        linkedin_url=body.linkedin_url
    )
    db.add(candidate)
    await db.commit()
    await db.refresh(user)
    await db.refresh(candidate)

    return RegisterCandidateResponse(
        message="Candidate registered successfully",
        user=UserResponse.model_validate(user),
        profile=CandidateProfileResponse.model_validate(candidate)
    )


# ─── Register Company ─────────────────────────────────────────────────────────

@router.post("/register/company", response_model=RegisterCompanyResponse, status_code=status.HTTP_201_CREATED)
async def register_company(body: RegisterCompanyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    if result.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        role="company"
    )
    db.add(user)
    await db.flush()

    company = Company(
        user_id=user.id,
        name=body.name,
        industry=body.industry,
        website=body.website,
        description=body.description
    )
    db.add(company)
    await db.commit()
    await db.refresh(user)
    await db.refresh(company)

    return RegisterCompanyResponse(
        message="Company registered successfully",
        user=UserResponse.model_validate(user),
        profile=CompanyProfileResponse.model_validate(company)
    )


# ─── Login ────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    # find user by email
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalars().first()

    # deliberately same error for wrong email or wrong password
    # never tell the client which one was wrong — security best practice
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(user.id), user.role)

    # set token in httpOnly cookie
    response.set_cookie(key=COOKIE_NAME, value=token, **COOKIE_SETTINGS)

    return LoginResponse(
        message="Login successful",
        user=UserResponse.model_validate(user)
    )


# ─── Me (get current logged in user) ─────────────────────────────────────────

@router.get("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role == "candidate":
        result = await db.execute(select(Candidate).where(Candidate.user_id == current_user.id))
        profile = result.first()
        return MeResponse(
            user=UserResponse.model_validate(current_user),
            profile=CandidateProfileResponse.model_validate(profile)
        )
    else:
        result = await db.execute(select(Company).where(Company.user_id == current_user.id))
        profile = result.first()
        return MeResponse(
            user=UserResponse.model_validate(current_user),
            profile=CompanyProfileResponse.model_validate(profile)
        )


# ─── Logout ───────────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME)
    return {"message": "Logged out successfully"}