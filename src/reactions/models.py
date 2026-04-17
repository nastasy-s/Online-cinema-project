from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class MovieLike(Base):
    __tablename__ = "movie_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_like"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id"), nullable=False)
    is_like: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comments.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    replies: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="parent"
    )
    parent: Mapped["Comment | None"] = relationship(
        "Comment", back_populates="replies", remote_side="Comment.id"
    )


class MovieRating(Base):
    __tablename__ = "movie_ratings"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_rating"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
