from typing import TYPE_CHECKING, List

from core.db import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .post import PostORM


class TagORM(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)

    posts: Mapped[List["PostORM"]] = relationship(
        secondary="post_tags", back_populates="tags", lazy="selectin"
    )
