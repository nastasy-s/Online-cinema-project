import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "newuser@gmail.com",
        "password": "Test1234!",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@gmail.com"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "duplicate@gmail.com",
        "password": "Test1234!",
    })
    response = await client.post("/auth/register", json={
        "email": "duplicate@gmail.com",
        "password": "Test1234!",
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "weak@gmail.com",
        "password": "123",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_activate_account_invalid_token(client: AsyncClient):
    response = await client.get("/auth/activate/invalid-token-123")
    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_not_active_user(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "inactive@gmail.com",
        "password": "Test1234!",
    })
    response = await client.post("/auth/login", json={
        "email": "inactive@gmail.com",
        "password": "Test1234!",
    })
    assert response.status_code == 401
    assert "not activated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post("/auth/login", json={
        "email": "newuser@gmail.com",
        "password": "WrongPass123!",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_resend_activation_invalid_email(client: AsyncClient):
    response = await client.post("/auth/resend-activation", json={
        "email": "notexist@gmail.com",
    })
    assert response.status_code == 400
