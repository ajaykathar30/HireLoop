from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Request, HTTPException, status
from core.config import settings
from uuid import UUID

import logging

logger = logging.getLogger(__name__)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def get_current_user_id(request: Request) -> UUID:
    token = request.cookies.get("access_token")
    if not token:
        logger.warning(f"No access_token cookie found in request to {request.url.path}")
        logger.debug(f"Available cookies: {request.cookies.keys()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated - Missing Cookie",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.error("Token payload missing 'sub' field")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token - Missing sub")
        return UUID(user_id)
    except JWTError as e:
        logger.error(f"JWT Decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token - {str(e)}")
