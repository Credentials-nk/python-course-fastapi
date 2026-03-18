import logging
import os
from datetime import datetime, timezone
from math import ceil
from typing import List, Literal, Optional, Union

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    func,
    select,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
    sessionmaker,
)

# ============== Config Database Connect =======================
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
logger = logging.getLogger("uvicorn.error")

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, echo=os.getenv("DB_ECHO", "false").lower() == "true", **engine_kwargs
)

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


# ============== Models =======================
class Base(DeclarativeBase):
    pass


post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class AuthorORM(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    posts: Mapped[List["PostORM"]] = relationship(back_populates="author")


class TagORM(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)

    posts: Mapped[List["PostORM"]] = relationship(
        secondary=post_tags, back_populates="tags", lazy="selectin"
    )


class PostORM(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Optional["AuthorORM"]] = relationship(back_populates="posts")

    tags: Mapped[List["TagORM"]] = relationship(
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",
        passive_deletes=True,
    )


Base.metadata.create_all(bind=engine)  # dev crea las tablas en caso que no exista


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


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
    author: Optional[Author] = None


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
    # limit: int
    # offset: int
    items: List[PostPublic]


# ============== APP de FastAPI =======================

app = FastAPI(title="Mini Blog")


@app.on_event("startup")
def on_startup():
    db_type = "PostgreSQL" if DATABASE_URL.startswith("postgresql") else "SQLite"
    db_name = DATABASE_URL.rsplit("/", 1)[-1]
    logger.info(
        "\n"
        "  ┌─────────────────────────────────────────┐\n"
        "  │         Base de datos conectada          │\n"
        "  ├─────────────────────────────────────────┤\n"
        "  │  Motor  : %s\n"
        "  │  Nombre : %s\n"
        "  └─────────────────────────────────────────┘",
        db_type,
        db_name,
    )


# ============== Router =======================


@app.get("/posts", response_model=PaginatedPost)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        description="Deprecated parameter use query instead",
        deprecated=True,
    ),
    query: Optional[str] = Query(
        default=None,
        description="Test for search by title",
        alias="search",
        min_length=3,
        max_length=10,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚÜü-]+$",
    ),
    per_page: int = Query(10, ge=1, le=50, description="Results of (1-50)"),
    page: int = Query(1, ge=1, description="Number of page (>=1)"),
    order_by: Literal["id", "title"] = Query("id", description="Input to order"),
    direction: Literal["asc", "desc"] = Query("asc", description="Order direction"),
    db: Session = Depends(get_db),
):
    results = select(PostORM)

    query = query or text

    if query:
        results = results.where(PostORM.title.ilike(f"%{query}%"))

    total = db.scalar(select(func.count()).select_from(results.subquery())) or 0
    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = min(page, total_pages) if total_pages > 0 else 1

    if order_by == "id":
        order_col = PostORM.id
    else:
        order_col = func.lower(PostORM.title)

    results = results.order_by(
        order_col.asc() if direction == "asc" else order_col.desc()
    )

    start = (current_page - 1) * per_page
    orm_posts = db.execute(results.limit(per_page).offset(start)).scalars().all()
    items = [PostPublic.model_validate(p) for p in orm_posts]

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=current_page > 1,
        has_next=current_page < total_pages,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items,
    )


@app.get(
    "/posts/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post found",
)
def get_post(
    post_id: int = Path(
        ...,
        ge=1,
        lt=4,
        title="ID Post",
        description="Identifier of Post. Should be gretter tan 1.",
        example=1,
    ),
    include_content: bool = Query(default=True, description="Flag to include content"),
    db: Session = Depends(get_db),
):
    post_query = select(PostORM).where(PostORM.id == post_id)
    post = db.execute(post_query).scalar_one_or_none()

    if post is None:
        return HTTPException(status_code=404, detail="Post not found")

    return (
        PostPublic.model_validate(post, from_attributes=True)
        if include_content
        else PostSummary.model_validate(post, from_attributes=True)
    )


@app.get("/post/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="One or more tags",
        example="Example: ?tags=python&tags=fastapi",
    ),
    db: Session = Depends(get_db),
):

    normalize_tag_names = [tag.strip().lower() for tag in tags if tag.strip()]

    if not normalize_tag_names:
        return []

    post_list = (
        select(PostORM)
        .options(selectinload(PostORM.tags), joinedload(PostORM.author))
        .join(PostORM.tags)
        .where(func.lower(TagORM.name).in_(normalize_tag_names))
        .distinct()
        .order_by(PostORM.id.asc())
    )

    posts = db.execute(post_list).scalars().all()

    return posts


@app.post(
    "/posts",
    response_model=PostPublic,
    response_description="Post Created",
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    author_obj = None

    if post.author:
        author_obj = db.execute(
            select(AuthorORM).where(AuthorORM.email == post.author.email)
        ).scalar_one_or_none()
        if not author_obj:
            author_obj = AuthorORM(name=post.author.name, email=post.author.email)

            db.add(author_obj)
            db.flush()

    new_post = PostORM(title=post.title, content=post.content, author=author_obj)

    for tag in post.tags or []:
        tag_obj = db.execute(
            select(TagORM).where(TagORM.name.ilike(tag.name))
        ).scalar_one_or_none()

        if not tag_obj:
            tag_obj = TagORM(name=tag.name)
            db.add(tag_obj)
            db.flush()

        new_post.tags.append(tag_obj)

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return new_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="A post with that title already exists"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")


@app.put(
    "/posts/{post_id}",
    response_model=PostPublic,
    response_description="Post Updated",
    response_model_exclude_none=True,
)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)

    if not db.get(PostORM, post_id):
        raise HTTPException(status_code=404, detail="Post not found")

    # Aplica solo los campos enviados en el request al objeto ORM
    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(post, key, value)

    try:
        db.commit()
        db.refresh(post)
        return post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el post")


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        db.delete(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el post")
