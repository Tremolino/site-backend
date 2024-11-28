from fastapi import FastAPI, Depends, HTTPException, status
from models import User, SessionLocal, init_db, Yacht
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
import security as security

from classes import UserCreate, UserLogin, Token, Yachts

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
    docs_url="/papers",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
init_db()
@yac.post("/reg", summary="Registration", tags=["users"])
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    em = db.query(User).filter(User.email == user_data.email).first()
    pn = db.query(User).filter(User.phone_num == user_data.phone_num).first()
    if user:
        raise HTTPException(status_code=400, detail="there is already such a user! try another username ( ͡° ͜ʖ ͡°)")
    if em:
        raise HTTPException(status_code=400, detail="there is already such an email! try another email ( ͡° ͜ʖ ͡°)")
    if pn:
        raise HTTPException(status_code=400, detail="there is there is already such an email! try another phone number ( ͡° ͜ʖ ͡°")

    hashed_password = security.hash_pass(user_data.password)

    new_user = User(username=user_data.username, phone_num=user_data.phone_num, email=user_data.email, hashed_password=hashed_password, realname=user_data.realname)
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

@yac.get("/yachts", response_model=List[Yachts], tags=["yachts"])
async def get_yachts(db: Session = Depends(get_db)):
    yachts = db.query(Yacht).all()
    return yachts