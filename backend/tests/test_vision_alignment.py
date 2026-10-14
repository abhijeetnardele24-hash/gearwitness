import os

import cv2
import numpy as np
import pytest

from backend.app.models.schemas import BoundingBox
from backend.app.services.fixture_generator import ensure_fixture_images
from backend.app.services.vision_alignment import (
    align_and_detect_changes,
    crop_bounding_box,
    load_image_rgb,
)


def test_load_image_rgb_success(tmp_path):
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    p = str(tmp_path / "test.jpg")
    cv2.imwrite(p, img)
    loaded = load_image_rgb(p)
    assert loaded.shape == (100, 100, 3)


def test_load_image_rgb_missing():
    with pytest.raises(FileNotFoundError):
        load_image_rgb("non_existent_file.jpg")


def test_crop_bounding_box(tmp_path):
    img = np.full((200, 200, 3), 128, dtype=np.uint8)
    p = str(tmp_path / "source.jpg")
    cv2.imwrite(p, img)

    out = str(tmp_path / "crop.jpg")
    # Normalized coordinates on 200x200 image: 0.25 * 200 = 50 width, 0.30 * 200 = 60 height
    bbox = BoundingBox(x=0.05, y=0.10, width=0.25, height=0.30)
    res_path = crop_bounding_box(p, bbox, out)

    assert os.path.exists(res_path)
    cropped = cv2.imread(res_path)
    assert cropped.shape[0] == 60
    assert cropped.shape[1] == 50


def test_align_and_detect_changes_hero_fixture(tmp_path):
    paths = ensure_fixture_images(str(tmp_path))
    co_path = paths["fx3_front_checkout"]
    ci_path = paths["fx3_front_checkin"]

    diff_dir = str(tmp_path / "diffs")
    alignment, bboxes = align_and_detect_changes(co_path, ci_path, output_diff_dir=diff_dir)

    assert alignment.difference_score >= 0.0
    assert len(bboxes) >= 1
    assert alignment.diff_heatmap_path is not None
    assert os.path.exists(alignment.diff_heatmap_path)


def test_insufficient_overlap_detection(tmp_path):
    # Two completely unrelated white vs black images
    img1 = np.full((200, 200, 3), 255, dtype=np.uint8)
    img2 = np.full((200, 200, 3), 0, dtype=np.uint8)

    p1 = str(tmp_path / "unrelated1.jpg")
    p2 = str(tmp_path / "unrelated2.jpg")
    cv2.imwrite(p1, img1)
    cv2.imwrite(p2, img2)

    alignment, bboxes = align_and_detect_changes(p1, p2)
    assert alignment.insufficient_overlap is True
    assert alignment.is_aligned is False
