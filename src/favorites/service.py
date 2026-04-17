from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.favorites.models import Favorite
from src.movies.models import Movie, Genre


class FavoritesService:

    async def add_favorite(
        self, db: AsyncSession, user_id: int, movie_id: int
    ) -> Favorite:
        result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.movie_id == movie_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Movie already in favorites")

        favorite = Favorite(user_id=user_id, movie_id=movie_id)
        db.add(favorite)
        await db.commit()

        result = await db.execute(
            select(Favorite)
            .where(Favorite.id == favorite.id)
            .options(
                selectinload(Favorite.movie).selectinload(Movie.genres),
                selectinload(Favorite.movie).selectinload(Movie.directors),
                selectinload(Favorite.movie).selectinload(Movie.stars),
                selectinload(Favorite.movie).selectinload(Movie.certification),
            )
        )
        return result.scalar_one()

    async def remove_favorite(
        self, db: AsyncSession, user_id: int, movie_id: int
    ) -> None:
        result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.movie_id == movie_id,
            )
        )
        favorite = result.scalar_one_or_none()
        if not favorite:
            raise ValueError("Movie not in favorites")

        await db.delete(favorite)
        await db.commit()

    async def get_favorites(
        self,
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        year: Optional[int] = None,
        imdb: Optional[float] = None,
        sort_by: Optional[str] = None,
    ) -> list[Favorite]:
        query = (
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .options(
                selectinload(Favorite.movie).selectinload(Movie.genres),
                selectinload(Favorite.movie).selectinload(Movie.directors),
                selectinload(Favorite.movie).selectinload(Movie.stars),
                selectinload(Favorite.movie).selectinload(Movie.certification),
            )
            .join(Movie, Favorite.movie_id == Movie.id)
        )

        if search:
            query = query.where(Movie.name.ilike(f"%{search}%"))
        if year:
            query = query.where(Movie.year == year)
        if imdb:
            query = query.where(Movie.imdb >= imdb)

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


favorites_service = FavoritesService()
