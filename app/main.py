from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, WebSocket, WebSocketDisconnect, Header, Query, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from models import User, SessionLocal, init_db, Base
from typing import List, Dict
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
import security as security
from datetime import datetime
import asyncio
import time

tags_metadata = [
    {
        "name": "users",
        "description": "Управление пользователями",
    },
    {
        "name": "yachts",
        "description": "Управление яхтами",
    },
    {
        "name": "bookings",
        "description": "Управление бронированием",
    },
]

yac = FastAPI(
    title="Booking Yacht API",
    description="Tremolino and Banderilya API",
    version="0.0.1",
    openapi_tags=tags_metadata,
    redoc_url=None,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
init_db()


class Token(BaseModel):
    access_token: str
    token_type: str
    realname: str

class UserCreate(BaseModel):
    realname: str
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@yac.post("/reg", summary="Registration", tags=["users"])
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    em = db.query(User).filter(User.email == user_data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="there is already such a user! try another username ( ͡° ͜ʖ ͡°)")
    if em:
        raise HTTPException(status_code=400, detail="there is already such an email! try another email ( ͡° ͜ʖ ͡°)")

    hashed_password = security.hash_pass(user_data.password)

    new_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_password, realname=user_data.realname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status_code": 200, "message": ".·´¯`·.´¯`·.¸¸.·´¯`·.¸><(((º> "}

@yac.post("/login", response_model=Token, tags=["users"])
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not security.verify_pass(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password or login is wrong!",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "realname": user.realname
    }




#
#
# @yac.get("/yachts/", response_model=List[Yacht], tags=["yachts"])
# async def list_yachts():
#     yachts_data = get_yachts()
#
#     return [{"id": yacht[0], "name": yacht[1], "capacity": yacht[2]} for yacht in yachts_data]
#
#
# @yac.post("/book/", tags=["bookings"])
# async def book_yacht(booking: Booking, current_user: str = Depends(get_current_user)):
#     book_yacht(booking.user_id, booking.yacht_id, booking.date)
#     return {"message": "Yacht booked successfully"}
#
#
# @yac.get("/my/", response_model=List[Booking], tags=["bookings"])
# async def users_bookings(current_user: str = Depends(get_current_user)):
#     user_id_query_result = get_user(current_user)
#
#     if not user_id_query_result:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     bookings_data = get_bookings(user_id_query_result[0])
#     return [{"user_id": booking[1], "yacht_id": booking[2], "date": booking[3]} for booking in bookings_data]
#