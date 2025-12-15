from fastapi import APIRouter, Depends, HTTPException, status
from databases import Listings, users, get_db
from sqlalchemy.orm import Session
from models import UserResponse, ListingResponse
from routers.auth import get_current_user
from typing import List

router = APIRouter()

@router.get("/User_Listings")
async def read_users_me(current_user: users = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    user = db.query(users).filter(users.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    user_data = db.query(Listings).filter(Listings.owner == current_user.id).all()
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return { "user": UserResponse.from_orm(user), "user_data": [ListingResponse.from_orm(item) for item in user_data]}