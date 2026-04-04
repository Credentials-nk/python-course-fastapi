# import asyncio
# import threading
# import time
from typing import List, Literal, Optional, Union

from core.db import DbSession
from core.security import get_current_user, oauth2_scheme
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from .exceptions import PostConflictError, PostDatabaseError
from .repository import PostRepository
from .schemas import PaginatedPost, PostCreate, PostPublic, PostSummary, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])

# ============ Async vs Sync =============== #


# @router.get("/sync")
# def sync_endpoint():
#     print("SYNC thread: ", threading.current_thread().name)
#     time.sleep(8)
#     return {"message": "Función síncrona termino"}


# @router.get("/async")
# async def async_endpoint():
#     print("ASYNC thread: ", threading.current_thread().name)
#     await asyncio.sleep(8)
#     return {"message": "Función asíncrona termino"}


# ========================================== #


@router.get("", response_model=PaginatedPost)
async def list_posts(
    db: DbSession,
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
):

    repository = PostRepository(db)

    query = query or text

    total, total_pages, current_page, orm_posts = await repository.search(
        query, order_by, direction, page, per_page
    )

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


@router.get("/by-tags", response_model=List[PostPublic])
async def filter_by_tags(
    db: DbSession,
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="One or more tags",
        example="Example: ?tags=python&tags=fastapi",
    ),
):

    repository = PostRepository(db)

    posts = await repository.by_tags(tags)

    return posts


@router.get(
    "/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post found",
)
async def get_post(
    db: DbSession,
    post_id: int = Path(
        ...,
        ge=1,
        # lt=4,
        title="ID Post",
        description="Identifier of Post. Should be gretter tan 1.",
        example=1,
    ),
    include_content: bool = Query(default=True, description="Flag to include content"),
):
    repository = PostRepository(db)

    post = await repository.get(post_id=post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return (
        PostPublic.model_validate(post, from_attributes=True)
        if include_content
        else PostSummary.model_validate(post, from_attributes=True)
    )


@router.post(
    "",
    response_model=PostPublic,
    response_description="Post Created",
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post: PostCreate, db: DbSession, user=Depends(get_current_user)):
    repository = PostRepository(db)

    try:
        return await repository.create_post(
            title=post.title,
            content=post.content,
            author=user,
            tags=[tag.model_dump() for tag in (post.tags or [])],
        )
    except PostConflictError:
        raise HTTPException(
            status_code=409, detail="A post with that title already exists"
        )
    except PostDatabaseError:
        raise HTTPException(status_code=500, detail="Error al crear el post")


@router.put(
    "/{post_id}",
    response_model=PostPublic,
    response_description="Post Updated",
    response_model_exclude_none=True,
)
async def update_post(
    post_id: int, data: PostUpdate, db: DbSession, user=Depends(get_current_user)
):
    repository = PostRepository(db)

    try:
        updates = data.model_dump(exclude_unset=True)

        post_updated = await repository.update_post(post_id=post_id, payload=updates)

        if not post_updated:
            raise HTTPException(status_code=404, detail="Post not found")

        return post_updated
    except PostDatabaseError:
        raise HTTPException(status_code=500, detail="Error al actualizar el post")


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, db: DbSession, user=Depends(get_current_user)):
    repository = PostRepository(db)

    try:
        post_deleted = await repository.delete_post(post_id=post_id)

        if not post_deleted:
            raise HTTPException(status_code=404, detail="Post not found")

        return post_deleted
    except PostDatabaseError:
        raise HTTPException(status_code=500, detail="Error al eliminar el post")


@router.get("/secure")
def secure_endpoint(token: str = Depends(oauth2_scheme)):
    return {"message": "Acceso con token", "toekn_recibido": token}
