from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.movies.models import Movie, Genre, Director, Star, Certification


class MovieService:

    async def get_movies(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        year: Optional[int] = None,
        imdb: Optional[float] = None,
        search: Optional[str] = None,
        genre_id: Optional[int] = None,
        sort_by: Optional[str] = None,
    ) -> List[Movie]:
        query = select(Movie).options(
            selectinload(Movie.genres),
            selectinload(Movie.directors),
            selectinload(Movie.stars),
            selectinload(Movie.certification),
        )

        if year:
            query = query.where(Movie.year == year)
        if imdb:
            query = query.where(Movie.imdb >= imdb)
        if search:
            query = query.where(Movie.name.ilike(f"%{search}%"))
        if genre_id:
            query = query.where(Movie.genres.any(Genre.id == genre_id))

        if sort_by == "price":
            query = query.order_by(Movie.price)
        elif sort_by == "year":
            query = query.order_by(Movie.year.desc())
        elif sort_by == "imdb":
            query = query.order_by(Movie.imdb.desc())

        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_movie_by_id(
        self, db: AsyncSession, movie_id: int
    ) -> Movie:
        query = (
            select(Movie)
            .where(Movie.id == movie_id)
            .options(
                selectinload(Movie.genres),
                selectinload(Movie.directors),
                selectinload(Movie.stars),
                selectinload(Movie.certification),
            )
        )
        result = await db.execute(query)
        movie = result.scalar_one_or_none()
        if not movie:
            raise ValueError("Movie not found")
        return movie

    async def create_movie(
        self, db: AsyncSession, data
    ) -> Movie:
        result = await db.execute(
            select(Certification).where(
                Certification.id == data.certification_id
            )
        )
        certification = result.scalar_one_or_none()
        if not certification:
            raise ValueError("Certification not found")

        movie = Movie(
            name=data.name,
            year=data.year,
            time=data.time,
            imdb=data.imdb,
            votes=data.votes,
            description=data.description,
            price=data.price,
            certification_id=data.certification_id,
        )
        db.add(movie)
        await db.flush()

        if data.genre_ids:
            genres_result = await db.execute(
                select(Genre).where(Genre.id.in_(data.genre_ids))
            )
            movie.genres = list(genres_result.scalars().all())

        if data.director_ids:
            directors_result = await db.execute(
                select(Director).where(Director.id.in_(data.director_ids))
            )
            movie.directors = list(directors_result.scalars().all())

        if data.star_ids:
            stars_result = await db.execute(
                select(Star).where(Star.id.in_(data.star_ids))
            )
            movie.stars = list(stars_result.scalars().all())

        await db.commit()

        result = await db.execute(
            select(Movie)
            .where(Movie.id == movie.id)
            .options(
                selectinload(Movie.genres),
                selectinload(Movie.directors),
                selectinload(Movie.stars),
                selectinload(Movie.certification),
            )
        )
        return result.scalar_one()

    async def delete_movie(
        self, db: AsyncSession, movie_id: int
    ) -> None:
        movie = await self.get_movie_by_id(db, movie_id)
        await db.delete(movie)
        await db.commit()


movie_service = MovieService()
