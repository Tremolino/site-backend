from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

DATABASE_URL = "sqlite:///./tremolino.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    realname = Column(String)
    phone_num = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Yacht(Base):
    __tablename__ = "yachts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True )
    capacity = Column(Integer, index=True)
    price = Column(Integer, index=True)
    yac_class = Column(String)
    available = Column(Boolean)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    date_of_booking = Column(DateTime, index=True, default=datetime.utcnow)
    event_date = Column(DateTime, index=True)
    event_time = Column(DateTime, index=True)
    yacht_id = Column(Integer, index=True)
    instructor_name = Column(String, index=True)
    username = Column(String, index=True)
    contacts = Column(String, index=True)
    guests = Column(Integer)
    price = Column(Integer)
    comments = Column(String, index=True, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)
