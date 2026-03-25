"""
Media Storage Service
=====================
Supports local filesystem and S3 + Cloudflare CDN.
Key design: every stored file records its storage_type (local|s3).
When resolving URLs, we look at the record's storage_type — NOT the current
STORAGE_BACKEND setting — so mixed-storage periods work correctly.

MIME detection uses file-header magic bytes (no native libmagic needed,
fully cross-platform on Windows / Linux / macOS).
"""
from __future__ import annotations
import io
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException

from app.config import settings


# ── Allowed MIME types ────────────────────────────────────────────────────────
ALLOWED_IMAGE_MIMES = {
    "image/jpeg", "image/png", "image/webp", "image/gif", "image/avif",
}
ALLOWED_VIDEO_MIMES = {
    "video/mp4", "video/webm", "video/quicktime",
}
ALLOWED_MIMES = ALLOWED_IMAGE_MIMES | ALLOWED_VIDEO_MIMES

MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB


# ── Pure-Python MIME detection via file-header magic bytes ───────────────────
# No libmagic / python-magic needed — works on Windows, Linux, macOS.
_SIGNATURES: list[tuple[bytes, int, str]] = [
    # (magic_bytes, offset, mime_type)
    (b"\xff\xd8\xff",               0, "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n",          0, "image/png"),
    (b"GIF87a",                     0, "image/gif"),
    (b"GIF89a",                     0, "image/gif"),
    (b"RIFF",                       0, "image/webp"),   # checked further below
    (b"\x00\x00\x00\x0cftyp",       0, "video/mp4"),    # mp4 ftyp box
    (b"\x00\x00\x00\x18ftyp",       0, "video/mp4"),
    (b"\x00\x00\x00\x20ftyp",       0, "video/mp4"),
    (b"\x1aE\xdf\xa3",              0, "video/webm"),
    (b"ftypqt",                     4, "video/quicktime"),
    (b"ftyp",                       4, "video/mp4"),    # generic mp4
]

_AVIF_BRAND = b"avif"
_WEBP_MARKER = b"WEBP"


def _detect_mime(header: bytes) -> Optional[str]:
    """
    Inspect the first 32 bytes of a file to determine MIME type.
    Returns None if the type cannot be determined.
    """
    for sig, offset, mime in _SIGNATURES:
        end = offset + len(sig)
        if header[offset:end] == sig:
            # Distinguish RIFF/WEBP vs RIFF/AVI etc.
            if sig == b"RIFF":
                if header[8:12] == _WEBP_MARKER:
                    return "image/webp"
                continue
            # Distinguish AVIF inside ISO Base Media (ftyp box)
            if mime == "video/mp4" and _AVIF_BRAND in header[:32]:
                return "image/avif"
            return mime
    # AVIF fallback: ftyp at offset 4 containing 'avif'
    if header[4:8] == b"ftyp" and _AVIF_BRAND in header[:32]:
        return "image/avif"
    return None


# ── S3 client (lazy, only imported when STORAGE_BACKEND=s3) ──────────────────
_s3_client = None


def _get_s3():
    global _s3_client
    if _s3_client is None:
        import boto3
        _s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return _s3_client


# ── Core upload ───────────────────────────────────────────────────────────────
async def upload_file(
    file: UploadFile,
    folder: str = "uploads",
    allowed_mimes: Optional[set] = None,
) -> dict:
    """
    Upload a file using the current STORAGE_BACKEND.

    Returns:
        {
            "path":         str,   # relative key (same for both backends)
            "storage_type": str,   # "local" | "s3"
            "url":          str,   # full public URL
            "file_type":    str,   # "image" | "video"
            "mime_type":    str,
            "size_bytes":   int,
            "width":        int | None,
            "height":       int | None,
            "filename":     str,
        }
    """
    if allowed_mimes is None:
        allowed_mimes = ALLOWED_MIMES

    content = await file.read()
    size    = len(content)

    # Detect MIME from file header (pure Python, no native deps)
    mime_type = _detect_mime(content[:32])

    # Fallback: trust filename extension if header unrecognised
    if mime_type is None and file.filename:
        import mimetypes
        guessed, _ = mimetypes.guess_type(file.filename)
        if guessed in allowed_mimes:
            mime_type = guessed

    if mime_type not in (allowed_mimes or ALLOWED_MIMES):
        detected_str = mime_type or "unknown"
        raise HTTPException(
            status_code=422,
            detail=f"File type '{detected_str}' not allowed. "
                   f"Allowed: {sorted(allowed_mimes or ALLOWED_MIMES)}",
        )

    is_image  = mime_type in ALLOWED_IMAGE_MIMES
    file_type = "image" if is_image else "video"

    if is_image and size > MAX_IMAGE_SIZE:
        raise HTTPException(422, f"Image too large (max {MAX_IMAGE_SIZE // 1024 // 1024} MB)")
    if not is_image and size > MAX_VIDEO_SIZE:
        raise HTTPException(422, f"Video too large (max {MAX_VIDEO_SIZE // 1024 // 1024} MB)")

    # Generate unique storage path
    ext  = _ext_from_mime(mime_type)
    name = f"{uuid.uuid4().hex}{ext}"
    path = f"{folder}/{name}"

    # Image dimensions (Pillow optional — skip gracefully if not installed)
    width = height = None
    if is_image:
        try:
            from PIL import Image as PILImage
            img    = PILImage.open(io.BytesIO(content))
            width  = img.width
            height = img.height
        except Exception:
            pass

    storage_type = settings.STORAGE_BACKEND

    if storage_type == "s3":
        _upload_to_s3(content, path, mime_type)
        url = _s3_url(path)
    else:
        _upload_to_local(content, path)
        url = _local_url(path)

    return {
        "path":         path,
        "storage_type": storage_type,
        "url":          url,
        "file_type":    file_type,
        "mime_type":    mime_type,
        "size_bytes":   size,
        "width":        width,
        "height":       height,
        "filename":     file.filename or name,
    }


# ── URL resolution — always based on stored storage_type ─────────────────────
def resolve_url(path: str, storage_type: str) -> str:
    """
    Given the stored path + storage_type, return the correct public URL.
    This is the key function that makes mixed-storage work correctly.
    """
    if not path:
        return ""
    if storage_type == "s3":
        return _s3_url(path)
    return _local_url(path)


def resolve_urls(items: list[dict]) -> list[str]:
    """Batch resolve a list of {path, storage_type} dicts."""
    return [resolve_url(i["path"], i["storage_type"]) for i in items]


# ── Delete ────────────────────────────────────────────────────────────────────
async def delete_file(path: str, storage_type: str) -> None:
    if storage_type == "s3":
        try:
            from botocore.exceptions import ClientError
            _get_s3().delete_object(Bucket=settings.AWS_S3_BUCKET, Key=path)
        except Exception:
            pass
    else:
        full = Path(settings.MEDIA_LOCAL_PATH) / path
        try:
            full.unlink(missing_ok=True)
        except Exception:
            pass


# ── Internals ─────────────────────────────────────────────────────────────────
def _upload_to_local(content: bytes, path: str) -> None:
    full = Path(settings.MEDIA_LOCAL_PATH) / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_bytes(content)


def _upload_to_s3(content: bytes, key: str, mime_type: str) -> None:
    _get_s3().put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
        Body=content,
        ContentType=mime_type,
        CacheControl="public, max-age=31536000",
    )


def _local_url(path: str) -> str:
    base = getattr(settings, "APP_URL", "http://localhost:8000")
    return f"{base}{settings.MEDIA_URL_PREFIX}/{path}"


def _s3_url(path: str) -> str:
    cdn = settings.CLOUDFLARE_CDN_URL.rstrip("/")
    return f"{cdn}/{path}"


def _ext_from_mime(mime: str) -> str:
    mapping = {
        "image/jpeg":      ".jpg",
        "image/png":       ".png",
        "image/webp":      ".webp",
        "image/gif":       ".gif",
        "image/avif":      ".avif",
        "video/mp4":       ".mp4",
        "video/webm":      ".webm",
        "video/quicktime": ".mov",
    }
    return mapping.get(mime, "")
