import sqlite3
from sqlite3 import Error



def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('yacht_booking.db')
    except Error as e:
        print(e)
    return conn


class User:
    def __init__(self, username: str, password: str, email: str):
        self.username = username
        self.password = password
        self.email = email


class Yacht:
    def __init__(self, id: int, name: str, capacity: int):
        self.id = id
        self.name = name
        self.capacity = capacity


class Booking:
    def __init__(self, user_id: int, yacht_id: int, date: str):
        self.user_id = user_id
        self.yacht_id = yacht_id
        self.date = date


# Создание таблиц (если они не существуют)
def init_db():
    conn = create_connection()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS yachts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            capacity INTEGER NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS bookings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            yacht_id INTEGER NOT NULL,
                            date TEXT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users (id),
                            FOREIGN KEY (yacht_id) REFERENCES yachts (id))''')


init_db()


def add_user(username: str, password: str):
    conn = create_connection()
    with conn:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                     (username, password))


def get_user(username: str):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))

    return cursor.fetchone()


def add_yacht(name: str, capacity: int):
    conn = create_connection()
    with conn:
        conn.execute("INSERT INTO yachts (name, capacity) VALUES (?, ?)",
                     (name, capacity))


def get_yachts():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM yachts")

    return cursor.fetchall()


def book_yacht(user_id: int, yacht_id: int, date: str):
    conn = create_connection()
    with conn:
        conn.execute("INSERT INTO bookings (user_id, yacht_id, date) VALUES (?, ?, ?)",
                     (user_id, yacht_id, date))


def get_bookings(user_id: int):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings WHERE user_id=?", (user_id,))

    return cursor.fetchall()
