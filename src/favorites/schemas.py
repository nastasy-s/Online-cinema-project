from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

from src.movies.schemas import CertificationSchema, GenreSchema, DirectorSchema, StarSchema


class FavoriteMovieSchema(BaseModel):
    id: int
    uuid: str
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    description: str
    price: Decimal
    certification: Optional[CertificationSchema] = None
    genres: List[GenreSchema] = []
    directors: List[DirectorSchema] = []
    stars: List[StarSchema] = []

    model_config = {"from_attributes": True}


class FavoriteResponseSchema(BaseModel):
    id: int
    movie_id: int
    created_at: datetime
    movie: FavoriteMovieSchema

    model_config = {"from_attributes": True}


class AddFavoriteSchema(BaseModel):
    movie_id: int
