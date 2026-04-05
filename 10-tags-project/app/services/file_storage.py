import os
import shutil
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, status

router = APIRouter(prefix="/upload", tags=["uploads"])

MEDIA_DIR = "app/media"
ALLOW_MIME = ["image/png", "image/jpeg"]
MAX_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
CHUNKS = 1024 * 1024


def ensure_media_dir() -> None:
    os.makedirs(MEDIA_DIR, exist_ok=True)


async def save_uploaded_image(file: UploadFile) -> dict[str, str]:
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imágenes PNG o JPEG",
        )

    ensure_media_dir()

    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, filename)

    # class _ChunkCounter:
    #     def __init__(self, f):
    #         self._f = f
    #         self.calls = 0
    #         self.sizes = []

    #     def read(self, n=-1):
    #         data = self._f.read(n)
    #         if data:
    #             self.calls += 1
    #             self.sizes.append(len(data))
    #         return data

    #     def __getattr__(self, name):  # delega cualquier otro atributo
    #         return getattr(self._f, name)

    # reader = _ChunkCounter(file.file)

    with open(file_path, "wb") as buffer:
        # shutil.copyfileobj(reader, buffer, length=CHUNKS)
        shutil.copyfileobj(file.file, buffer, length=CHUNKS)

    size = os.path.getsize(file_path)
    if size > MAX_MB * CHUNKS:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Archivo demasiado grande (>{MAX_MB} MB)",
        )

    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}",
        # "size": f"{size}",
        # "chunk_size_used": f"{CHUNKS}",
        # "chunk_calls": f"{reader.calls}",
        # "chunk_sizes_sample": f"{reader.sizes[:5]}",
    }
