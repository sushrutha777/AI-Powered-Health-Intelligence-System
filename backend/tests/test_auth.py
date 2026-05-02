"""
Authentication endpoint tests.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient) -> None:
    """Test user registration."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Test duplicate email registration returns 409."""
    user_data = {
        "email": "dupe@example.com",
        "password": "securepassword123",
        "full_name": "Dupe User",
    }
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """Test successful login returns JWT."""
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "securepassword123",
        "full_name": "Login User",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "securepassword123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient) -> None:
    """Test login with wrong password returns 401."""
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "correctpassword",
        "full_name": "Wrong User",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient) -> None:
    """Test /me endpoint with valid token."""
    await client.post("/api/v1/auth/register", json={
        "email": "me@example.com",
        "password": "securepassword123",
        "full_name": "Me User",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "me@example.com",
        "password": "securepassword123",
    })
    token = login_resp.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient) -> None:
    """Test /me endpoint without token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
