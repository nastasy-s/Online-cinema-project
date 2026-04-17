from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel

from src.orders.models import OrderStatus


class OrderMovieSchema(BaseModel):
    id: int
    name: str
    year: int
    price: Decimal

    model_config = {"from_attributes": True}


class OrderItemResponseSchema(BaseModel):
    id: int
    movie_id: int
    price_at_order: Decimal
    movie: OrderMovieSchema

    model_config = {"from_attributes": True}


class OrderResponseSchema(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal | None
    created_at: datetime
    items: List[OrderItemResponseSchema] = []

    model_config = {"from_attributes": True}
