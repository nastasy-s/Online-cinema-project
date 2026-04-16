from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class DirectorSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class StarSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CertificationSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class MovieCreateSchema(BaseModel):
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    description: str
    price: Decimal
    certification_id: int
    genre_ids: List[int] = []
    director_ids: List[int] = []
    star_ids: List[int] = []


class MovieResponseSchema(BaseModel):
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
