from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status
from models.user import User
from models.candidate import Candidate
from models.company import Company
from schemas.user import CandidateRegister, CompanyRegister, LoginRequest
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def signup_candidate(db: AsyncSession, schema: CandidateRegister):
    # Check if user already exists
    statement = select(User).where(User.email == schema.email)
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create User record
    new_user = User(
        email=schema.email,
        password_hash=get_password_hash(schema.password),
        role="candidate"
    )
    db.add(new_user)
    await db.flush() # To get the generated ID
    
    # Create Candidate record
    new_candidate = Candidate(
        user_id=new_user.id,
        full_name=schema.full_name
    )
    db.add(new_candidate)
    
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

async def signup_company(db: AsyncSession, schema: CompanyRegister):
    # Check if user already exists
    statement = select(User).where(User.email == schema.email)
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create User record
    new_user = User(
        email=schema.email,
        password_hash=get_password_hash(schema.password),
        role="company"
    )
    db.add(new_user)
    await db.flush() # To get the generated ID
    
    # Create Company record
    new_company = Company(
        user_id=new_user.id,
        name=schema.name
    )
    db.add(new_company)
    
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

async def authenticate_user(db: AsyncSession, schema: LoginRequest):
    statement = select(User).where(User.email == schema.email)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(schema.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_me(db: AsyncSession, user_id: uuid.UUID):
    # Get user
    statement = select(User).where(User.id == user_id)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_data = {}
    if user.role == "candidate":
        stmt = select(Candidate).where(Candidate.user_id == user_id)
        res = await db.execute(stmt)
        profile = res.scalar_one_or_none()
        profile_data = profile
    else:
        stmt = select(Company).where(Company.user_id == user_id)
        res = await db.execute(stmt)
        profile = res.scalar_one_or_none()
        profile_data = profile
        
    return {
        "user": user,
        "profile": profile_data
    }
