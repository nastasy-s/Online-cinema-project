from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import get_db
from src.core.dependencies import get_current_user, require_moderator
from src.movies.schemas import MovieCreateSchema, MovieResponseSchema
from src.movies.service import movie_service

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get(
    "/",
    response_model=List[MovieResponseSchema],
    summary="Get movies catalog",
    description="Returns paginated list of movies with optional filters and sorting.",
)
async def get_movies(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    year: Optional[int] = None,
    imdb: Optional[float] = None,
    search: Optional[str] = None,
    genre_id: Optional[int] = None,
    sort_by: Optional[str] = Query(None, enum=["price", "year", "imdb"]),
    db: AsyncSession = Depends(get_db),
):
    return await movie_service.get_movies(
        db=db,
        page=page,
        limit=limit,
        year=year,
        imdb=imdb,
        search=search,
        genre_id=genre_id,
        sort_by=sort_by,
    )


@router.get(
    "/{movie_id}",
    response_model=MovieResponseSchema,
    summary="Get movie by ID",
    description="Returns detailed information about a specific movie.",
)
async def get_movie_by_id(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/",
    response_model=MovieResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create movie",
    description="Moderator only. Creates a new movie in the catalog.",
)
async def create_movie(
    data: MovieCreateSchema,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_moderator),
):
    try:
        return await movie_service.create_movie(db=db, data=data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete movie",
    description="Moderator only. Deletes a movie from the catalog.",
)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_moderator),
):
    try:
        await movie_service.delete_movie(db=db, movie_id=movie_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
