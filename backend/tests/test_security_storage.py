import io

import pytest
from PIL import Image

from backend.app.models.schemas import CaptureViewEnum
from backend.app.services.storage import (
    InvalidMediaError,
    detect_mime_type,
    safe_resolve_path,
    save_media_file,
    strip_exif_and_normalize,
)


def test_detect_mime_type_jpeg():
    raw = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01"
    assert detect_mime_type(raw) == "image/jpeg"


def test_detect_mime_type_png():
    raw = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    assert detect_mime_type(raw) == "image/png"


def test_detect_mime_type_webp():
    raw = b"RIFF\x24\x00\x00\x00WEBPVP8 "
    assert detect_mime_type(raw) == "image/webp"


def test_detect_mime_type_rejects_malicious_executable():
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff"
    with pytest.raises(InvalidMediaError, match="Unsupported file format"):
        detect_mime_type(fake_exe)


def test_path_traversal_defense():
    with pytest.raises(InvalidMediaError, match="forbidden"):
        safe_resolve_path("../../etc/passwd")


def test_strip_exif_and_normalize():
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    sanitized, w, h = strip_exif_and_normalize(buf.getvalue())
    assert w == 100
    assert h == 100
    assert len(sanitized) > 0


def test_save_media_file_exceeds_size(monkeypatch):
    import backend.app.services.storage as storage_mod

    monkeypatch.setattr(storage_mod.settings, "MAX_UPLOAD_SIZE_MB", 1)
    huge_bytes = b"A" * (2 * 1024 * 1024)
    with pytest.raises(InvalidMediaError, match="exceeds maximum"):
        save_media_file(huge_bytes, "huge.jpg", CaptureViewEnum.FRONT, True)
