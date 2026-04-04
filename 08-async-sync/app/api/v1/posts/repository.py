from math import ceil
from typing import List, Optional, Tuple

from models import AuthorORM, PostORM, TagORM
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, selectinload

from .exceptions import PostConflictError, PostDatabaseError


class PostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:
        post_query = select(PostORM).where(PostORM.id == post_id)
        return self.db.execute(post_query).scalar_one_or_none()

    def search(
        self,
        query: Optional[str],
        order_by: str,
        direction: str,
        page: int,
        per_page: int,
    ) -> Tuple[int, int, int, List[PostORM]]:
        results = select(PostORM)

        if query:
            results = results.where(PostORM.title.ilike(f"%{query}%"))

        total = (
            self.db.scalar(select(func.count()).select_from(results.subquery())) or 0
        )

        if total == 0:
            return 0, 0, 1, []

        total_pages = ceil(total / per_page)
        current_page = min(page, total_pages)

        order_col = PostORM.id if order_by == "id" else func.lower(PostORM.title)

        results = results.order_by(
            order_col.asc() if direction == "asc" else order_col.desc()
        )

        offset = (current_page - 1) * per_page
        orm_posts = list(
            self.db.execute(results.limit(per_page).offset(offset)).scalars().all()
        )

        return total, total_pages, current_page, orm_posts

    def by_tags(self, tags: List[str]) -> List[PostORM]:

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

        return list(self.db.execute(post_list).scalars().all())

    def ensure_author(self, name: str, email: str) -> AuthorORM:
        # Valida existencia
        author_obj = self.db.execute(
            select(AuthorORM).where(AuthorORM.email == email)
        ).scalar_one_or_none()

        # Si existe lo retorna y corta la ejecución
        if author_obj:
            return author_obj

        # De lo contrario lo crea para retornarlo
        author_obj = AuthorORM(name=name, email=email)

        self.db.add(author_obj)
        self.db.flush()

        return author_obj

    def ensure_tag(self, name: str) -> TagORM:
        tag_obj = self.db.execute(
            select(TagORM).where(TagORM.name.ilike(name))
        ).scalar_one_or_none()

        if tag_obj:
            return tag_obj

        tag_obj = TagORM(name=name)
        self.db.add(tag_obj)
        self.db.flush()

        return tag_obj

    def create_post(
        self, title: str, content: str, author: Optional[dict], tags: List[dict]
    ) -> PostORM:
        try:
            author_obj = None

            if author:
                author_obj = self.ensure_author(author["username"], author["email"])

            post = PostORM(title=title, content=content, author=author_obj)

            for tag in tags:
                tag_obj = self.ensure_tag(tag["name"])
                post.tags.append(tag_obj)

            self.db.add(post)
            self.db.flush()
            self.db.refresh(post)

            return post
        except IntegrityError:
            self.db.rollback()
            raise PostConflictError()
        except SQLAlchemyError:
            self.db.rollback()
            raise PostDatabaseError()

    def update_post(self, post_id: int, payload: dict) -> Optional[PostORM]:
        post = self.get(post_id)

        if not post:
            return None

        try:
            for key, value in payload.items():
                setattr(post, key, value)

            self.db.commit()
            self.db.refresh(post)
            return post
        except SQLAlchemyError:
            self.db.rollback()
            raise PostDatabaseError()

    def delete_post(self, post_id) -> bool:
        post = self.get(post_id)

        if not post:
            return False

        try:
            self.db.delete(post)
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            raise PostDatabaseError()
