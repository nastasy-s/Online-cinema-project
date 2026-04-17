from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.favorites.schemas import AddFavoriteSchema, FavoriteResponseSchema
from src.favorites.service import favorites_service

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post(
    "/",
    response_model=FavoriteResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add movie to favorites",
    description="Adds a movie to the authenticated user's favorites list.",
)
async def add_favorite(
    data: AddFavoriteSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await favorites_service.add_favorite(db, current_user.id, data.movie_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove movie from favorites",
    description="Removes a movie from the authenticated user's favorites list.",
)
async def remove_favorite(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await favorites_service.remove_favorite(db, current_user.id, movie_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/",
    response_model=List[FavoriteResponseSchema],
    summary="Get favorites list",
    description="Returns the authenticated user's favorites with optional filters and sorting.",
)
async def get_favorites(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    year: Optional[int] = None,
    imdb: Optional[float] = None,
    sort_by: Optional[str] = Query(None, enum=["price", "year", "imdb"]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await favorites_service.get_favorites(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        year=year,
        imdb=imdb,
        sort_by=sort_by,
    )
