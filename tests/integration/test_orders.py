import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User, UserGroup, UserGroupEnum
from src.movies.models import Certification, Movie, Genre, movie_genres
from src.core.security import hash_password


async def create_test_user(db: AsyncSession, email: str) -> User:
    result = await db.execute(
        select(UserGroup).where(UserGroup.name == UserGroupEnum.USER)
    )
    group = result.scalar_one_or_none()
    user = User(
        email=email,
        hashed_password=hash_password("Test1234!"),
        is_active=True,
        group_id=group.id if group else None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_test_movie(db: AsyncSession, name: str = "Test Movie") -> Movie:
    certification = Certification(name=f"Cert-Order-{name}")
    db.add(certification)
    await db.flush()

    genre = Genre(name=f"Genre-Order-{name}")
    db.add(genre)
    await db.flush()

    movie = Movie(
        name=name,
        year=2023,
        time=120,
        imdb=8.5,
        votes=1000,
        description="Test description",
        price=9.99,
        certification_id=certification.id,
    )
    db.add(movie)
    await db.flush()

    await db.execute(
        insert(movie_genres).values(movie_id=movie.id, genre_id=genre.id)
    )
    await db.commit()
    return movie


async def login_user(client: AsyncClient, email: str) -> str:
    response = await client.post("/auth/login", json={
        "email": email,
        "password": "Test1234!",
    })
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, db_session: AsyncSession):
    await create_test_user(db_session, "order_user1@test.com")
    movie = await create_test_movie(db_session, "Order Movie 1")
    token = await login_user(client, "order_user1@test.com")

    await client.post(
        "/cart/",
        json={"movie_id": movie.id},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_create_order_empty_cart(client: AsyncClient, db_session: AsyncSession):
    await create_test_user(db_session, "order_user2@test.com")
    token = await login_user(client, "order_user2@test.com")

    response = await client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_orders(client: AsyncClient, db_session: AsyncSession):
    await create_test_user(db_session, "order_user3@test.com")
    movie = await create_test_movie(db_session, "Order Movie 2")
    token = await login_user(client, "order_user3@test.com")

    await client.post(
        "/cart/",
        json={"movie_id": movie.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_cancel_order(client: AsyncClient, db_session: AsyncSession):
    await create_test_user(db_session, "order_user4@test.com")
    movie = await create_test_movie(db_session, "Order Movie 3")
    token = await login_user(client, "order_user4@test.com")

    await client.post(
        "/cart/",
        json={"movie_id": movie.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    order_response = await client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"},
    )
    order_id = order_response.json()["id"]

    response = await client.post(
        f"/orders/{order_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "canceled"


@pytest.mark.asyncio
async def test_cancel_nonexistent_order(client: AsyncClient, db_session: AsyncSession):
    await create_test_user(db_session, "order_user5@test.com")
    token = await login_user(client, "order_user5@test.com")

    response = await client.post(
        "/orders/99999/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
