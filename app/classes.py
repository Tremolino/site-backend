from pydantic import BaseModel
from typing import List


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

class Yachts(BaseModel):
    name: str
    capacity: int
    price: int
    yac_class: str
    available: bool
