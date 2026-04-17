import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.movies.models import Certification, Genre, Movie, movie_genres


async def create_test_movie(db: AsyncSession, name: str = "Test Movie") -> Movie:
    certification = Certification(name=f"PG-{name}")
    db.add(certification)
    await db.flush()

    genre = Genre(name=f"Action-{name}")
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


@pytest.mark.asyncio
async def test_get_movies_empty(client: AsyncClient):
    response = await client.get("/movies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_movies_with_data(client: AsyncClient, db_session: AsyncSession):
    await create_test_movie(db_session, "Movie One")
    response = await client.get("/movies/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_movie_by_id(client: AsyncClient, db_session: AsyncSession):
    movie = await create_test_movie(db_session, "Movie Two")
    response = await client.get(f"/movies/{movie.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Movie Two"
    assert data["imdb"] == 8.5


@pytest.mark.asyncio
async def test_get_movie_not_found(client: AsyncClient):
    response = await client.get("/movies/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_movies_filter_by_year(client: AsyncClient, db_session: AsyncSession):
    await create_test_movie(db_session, "Movie Three")
    response = await client.get("/movies/?year=2023")
    assert response.status_code == 200
    data = response.json()
    assert all(m["year"] == 2023 for m in data)


@pytest.mark.asyncio
async def test_get_movies_filter_by_imdb(client: AsyncClient, db_session: AsyncSession):
    await create_test_movie(db_session, "Movie Four")
    response = await client.get("/movies/?imdb=8.0")
    assert response.status_code == 200
    data = response.json()
    assert all(m["imdb"] >= 8.0 for m in data)


@pytest.mark.asyncio
async def test_get_movies_pagination(client: AsyncClient):
    response = await client.get("/movies/?page=1&limit=5")
    assert response.status_code == 200
    assert len(response.json()) <= 5


@pytest.mark.asyncio
async def test_get_movies_sort_by_imdb(client: AsyncClient):
    response = await client.get("/movies/?sort_by=imdb")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_movies_search(client: AsyncClient, db_session: AsyncSession):
    await create_test_movie(db_session, "UniqueSearchMovie")
    response = await client.get("/movies/?search=UniqueSearch")
    assert response.status_code == 200
    data = response.json()
    assert any("UniqueSearch" in m["name"] for m in data)
