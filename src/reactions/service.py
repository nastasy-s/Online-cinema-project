from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.reactions.models import Comment, MovieLike, MovieRating
from src.reactions.schemas import CommentCreateSchema, LikeSchema, RatingCreateSchema


class ReactionsService:

    async def like_movie(
        self, db: AsyncSession, user_id: int, data: LikeSchema
    ) -> MovieLike:
        result = await db.execute(
            select(MovieLike).where(
                MovieLike.user_id == user_id,
                MovieLike.movie_id == data.movie_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.is_like = data.is_like
            await db.commit()
            await db.refresh(existing)
            return existing

        like = MovieLike(
            user_id=user_id,
            movie_id=data.movie_id,
            is_like=data.is_like,
        )
        db.add(like)
        await db.commit()
        await db.refresh(like)
        return like

    async def get_movie_likes(
        self, db: AsyncSession, movie_id: int
    ) -> dict:
        likes = await db.scalar(
            select(func.count()).where(
                MovieLike.movie_id == movie_id,
                MovieLike.is_like == True,
            )
        )
        dislikes = await db.scalar(
            select(func.count()).where(
                MovieLike.movie_id == movie_id,
                MovieLike.is_like == False,
            )
        )
        return {"likes": likes, "dislikes": dislikes}

    async def add_comment(
        self, db: AsyncSession, user_id: int, data: CommentCreateSchema
    ) -> Comment:
        comment = Comment(
            user_id=user_id,
            movie_id=data.movie_id,
            text=data.text,
            parent_id=data.parent_id,
        )
        db.add(comment)
        await db.commit()

        result = await db.execute(
            select(Comment)
            .where(Comment.id == comment.id)
            .options(selectinload(Comment.replies))
        )
        return result.scalar_one()

    async def get_movie_comments(
        self, db: AsyncSession, movie_id: int
    ) -> list[Comment]:
        result = await db.execute(
            select(Comment)
            .where(Comment.movie_id == movie_id, Comment.parent_id == None)
            .options(selectinload(Comment.replies))
        )
        return list(result.scalars().all())

    async def rate_movie(
        self, db: AsyncSession, user_id: int, data: RatingCreateSchema
    ) -> MovieRating:
        result = await db.execute(
            select(MovieRating).where(
                MovieRating.user_id == user_id,
                MovieRating.movie_id == data.movie_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.rating = data.rating
            await db.commit()
            await db.refresh(existing)
            return existing

        rating = MovieRating(
            user_id=user_id,
            movie_id=data.movie_id,
            rating=data.rating,
        )
        db.add(rating)
        await db.commit()
        await db.refresh(rating)
        return rating

    async def get_movie_average_rating(
        self, db: AsyncSession, movie_id: int
    ) -> dict:
        avg = await db.scalar(
            select(func.avg(MovieRating.rating)).where(
                MovieRating.movie_id == movie_id
            )
        )
        return {"average_rating": round(float(avg), 2) if avg else 0.0}


reactions_service = ReactionsService()
