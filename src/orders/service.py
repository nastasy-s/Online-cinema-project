from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.cart.models import Cart, CartItem
from src.movies.models import Movie
from src.orders.models import Order, OrderItem, OrderStatus


class OrderService:

    async def create_order(
        self, db: AsyncSession, user_id: int
    ) -> Order:
        result = await db.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.movie)
            )
        )
        cart = result.scalar_one_or_none()

        if not cart or not cart.items:
            raise ValueError("Cart is empty")

        total = sum(item.movie.price for item in cart.items)

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total,
        )
        db.add(order)
        await db.flush()

        for item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                movie_id=item.movie_id,
                price_at_order=item.movie.price,
            )
            db.add(order_item)

        for item in cart.items:
            await db.delete(item)

        await db.commit()

        result = await db.execute(
            select(Order)
            .where(Order.id == order.id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.movie)
            )
        )
        return result.scalar_one()

    async def get_user_orders(
        self, db: AsyncSession, user_id: int
    ) -> list[Order]:
        result = await db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.movie)
            )
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def cancel_order(
        self, db: AsyncSession, user_id: int, order_id: int
    ) -> Order:
        result = await db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise ValueError("Order not found")

        if order.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be canceled")

        order.status = OrderStatus.CANCELED
        await db.commit()

        result = await db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.movie)
            )
        )
        return result.scalar_one()


order_service = OrderService()
