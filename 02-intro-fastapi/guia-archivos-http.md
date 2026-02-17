# Probando endpoints de FastAPI con archivos `.http`

Una alternativa ligera a Postman o Insomnia para probar tus APIs directamente desde tu editor de código.

## Requisitos

Necesitas instalar la extensión **REST Client** en VS Code:

1. Abre VS Code
2. Ve a **Extensions** (`Ctrl+Shift+X`)
3. Busca **REST Client** (autor: Huachao Mao)
4. Haz clic en **Install**

## Estructura básica de un archivo `.http`

```http
@base_url = http://localhost:8000

### Nombre de la solicitud
GET {{base_url}}/mi-endpoint
```

### Puntos clave

- **`@variable = valor`** — Define variables reutilizables. Ideal para cambiar la URL base cuando pasas de desarrollo local a un VPS o producción.
- **`###`** — Separa cada solicitud. Cada bloque es independiente y se puede ejecutar por separado.
- **`{{variable}}`** — Usa las variables definidas al inicio del archivo.

## Ejemplo completo

```http
@base_url = http://localhost:8000

### GET simple
GET {{base_url}}/

### GET con query params
GET {{base_url}}/posts?query=fastapi

### GET con path params
GET {{base_url}}/posts/1

### GET con múltiples query params
GET {{base_url}}/posts/1?include_content=false

### POST con body JSON
POST {{base_url}}/posts
Content-Type: application/json

{
    "title": "Nuevo Post",
    "content": "Contenido del post"
}
```

## Cómo ejecutar las solicitudes

1. Abre el archivo `.http` en VS Code
2. Verás un texto **"Send Request"** encima de cada bloque `###`
3. Haz clic en **Send Request**
4. La respuesta aparecerá en un panel lateral

![Send Request](https://raw.githubusercontent.com/Huachao/vscode-restclient/master/images/usage.gif)

## Ventajas sobre Postman

| Característica | Archivos `.http` | Postman |
|---|---|---|
| Vive en el repositorio | Si, se versiona con git | No, se guarda aparte |
| Requiere cuenta | No | Si (para sincronizar) |
| Peso | Un archivo de texto | Aplicación completa |
| Compartir con el equipo | Push al repo | Exportar colección |
| Curva de aprendizaje | Mínima | Media |

## Tips

- **Cambia de entorno fácilmente**: solo modifica la variable `@base_url` para apuntar a local, staging o producción.
- **Versionalo con git**: al vivir en el repo, todo el equipo tiene las mismas solicitudes de prueba.
- **Headers reutilizables**: si varias solicitudes usan el mismo header, puedes definirlo como variable.

```http
@token = Bearer eyJhbGciOiJIUzI1NiIs...

### Endpoint protegido
GET {{base_url}}/admin
Authorization: {{token}}
```

- **Organiza por archivo**: puedes tener un `.http` por módulo o grupo de endpoints (`auth.http`, `posts.http`, `users.http`).

## Antes de probar

Asegúrate de que tu servidor FastAPI esté corriendo:

```bash
uvicorn main:app --reload
```

O si usas `uv`:

```bash
uv run uvicorn main:app --reload
```

El servidor estará disponible en `http://localhost:8000` por defecto.
