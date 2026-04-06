import logging

from models import TagORM
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import TagDatabaseError

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
