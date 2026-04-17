from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.reactions.schemas import (
    CommentCreateSchema,
    CommentResponseSchema,
    LikeSchema,
    LikeResponseSchema,
    RatingCreateSchema,
    RatingResponseSchema,
)
from src.reactions.service import reactions_service

router = APIRouter(prefix="/reactions", tags=["Reactions"])


@router.post(
    "/like",
    response_model=LikeResponseSchema,
    summary="Like or dislike a movie",
    description="Authenticated user can like or dislike a movie.",
)
async def like_movie(
    data: LikeSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await reactions_service.like_movie(db, current_user.id, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/likes/{movie_id}",
    summary="Get movie likes count",
    description="Returns total likes and dislikes for a movie.",
)
async def get_movie_likes(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await reactions_service.get_movie_likes(db, movie_id)


@router.post(
    "/comment",
    response_model=CommentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add comment",
    description="Authenticated user can add a comment or reply to a comment.",
)
async def add_comment(
    data: CommentCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await reactions_service.add_comment(db, current_user.id, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/comments/{movie_id}",
    response_model=list[CommentResponseSchema],
    summary="Get movie comments",
    description="Returns all comments with replies for a movie.",
)
async def get_movie_comments(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await reactions_service.get_movie_comments(db, movie_id)


@router.post(
    "/rate",
    response_model=RatingResponseSchema,
    summary="Rate a movie",
    description="Authenticated user can rate a movie from 1 to 10.",
)
async def rate_movie(
    data: RatingCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await reactions_service.rate_movie(db, current_user.id, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/rating/{movie_id}",
    summary="Get movie average rating",
    description="Returns the average rating for a movie.",
)
async def get_movie_rating(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await reactions_service.get_movie_average_rating(db, movie_id)
