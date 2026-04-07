import logging
from typing import Optional

from models import TagORM
from services.pagination import paginate_query
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import TagDatabaseError
from .schemas import TagPublic

logger = logging.getLogger("uvicorn.error")


class TagRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_tag(self, name: str) -> TagORM:
        normalize = name.strip().lower()

        tag_obj = (
            await self.db.execute(select(TagORM).where(TagORM.name == normalize))
        ).scalar_one_or_none()

        if tag_obj:
            return tag_obj

        try:
            tag_obj = TagORM(name=normalize)
            self.db.add(tag_obj)
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(tag_obj)
            return tag_obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error("Error al crear el tag '%s': %s", normalize, e)
            raise TagDatabaseError(str(e))

    async def list_tags(
        self,
        search: Optional[str],
        order_by: str = "id",
        direction: str = "id",
        page: int = 1,
        per_page: int = 10,
    ):
        query = select(TagORM)
        if search:
            query = query.where(func.lower(TagORM.name).ilike(f"%{search.lower()}%"))

        allowed_order = {"id": TagORM.id, "name": func.lower(TagORM.name)}

        total, total_pages, current_page, items = await paginate_query(
            db=self.db,
            model=TagORM,
            query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order,
        )

        # convierte cada TagORM a TagPublic (desacopla el ORM del schema de respuesta)
        tags = [TagPublic.model_validate(item) for item in items]

        return total, total_pages, current_page, tags
