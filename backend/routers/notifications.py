from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_
from core.db import get_db
from middleware.auth import get_current_user_id
from models.notification import Notification
import uuid

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/")
async def get_my_notifications(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns all notifications for the logged-in user.
    """
    statement = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
    result = await db.execute(statement)
    return result.scalars().all()

@router.patch("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Marks a specific notification as read.
    """
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    notification.is_read = True
    db.add(notification)
    await db.commit()
    return {"message": "Notification marked as read"}
