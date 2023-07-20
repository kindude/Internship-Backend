from fastapi.testclient import TestClient
from app.main import app



import sys
import os

# Get the absolute path of the 'app' folder
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the 'app' folder to sys.path
sys.path.insert(0, app_path)

client = TestClient(app)

def test_create_user():
    # Test Create operation
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "city": "Test City",
        "country": "Test Country",
        "phone": "1234567890",
        "status": True,
        "roles": ["admin", "client"]
    }
    response = client.post("/create", json=payload)
    assert response.status_code == 200
    assert response.json().get("username") == payload["username"]
    assert response.json().get("email") == payload["email"]

def test_get_user():
    # Test Read operation (get_user)
    response = client.get("/users/3")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "testuser@example.com"


def test_update_user():
    # Test Update operation
    payload = {
        "username": "updateduser",
        "email": "updateduser@example.com"
    }
    response = client.put("/users/3", json=payload)
    assert response.status_code == 200
    assert response.json()["username"] == payload["username"]
    assert response.json()["email"] == payload["email"]

def test_delete_user():
    # Test Delete operation
    response = client.delete("/users/3")
    assert response.status_code == 200
    assert response.json() == {"msg": "User with id 1 deleted"}

def test_get_users_list():
    # Test Read operation (get_users_list)
    response = client.get("/all/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
