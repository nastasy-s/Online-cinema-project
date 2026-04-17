from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.cart.models import Cart, CartItem
from src.movies.models import Movie


class CartService:

    async def get_or_create_cart(
        self, db: AsyncSession, user_id: int
    ) -> Cart:
        result = await db.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.genres),
                selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.certification),
            )
        )
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.commit()
            await db.refresh(cart)

        return cart

    async def add_to_cart(
        self, db: AsyncSession, user_id: int, movie_id: int
    ) -> Cart:
        movie_result = await db.execute(
            select(Movie).where(Movie.id == movie_id)
        )
        movie = movie_result.scalar_one_or_none()
        if not movie:
            raise ValueError("Movie not found")

        cart = await self.get_or_create_cart(db, user_id)

        existing = await db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.movie_id == movie_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Movie already in cart")

        item = CartItem(cart_id=cart.id, movie_id=movie_id)
        db.add(item)
        await db.commit()

        return await self.get_cart(db, user_id)

    async def remove_from_cart(
        self, db: AsyncSession, user_id: int, movie_id: int
    ) -> None:
        cart = await self.get_or_create_cart(db, user_id)

        result = await db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.movie_id == movie_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError("Movie not in cart")

        await db.delete(item)
        await db.commit()

    async def clear_cart(
        self, db: AsyncSession, user_id: int
    ) -> None:
        cart = await self.get_or_create_cart(db, user_id)

        result = await db.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = result.scalars().all()
        for item in items:
            await db.delete(item)
        await db.commit()

    async def get_cart(
        self, db: AsyncSession, user_id: int
    ) -> Cart:
        result = await db.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.genres),
                selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.certification),
            )
        )
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.commit()

            result = await db.execute(
                select(Cart)
                .where(Cart.user_id == user_id)
                .options(
                    selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.genres),
                    selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.certification),
                )
            )
            cart = result.scalar_one()

        return cart

cart_service = CartService()
