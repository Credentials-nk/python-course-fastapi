# Mini Blog API — Tags Project

REST API construida con FastAPI y PostgreSQL. Implementa un sistema de blog con posts, autores, tags y uploads de imágenes.

## Stack

- **FastAPI** — framework web async
- **SQLAlchemy 2.0** — ORM async con `AsyncSession`
- **PostgreSQL** — base de datos
- **Pydantic v2** — validación y serialización
- **Docker** — contenedor de la base de datos

## Estructura

```
app/
├── api/v1/
│   ├── auth/        # JWT login
│   ├── posts/       # CRUD de posts
│   ├── tags/        # CRUD de tags
│   └── uploads/     # subida de imágenes
├── core/
│   ├── db.py        # engine, sesión async, DbSession
│   └── security.py  # JWT, get_current_user
├── models/          # modelos ORM (Post, Tag, Author)
├── services/
│   └── pagination.py  # paginación genérica reutilizable
└── main.py
```

## Endpoints

### Auth
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | Login, retorna JWT |

### Posts
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/posts` | Listar posts con paginación y búsqueda |
| GET | `/posts/{id}` | Obtener post |
| POST | `/posts` | Crear post (auth) |
| PUT | `/posts/{id}` | Actualizar post (auth) |
| DELETE | `/posts/{id}` | Eliminar post (auth) |
| GET | `/posts/by-tags` | Filtrar posts por tags |

### Tags
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tags` | Listar tags con paginación |
| POST | `/tags` | Crear tag (auth) |
| PUT | `/tags/{id}` | Actualizar tag (auth) |
| DELETE | `/tags/{id}` | Eliminar tag (auth) |

### Uploads
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/uploads/image` | Subir imagen |

## Setup

### 1. Levantar la base de datos

```bash
docker compose up -d
```

### 2. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/blogfastapi
```

### 3. Instalar dependencias y correr

```bash
uv run fastapi dev app/main.py
```

La API estará disponible en `http://localhost:8000` y la documentación en `http://localhost:8000/docs`.

## Patrones utilizados

- **Repository pattern** — la lógica de DB está encapsulada en repositories, los routers no tocan el ORM directamente
- **Schema separation** — schemas de input (`TagCreate`, `TagUpdate`) separados del schema de output (`TagPublic`)
- **Paginación genérica** — `paginate_query` en `services/pagination.py` reutilizable por cualquier repository
- **Guard via dependencies** — autenticación con `dependencies=[Depends(get_current_user)]` en el decorator del endpoint
