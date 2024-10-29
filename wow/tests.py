import pytest
from fastapi.testclient import TestClient
from main import yac
from models import create_connection

client = TestClient(yac)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    conn = create_connection()
    with conn:
        conn.execute("DELETE FROM bookings")
        conn.execute("DELETE FROM yachts")
        conn.execute("DELETE FROM users")
    yield

@pytest.fixture(scope="module")
def create_user():
    response = client.post("/register/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    return "testuser", "testpassword"

def test_register(create_user):
    username, password = create_user
    response = client.post("/register/", json={"username": username, "password": password})
    assert response.status_code == 400  # Пользователь уже существует

def test_login(create_user):
    username, password = create_user
    # Изменяем формат данных на application/x-www-form-urlencoded
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_add_yacht(create_user):
    username, password = create_user
    token_response = client.post("/token", data={"username": username, "password": password})
    access_token = token_response.json()["access_token"]

    response = client.post("/yachts/", json={"name": "Yacht A", "capacity": 10}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

def test_get_yachts():
    response = client.get("/yachts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Проверяем, что возвращается список

def test_book_yacht(create_user):
    username, password = create_user
    # Получаем токен для аутентификации
    token_response = client.post("/token", data={"username": username, "password": password})
    access_token = token_response.json()["access_token"]

    # Бронирование яхты (используем ID яхты, которую добавили ранее)
    response = client.post("/book/", json={"user_id": 1, "yacht_id": 1, "date": "2024-10-23"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

def test_my_bookings(create_user):
    username, password = create_user
    # Получаем токен для аутентификации
    token_response = client.post("/token", data={"username": username, "password": password})
    access_token = token_response.json()["access_token"]

    # Получаем свои бронирования
    response = client.get("/my_bookings/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Проверяем, что возвращается список

if __name__ == "__main__":
   pytest.main()
