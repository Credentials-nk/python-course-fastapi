# Changelog — Migración Async

## Qué se cambió

Se migró toda la capa de base de datos de SQLAlchemy síncrono a asíncrono para que los
endpoints de FastAPI puedan declararse como `async def` de forma correcta.

### Archivos modificados

| Archivo | Cambio |
|---|---|
| `core/db.py` | `create_engine` → `create_async_engine`, `Session` → `AsyncSession`, `get_db` ahora es `async def` con `async with` |
| `api/v1/posts/repository.py` | Todos los métodos pasan a `async def` y cada llamada a la DB lleva `await` |
| `api/v1/posts/router.py` | Todos los endpoints pasan a `async def` y cada llamada al repositorio lleva `await` |

### Dependencia extra requerida

```
pip install aiosqlite  # driver async para SQLite
```

Para Postgres se usaría `asyncpg` en lugar de `psycopg2` en la URL de conexión.

---

## El yeite (cómo funciona)

FastAPI corre sobre un event loop (asyncio). Cuando un endpoint es `def` síncrono,
FastAPI lo mueve a un **threadpool** para no bloquear el loop. Cuando es `async def`,
corre **directamente en el event loop**.

El problema es que `async def` sin `await` real (es decir, con I/O bloqueante adentro)
**bloquea el event loop entero**, frenando todas las requests simultáneas.

Por eso la migración no es solo agregar `async def` en el router — hay que hacer
async **toda la cadena**: engine → sesión → repositorio → endpoint.

```
create_async_engine  →  AsyncSession  →  await repo.método()  →  async def endpoint
```

Si algún eslabón de la cadena es bloqueante, el beneficio desaparece.

---

## ¿Conviene en este caso?

**En este proyecto de curso: no es necesario, pero es válido para aprenderlo.**

| Criterio | Contexto de este proyecto |
|---|---|
| Carga concurrente alta | No — es un proyecto educativo |
| Operaciones I/O lentas o externas | No — SQLite local, sin APIs externas |
| Equipo con experiencia async | Depende del alumno |
| Ganancia real de rendimiento | Mínima con SQLite |

El enfoque async brilla en escenarios con **muchas requests concurrentes** y **I/O lento**
(llamadas a APIs externas, Postgres con alta carga, WebSockets). Con SQLite y tráfico
bajo, la diferencia práctica es imperceptible y la complejidad del código aumenta.

**Conclusión:** `def` síncrono con FastAPI threadpool es la opción más simple y
suficiente para este caso. La migración async vale la pena aprenderla porque es el
patrón correcto en producción con Postgres y alta concurrencia.
