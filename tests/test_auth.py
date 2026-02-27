
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.session import engine, Base, get_db
from app.crud.user import create_user


client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  


def test_register_user(test_db):
    response = client.post("/register", json={"username": "testuser", "password": "123456"})
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    response_dup = client.post("/register", json={"username": "testuser", "password": "123456"})
    assert response_dup.status_code == 400


def test_login_user(test_db):
    create_user(test_db, "loginuser", "123456")

    response = client.post("/login", json={"username": "loginuser", "password": "123456"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)

    response_fail = client.post("/login", json={"username": "loginuser", "password": "wrongpass"})
    assert response_fail.status_code == 401


def test_profile_user(test_db):
    create_user(test_db, "profileuser", "123456")
    login_resp = client.post("/login", json={"username": "profileuser", "password": "123456"})
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    profile_resp = client.get("/profile", headers=headers)
    assert profile_resp.status_code == 200
    assert profile_resp.json()["username"] == "profileuser"