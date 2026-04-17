from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.cart.schemas import AddToCartSchema, CartResponseSchema
from src.cart.service import cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get(
    "/",
    response_model=CartResponseSchema,
    summary="Get cart",
    description="Returns the current user's cart with all items.",
)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await cart_service.get_cart(db, current_user.id)


@router.post(
    "/",
    response_model=CartResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add movie to cart",
    description="Adds a movie to the current user's cart.",
)
async def add_to_cart(
    data: AddToCartSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await cart_service.add_to_cart(db, current_user.id, data.movie_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove movie from cart",
    description="Removes a specific movie from the current user's cart.",
)
async def remove_from_cart(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await cart_service.remove_from_cart(db, current_user.id, movie_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear cart",
    description="Removes all movies from the current user's cart.",
)
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await cart_service.clear_cart(db, current_user.id)
