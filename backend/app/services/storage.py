import hashlib
import io
import os
import uuid
from typing import Tuple

from PIL import Image

from backend.app.config import settings
from backend.app.models.schemas import CaptureViewEnum, MediaEvidence

# Decompression bomb guard
Image.MAX_IMAGE_PIXELS = 25_000_000

MAGIC_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # WebP begins with RIFF....WEBP
}


class StorageError(Exception):
    pass


class InvalidMediaError(StorageError):
    pass


def detect_mime_type(data: bytes) -> str:
    """Inspects file header magic bytes to detect legitimate image formats."""
    if len(data) < 12:
        raise InvalidMediaError("Uploaded file is too small or truncated.")

    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"

    raise InvalidMediaError("Unsupported file format. Only JPEG, PNG, and WebP are permitted.")


def calculate_sha256(data: bytes) -> str:
    """Computes standard hex digest SHA-256 for media integrity."""
    return hashlib.sha256(data).hexdigest()


def ensure_upload_dirs():
    """Ensures uploads and derived directories exist."""
    base_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "originals"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "derived"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "crops"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "diffs"), exist_ok=True)
    return base_dir


def strip_exif_and_normalize(image_bytes: bytes) -> Tuple[bytes, int, int]:
    """
    Opens image, validates dimensions against decompression bombs,
    strips EXIF metadata to protect customer/operator privacy,
    and returns sanitized JPEG/PNG bytes along with dimensions.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size
            if width <= 0 or height <= 0:
                raise InvalidMediaError("Image has invalid dimensions.")

            # Convert RGBA to RGB for uniform JPEG/PNG storage
            if img.mode in ("RGBA", "P"):
                converted = img.convert("RGB")
            else:
                converted = img.convert("RGB")

            out_io = io.BytesIO()
            # Saving without EXIF dict strips all metadata tags
            converted.save(out_io, format="JPEG", quality=92, optimize=True)
            return out_io.getvalue(), width, height
    except Exception as e:
        if isinstance(e, InvalidMediaError):
            raise
        raise InvalidMediaError(f"Failed to process image: {str(e)}") from e


def save_media_file(
    file_bytes: bytes,
    original_filename: str,
    capture_view: CaptureViewEnum,
    is_checkout: bool,
) -> MediaEvidence:
    """
    Validates, strips metadata, saves to disk under generated UUID,
    and returns a MediaEvidence schema.
    """
    # 1. Size check
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise InvalidMediaError(
            f"File size exceeds maximum {settings.MAX_UPLOAD_SIZE_MB} MB limit."
        )

    # 2. Magic signature check
    mime_type = detect_mime_type(file_bytes)

    # 3. Hash computation
    sha256_hash = calculate_sha256(file_bytes)

    # 4. Strip EXIF and sanitize
    sanitized_bytes, width, height = strip_exif_and_normalize(file_bytes)

    # 5. Persist with non-user-controlled UUID
    base_dir = ensure_upload_dirs()
    media_id = str(uuid.uuid4())
    stored_name = f"{media_id}.jpg"
    orig_path = os.path.join(base_dir, "originals", stored_name)
    derived_path = os.path.join(base_dir, "derived", stored_name)

    # Store pristine original for local forensic reference
    with open(orig_path, "wb") as f_orig:
        f_orig.write(file_bytes)

    # Store sanitized derived copy for web canvas and export
    with open(derived_path, "wb") as f_der:
        f_der.write(sanitized_bytes)

    return MediaEvidence(
        id=media_id,
        filename=stored_name,
        storage_path=derived_path,
        sha256_hash=sha256_hash,
        file_size_bytes=len(sanitized_bytes),
        mime_type=mime_type,
        width=width,
        height=height,
        capture_view=capture_view,
        is_checkout=is_checkout,
    )


def safe_resolve_path(rel_or_abs_path: str) -> str:
    """
    Guards against path traversal attacks by validating that
    the resolved target is strictly inside the authorized upload directory.
    """
    base_dir = os.path.abspath(settings.UPLOAD_DIR)
    resolved = os.path.abspath(rel_or_abs_path)
    if os.path.commonpath([base_dir, resolved]) != base_dir:
        raise InvalidMediaError("Access to requested filesystem path is forbidden.")
    return resolved
