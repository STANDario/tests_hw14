from datetime import datetime

from unittest.mock import MagicMock, patch, AsyncMock
import pytest

from src.database.models import User
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")}
    )
    data = response.json()
    return data["access_token"]


def test_create_contact(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())  # Треба щоб замокати fastapilimiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        birthday = datetime.now().isoformat().split("T")[0]
        response = client.post(
            "/api/contacts",
            json={"first_name": "username",
                  "surname": "surname",
                  "email": "test@example.com",
                  "phone_number": "380670000000",
                  "birthday": birthday
                  },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data


def test_get_contact_by_id(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data


def test_get_contact_by_email(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/?contact_email=test%40example.com",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["first_name"] == "username"


def test_get_contact_by_name(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/search_by_name?contact_name=username",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["email"] == "test@example.com"


def test_get_contact_by_surname(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/search_by_surname?contact_surname=surname",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["email"] == "test@example.com"


def test_get_contact_birthday(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/birthday",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["email"] == "test@example.com"


def test_get_contacts(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["first_name"] == "username"
        assert "id" in data[0]


def test_update_contact(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.put(
            "/api/contacts/1",
            json={
                "first_name": "another_username",
                "surname": "another_surname",
                "email": "user@example.com",
                "phone_number": "380671111111",
                "birthday": "2002-01-12"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == "user@example.com"


def test_remove_contact(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == "user@example.com"


def test_repeat_remove_contact(client, token, monkeypatch):
    with patch.object(auth_service, "r") as r_mock:
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Not found!"
