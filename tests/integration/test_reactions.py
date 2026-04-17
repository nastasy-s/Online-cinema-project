import pytest
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User, UserGroup, UserGroupEnum
from src.movies.models import Certification, Movie, movie_genres, Genre
from src.core.security import hash_password


async def create_test_user(db: AsyncSession, email: str) -> User:
    result = await db.execute(
        __import__('sqlalchemy', fromlist=['select']).select(UserGroup).where(
            UserGroup.name == UserGroupEnum.USER
        )
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
    certification = Certification(name=f"Cert-{name}")
    db.add(certification)
    await db.flush()

    genre = Genre(name=f"Genre-{name}")
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


async def get_auth_token(client: AsyncClient, email: str) -> str:
    from src.auth.models import ActivationToken
    from sqlalchemy import select
    response = await client.post("/auth/login", json={
        "email": email,
        "password": "Test1234!",
    })
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_like_movie(client: AsyncClient, db_session: AsyncSession):
    user = await create_test_user(db_session, "like_user@test.com")
    movie = await create_test_movie(db_session, "Like Movie")

    login = await client.post("/auth/login", json={
        "email": "like_user@test.com",
        "password": "Test1234!",
    })
    token = login.json()["access_token"]

    response = await client.post(
        "/reactions/like",
        json={"movie_id": movie.id, "is_like": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["is_like"] is True


@pytest.mark.asyncio
async def test_get_movie_likes(client: AsyncClient, db_session: AsyncSession):
    movie = await create_test_movie(db_session, "Likes Count Movie")
    response = await client.get(f"/reactions/likes/{movie.id}")
    assert response.status_code == 200
    data = response.json()
    assert "likes" in data
    assert "dislikes" in data


@pytest.mark.asyncio
async def test_add_comment(client: AsyncClient, db_session: AsyncSession):
    user = await create_test_user(db_session, "comment_user@test.com")
    movie = await create_test_movie(db_session, "Comment Movie")

    login = await client.post("/auth/login", json={
        "email": "comment_user@test.com",
        "password": "Test1234!",
    })
    token = login.json()["access_token"]

    response = await client.post(
        "/reactions/comment",
        json={"movie_id": movie.id, "text": "Great movie!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["text"] == "Great movie!"


@pytest.mark.asyncio
async def test_get_comments(client: AsyncClient, db_session: AsyncSession):
    movie = await create_test_movie(db_session, "Get Comments Movie")
    response = await client.get(f"/reactions/comments/{movie.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_rate_movie(client: AsyncClient, db_session: AsyncSession):
    user = await create_test_user(db_session, "rate_user@test.com")
    movie = await create_test_movie(db_session, "Rate Movie")

    login = await client.post("/auth/login", json={
        "email": "rate_user@test.com",
        "password": "Test1234!",
    })
    token = login.json()["access_token"]

    response = await client.post(
        "/reactions/rate",
        json={"movie_id": movie.id, "rating": 8},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 8


@pytest.mark.asyncio
async def test_get_average_rating(client: AsyncClient, db_session: AsyncSession):
    movie = await create_test_movie(db_session, "Avg Rating Movie")
    response = await client.get(f"/reactions/rating/{movie.id}")
    assert response.status_code == 200
    assert "average_rating" in response.json()
