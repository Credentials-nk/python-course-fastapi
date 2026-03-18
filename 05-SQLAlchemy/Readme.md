# Seccion 5: SQLAlchemy y bases de datos relacionales

## Conceptos abarcados

### 1. ORM con SQLAlchemy
Uso de SQLAlchemy como ORM para mapear tablas a clases Python. Se definen modelos con `DeclarativeBase` y `mapped_column` con tipado explícito usando `Mapped[T]`.

### 2. Modelos y relaciones
- **PostORM**, **AuthorORM**, **TagORM**: modelos que representan las tablas de la base de datos.
- Relación uno-a-muchos entre `Author` y `Post` con `relationship` y `back_populates`.
- Relación muchos-a-muchos entre `Post` y `Tag` a través de una tabla intermedia `post_tags` (`secondary`).

### 3. Sesión y dependencias
Patrón `get_db` con `yield` para inyectar la sesión como dependencia en cada endpoint, garantizando que se cierre correctamente y se haga rollback ante errores.

### 4. CRUD con SQLAlchemy Core/ORM
- **GET** `/posts`: listado con filtros, ordenamiento y paginación usando `select()`, `where()`, `order_by()`, `limit()` y `offset()`.
- **GET** `/posts/{id}`: búsqueda por PK con `scalar_one_or_none()`.
- **GET** `/post/by-tags`: filtro por tags usando `join()`, `in_()` y `distinct()`.
- **POST** `/posts`: creación con manejo de autor y tags existentes (upsert manual), `flush()` para obtener IDs antes del commit.
- **PUT** `/posts/{id}`: actualización parcial con `model_dump(exclude_unset=True)` y `setattr`.
- **DELETE** `/posts/{id}`: eliminación con cascade.

### 5. Manejo de errores de base de datos
Captura de `IntegrityError` para conflictos de unicidad (título duplicado) y `SQLAlchemyError` para errores genéricos, respondiendo con los códigos HTTP correspondientes (409, 500).

### 6. Carga de relaciones: lazy vs eager
Uso de `selectinload` y `joinedload` para cargar relaciones eficientemente y evitar el problema N+1.

### 7. Variables de entorno y configuración
Carga de la `DATABASE_URL` desde un archivo `.env` con `python-dotenv`, con soporte para SQLite (desarrollo) y PostgreSQL (producción) de forma transparente.

### 8. Docker Compose con PostgreSQL
Levantamiento de una instancia de PostgreSQL 16 con Docker Compose para el entorno de desarrollo local.
