from datetime import datetime, time, date
from pydantic import BaseModel
from typing import List, Optional


class Token(BaseModel):
    access_token: str
    token_type: str
    realname: str

class UserCreate(BaseModel):
    realname: str
    phone_num: str
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Booking(BaseModel):
    event_date: date
    event_time: time
    yacht_id: int
    instructor_name: str
    contacts: str
    guests: str
    duration: int
    comments: Optional[str] = None



#for developers
class Yachts(BaseModel): #delete in prod
    name: str
    capacity: int
    price: int
    yac_class: str
    available: bool

class BookingSchema(BaseModel):
    yacht_id: int
    event_date: date
    event_time: time
    username: str
    # realname: str
    instructor_name: str
    contacts: str
    guests: int
    duration: int
    comments: Optional[str] = None

class Config:
    orm_mode = True