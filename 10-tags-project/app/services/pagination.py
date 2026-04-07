from math import ceil
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100


def sanitize_pagination(
    page: int = 1, per_page: int = DEFAULT_PER_PAGE
) -> tuple[int, int]:
    page = max(1, int(page or 1))  # mínimo página 1, evita 0 o None
    # clamp entre 1 y MAX
    per_page = min(MAX_PER_PAGE, max(1, int(per_page or DEFAULT_PER_PAGE)))
    return page, per_page


async def paginate_query(
    db: AsyncSession,
    model: Any,
    query: Optional[Select] = None,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
    order_by: Optional[str] = None,
    direction: str = "asc",
    allowed_order: Optional[Dict[str, Any]] = None,
) -> Tuple[int, int, int, List[Any]]:
    # normaliza antes de cualquier cálculo
    page, per_page = sanitize_pagination(page, per_page)

    # si no se pasa query, hace un select básico del modelo
    query = query if query is not None else select(model)

    if allowed_order and order_by:
        # si el campo no está en allowed_order, usa el primero como fallback
        col = allowed_order.get(order_by, next(iter(allowed_order.values())))
        query = query.order_by(col.desc() if direction == "desc" else col.asc())

    # cuenta respetando los filtros del query (no el total de la tabla)
    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0

    if total == 0:
        return 0, 0, 1, []

    total_pages = ceil(total / per_page)
    current_page = min(page, total_pages)  # evita pedir una página que no existe

    offset = (current_page - 1) * per_page  # registros a saltear
    results = list(
        (await db.execute(query.limit(per_page).offset(offset))).scalars().all()
    )

    return total, total_pages, current_page, results
