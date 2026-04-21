from fastapi import Depends, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import uuid

from src.db import get_db
from src.models import User
from src.api.auth.utils import decode_access_token

COOKIE_NAME = "access_token"


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    # extract token from cookie
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # decode and verify token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # get user from DB
    user_id = payload.get("sub")
    result = await db.exec(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ─── Role Guards ──────────────────────────────────────────────────────────────

async def require_candidate(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can access this"
        )
    return current_user


async def require_company(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "company":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only companies can access this"
        )
    return current_user