from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import datetime
from starlette.middleware.cors import CORSMiddleware


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

from security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)

from models import (
    init_db,
    add_user,
    get_user,
    add_yacht,
    get_yachts,
    book_yacht,
    get_bookings,
)




origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

yac.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class User(BaseModel):
    username: str
    password: str


class Yacht(BaseModel):
    id: int
    name: str
    capacity: int


class Booking(BaseModel):
    user_id: int
    yacht_id: int
    date: str


class Token(BaseModel):
    access_token: str
    token_type: str


@yac.post("/register/", tags=["users"])
async def register(user: User):
    try:
        hashed_password = get_password_hash(user.password)
        add_user(user.username, hashed_password)
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Username already exists")


@yac.post("/token", response_model=Token, tags=["users"])
async def login(user: User):
    db_user = get_user(user.username)

    if not db_user or not verify_password(user.password, db_user[2]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = datetime.timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@yac.post("/yachts/", tags=["yachts"])
async def add_new_yacht(yacht: Yacht):
    add_yacht(yacht.name, yacht.capacity)
    return {"message": "Yacht added successfully"}


@yac.get("/yachts/", response_model=List[Yacht], tags=["yachts"])
async def list_yachts():
    yachts_data = get_yachts()

    return [{"id": yacht[0], "name": yacht[1], "capacity": yacht[2]} for yacht in yachts_data]


@yac.post("/book/", tags=["bookings"])
async def book_yacht_route(booking: Booking, current_user: str = Depends(get_current_user)):
    book_yacht(booking.user_id, booking.yacht_id, booking.date)
    return {"message": "Yacht booked successfully"}


@yac.get("/my_bookings/", response_model=List[Booking], tags=["bookings"])
async def my_bookings(current_user: str = Depends(get_current_user)):
    user_id_query_result = get_user(current_user)

    if not user_id_query_result:
        raise HTTPException(status_code=404, detail="User not found")

    bookings_data = get_bookings(user_id_query_result[0])
    return [{"user_id": booking[1], "yacht_id": booking[2], "date": booking[3]} for booking in bookings_data]


if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run(yac, host="127.0.0.1", port=8000)