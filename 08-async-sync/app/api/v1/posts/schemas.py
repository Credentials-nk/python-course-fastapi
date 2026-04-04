from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ============== Entidades =======================


class Tag(BaseModel):
    name: str = Field(..., min_length=3, max_length=30, description="Tag name")

    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str = Field(..., min_length=5, max_length=30, description="Author name")
    email: EmailStr = Field(..., description="Author email")

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)
    # author: Optional[Author] = None
    author: Author


class PostCreate(PostBase):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Title of Post(min 3 character, max 100)",
        examples=["Mi first post in FastAPI"],
    )
    content: str = Field(
        default="Content not available",
        min_length=10,
        description="Content example for Post",
        examples=["This an available content Post"],
    )
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("The title cannot contain the word: 'spam'")
        return value


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"] | None
    direction: Literal["asc", "desc"] | None
    search: str | None
    items: List[PostPublic]
