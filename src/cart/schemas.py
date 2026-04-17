from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

from src.movies.schemas import CertificationSchema, GenreSchema


class CartMovieSchema(BaseModel):
    id: int
    name: str
    year: int
    price: Decimal
    certification: Optional[CertificationSchema] = None
    genres: List[GenreSchema] = []

    model_config = {"from_attributes": True}


class CartItemResponseSchema(BaseModel):
    id: int
    movie_id: int
    added_at: datetime
    movie: CartMovieSchema

    model_config = {"from_attributes": True}


class CartResponseSchema(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponseSchema] = []

    model_config = {"from_attributes": True}


class AddToCartSchema(BaseModel):
    movie_id: int
