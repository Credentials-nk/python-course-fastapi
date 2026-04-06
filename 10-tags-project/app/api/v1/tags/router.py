from core.db import DbSession
from core.security import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status

from .exceptions import TagDatabaseError
from .repository import TagRepository
from .schemas import TagCreate, TagPublic

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post(
    "",
    response_model=TagPublic,
    response_description="Tag creado (OK)",
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    tag: TagCreate, db: DbSession, user=Depends(get_current_user)
):
    repository = TagRepository(db)

    try:
        tag_created = await repository.create_tag(name=tag.name)
        return TagPublic.model_validate(tag_created)
    except TagDatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el tag: {e}")
