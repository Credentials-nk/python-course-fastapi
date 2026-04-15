from core.db import DbSession
from core.security import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query, status

from .exceptions import TagDatabaseError
from .repository import TagRepository
from .schemas import PaginatedTag, TagCreate, TagPublic, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=PaginatedTag)
async def list_tags(
    db: DbSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    order_by: str = Query("id", pattern="^(id|name)$"),
    direction: str = Query("asc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
):
    repository = TagRepository(db)
    total, total_pages, current_page, items = await repository.list_tags(
        page=page,
        per_page=per_page,
        order_by=order_by,
        direction=direction,
        search=search,
    )
    return PaginatedTag(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        search=search,
        order_by=order_by,
        direction=direction,
        items=items,
    )


@router.post(
    "",
    response_model=TagPublic,
    response_description="Tag creado (OK)",
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(tag: TagCreate, db: DbSession, user=Depends(get_current_user)):
    repository = TagRepository(db)

    try:
        tag_created = await repository.create_tag(name=tag.name)
        return TagPublic.model_validate(tag_created)
    except TagDatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el tag: {e}")


@router.put(
    "/{tag_id}", response_model=TagPublic, dependencies=[Depends(get_current_user)]
)
async def update_tag(tag_id: int, payload: TagUpdate, db: DbSession):
    repository = TagRepository(db)
    try:
        tag_updated = await repository.update(tag_id=tag_id, payload=payload)

        if tag_updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado"
            )

        return TagPublic.model_validate(tag_updated)

    except TagDatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el tag: {e}")


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete_tag(tag_id: int, db: DbSession):
    repository = TagRepository(db)
    try:
        tag_deleted = await repository.delete(tag_id=tag_id)

        if not tag_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado"
            )

    except TagDatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el tag: {e}")


@router.get("/popular/top", dependencies=[Depends(get_current_user)])
async def get_most_popular_tag(db: DbSession):
    repository = TagRepository(db)

    row = await repository.most_popular()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no hay tags en uso"
        )

    return row
