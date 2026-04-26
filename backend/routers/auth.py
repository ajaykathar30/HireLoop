from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.user import CandidateRegister, CompanyRegister, UserResponse, LoginRequest
from services.auth_service import signup_candidate, signup_company, authenticate_user, get_me
from middleware.auth import create_access_token, get_current_user_id
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup/candidate", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_candidate(
    schema: CandidateRegister,
    db: AsyncSession = Depends(get_db)
):
    return await signup_candidate(db, schema)

@router.post("/signup/company", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_company(
    schema: CompanyRegister,
    db: AsyncSession = Depends(get_db)
):
    return await signup_company(db, schema)

@router.post("/login")
async def login(
    response: Response,
    schema: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, schema)
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    # Set the cookie in the response
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=24 * 3600, # 24 hours
        samesite="none",
        secure=True, # Required for samesite="none"
    )
    
    return {"message": "Login successful", "role": user.role, "user": user}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.get("/me")
async def read_users_me(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_me(db, user_id)
