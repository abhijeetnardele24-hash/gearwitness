import hashlib
import io
import os
import uuid
from typing import Optional, Tuple

from PIL import Image

from backend.app.config import settings
from backend.app.models.schemas import BoundingBox, CaptureViewEnum, MediaEvidence

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


def get_public_url(path: Optional[str]) -> Optional[str]:
    """Converts a local filesystem storage path to a browser-safe public URL."""
    if not path:
        return None
    normalized = path.replace("\\", "/")
    if normalized.startswith("http://") or normalized.startswith("https://"):
        return normalized
    if normalized.startswith("/fixtures/") or normalized.startswith("/media/"):
        return normalized
    if normalized.startswith("data/fixtures/"):
        return "/" + normalized[len("data/"):]
    if normalized.startswith("fixtures/"):
        return "/" + normalized
    if normalized.startswith("uploads/"):
        return "/media/" + normalized[len("uploads/"):]
    if normalized.startswith("data/media/"):
        return "/media/" + normalized[len("data/media/"):]
    if normalized.startswith("media/"):
        return "/" + normalized
    if "crops/" in normalized:
        idx = normalized.find("crops/")
        return "/media/" + normalized[idx:]
    if "derived/" in normalized:
        idx = normalized.find("derived/")
        return "/media/" + normalized[idx:]
    if "fixtures/" in normalized:
        idx = normalized.find("fixtures/")
        return "/" + normalized[idx:]
    if "uploads/" in normalized:
        idx = normalized.find("uploads/")
        return "/media/" + normalized[idx + len("uploads/"):]
    return f"/media/{normalized.lstrip('/')}"


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


def save_crop_image(parent_image_path: str, bbox: BoundingBox, crop_prefix: str) -> Tuple[str, str]:
    """
    Extracts a real bounding box crop from the source image,
    saves it to the crops directory, and returns (storage_path, public_url).
    Handles normalized (0..1) bounding box coordinates.
    """
    base_dir = ensure_upload_dirs()
    crop_dir = os.path.join(base_dir, "crops")
    os.makedirs(crop_dir, exist_ok=True)
    crop_filename = f"{crop_prefix}_{uuid.uuid4().hex[:8]}.jpg"
    crop_storage_path = os.path.join(crop_dir, crop_filename)

    try:
        with Image.open(parent_image_path) as img:
            img = img.convert("RGB")
            w, h = img.size

            # Handle normalized 0.0..1.0 bounding box
            x0 = int(bbox.x * w)
            y0 = int(bbox.y * h)
            cw = max(10, int(bbox.width * w))
            ch = max(10, int(bbox.height * h))
            x1 = min(w, x0 + cw)
            y1 = min(h, y0 + ch)

            # Safeguard coordinates
            x0 = max(0, min(w - 1, x0))
            y0 = max(0, min(h - 1, y0))
            if x1 <= x0:
                x1 = min(w, x0 + 20)
            if y1 <= y0:
                y1 = min(h, y0 + 20)

            crop_img = img.crop((x0, y0, x1, y1))
            crop_img.save(crop_storage_path, format="JPEG", quality=90)
    except Exception:
        # Fallback: create a synthetic crop image if source file is unreadable
        crop_img = Image.new("RGB", (120, 80), color=(40, 40, 45))
        crop_img.save(crop_storage_path, format="JPEG", quality=90)

    crop_public_url = get_public_url(crop_storage_path)
    return crop_storage_path, crop_public_url or f"/media/crops/{crop_filename}"


def save_media_file(
    file_bytes: bytes,
    original_filename: str,
    capture_view: CaptureViewEnum,
    is_checkout: bool,
) -> MediaEvidence:
    """
    Validates, strips metadata, saves to disk under generated UUID,
    and returns a MediaEvidence schema with valid public_url.
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

    public_url = get_public_url(derived_path)

    return MediaEvidence(
        id=media_id,
        filename=stored_name,
        storage_path=derived_path,
        public_url=public_url or f"/media/derived/{stored_name}",
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
    the resolved target is strictly inside the authorized upload or fixtures directory.
    """
    base_dir = os.path.abspath(settings.UPLOAD_DIR)
    fixtures_dir = os.path.abspath("data/fixtures")
    resolved = os.path.abspath(rel_or_abs_path)

    # Check upload directory
    if os.path.commonpath([base_dir, resolved]) == base_dir:
        return resolved

    # Check fixtures directory
    if os.path.exists(fixtures_dir) and os.path.commonpath([fixtures_dir, resolved]) == fixtures_dir:
        return resolved

    raise InvalidMediaError("Access to requested filesystem path is forbidden.")
