#TODO add ajax requests for price

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, status, Header, Form
from models import User, SessionLocal, init_db, Yacht, Booking
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import timedelta
import security as security
from typing import List

from classes import UserCreate, UserLogin, Token, Yachts, BookingSchema, UserSchema

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
    {
        "name": "dev",
        "description": "methods for developers. dont use in production",
    }
]

yac = FastAPI(
    title="Booking Yacht API",
    description="Tremolino site API",
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
        raise HTTPException(status_code=400, detail="there is there is already such a phone number! try another phone number ( ͡° ͜ʖ ͡°) ")

    hashed_password = security.hash_pass(user_data.password)

    new_user = User(username=user_data.username,
                    phone_num=user_data.phone_num,
                    email=user_data.email,
                    hashed_password=hashed_password,
                    realname=user_data.realname)
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

@yac.get("/profile", response_model=UserSchema, tags=["users"])

async def get_user(db: Session = Depends(get_db), token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="missing access token")

    username = security.verify_token(token)
    user = db.query(User).filter(User.username == username).first()

    return user

@yac.delete("/del", tags=["users"])
async def delete_account(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=418, detail="we don't have any here! try registration or check /docs")

    if not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=403, detail="password is wrong!")
    db.delete(user)
    db.commit()
    return {"status_code": 200, "detail": "User deleted success (✖╭╮✖)"}



@yac.post("/book", tags=["bookings"])
async def create_booking(booking_data: BookingSchema, db: Session = Depends(get_db), token: str = Header(None)):

    if not token:
        raise HTTPException(status_code=401, detail="missing access token")

    username = security.verify_token(token)

    yacht = db.query(Yacht).filter(Yacht.id == booking_data.yacht_id).first()
    if not yacht:
        raise HTTPException(
            status_code=404,
            detail=f"yacht with ID {booking_data.yacht_id} not found"
        )

    if not yacht.available:
        raise HTTPException(
            status_code=400,
            detail="the selected yacht is not available for booking"
        )

    booking_price = yacht.price * booking_data.duration

    new_booking = Booking(
        event_date=booking_data.event_date,
        event_time=booking_data.event_time,
        yacht_id=booking_data.yacht_id,
        instructor_name=booking_data.instructor_name,
        username=username,
        contacts=booking_data.contacts,
        guests=booking_data.guests,
        duration=booking_data.duration,
        price=int(booking_price),
        comments=booking_data.comments
    )

    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="there was an error with your booking request. please check your sending data."
        )

    return JSONResponse(
        status_code=201,
        content={
            "message": "booking created",
            "booking_id": new_booking.id,
            "total_price": booking_price
        }
    )

@yac.delete("/cancel", tags=["bookings"])
async def cancel_booking(booking_id: int, db: Session = Depends(get_db), token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="access token not found")

    username = security.verify_token(token)

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=404,
            detail="booking not found"
        )

    db.delete(booking)
    db.commit()
    return {"status_code": 200,
            "booking_id": booking_id,
            "username": username,
            "detail": "booking deleted success (✖╭╮✖)"}






"""
developer methods
"""



@yac.get("/yachts", response_model=List[Yachts], tags=["dev"], summary="list of all yachts") #for developers, delete in prod
async def get_yachts(db: Session = Depends(get_db)):
    yachts = db.query(Yacht).all()
    return yachts

@yac.get("/bookings", response_model=List[BookingSchema], tags=["dev"], summary="list of all bookings") #for developers, delete in prod
async def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return bookings


@yac.get("/bookings/{username}", response_model=List[BookingSchema], tags=["dev"], summary="list of user bookings") #for developers, delete in prod
async def get_user_bookings(username: str, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.username == username).all()
    return bookings

@yac.put("/yachts/{yacht_id}", tags=["dev"], summary="update available yacht")
async def update_yacht(yacht_id: int, db: Session = Depends(get_db)):
    yacht = db.query(Yacht).filter(Yacht.id == yacht_id).first()
    if not yacht:
        raise HTTPException(
            status_code=404,
            detail=f"yacht with ID {yacht_id} not found"
        )
    yacht.available = not yacht.available
    db.commit()
    return yacht

