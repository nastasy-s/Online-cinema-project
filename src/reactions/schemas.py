from datetime import datetime
from pydantic import BaseModel, Field


class LikeSchema(BaseModel):
    movie_id: int
    is_like: bool


class LikeResponseSchema(BaseModel):
    id: int
    movie_id: int
    is_like: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreateSchema(BaseModel):
    movie_id: int
    text: str = Field(..., min_length=1, max_length=1000)
    parent_id: int | None = None


class CommentResponseSchema(BaseModel):
    id: int
    movie_id: int
    user_id: int
    text: str
    parent_id: int | None
    created_at: datetime
    replies: list["CommentResponseSchema"] = []

    model_config = {"from_attributes": True}


class RatingCreateSchema(BaseModel):
    movie_id: int
    rating: int = Field(..., ge=1, le=10)


class RatingResponseSchema(BaseModel):
    id: int
    movie_id: int
    rating: int
    created_at: datetime

    model_config = {"from_attributes": True}
