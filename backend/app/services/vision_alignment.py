import os
import uuid
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from backend.app.models.schemas import AlignmentResult, BoundingBox


def load_image_rgb(path: str) -> np.ndarray:
    """Loads image from path in RGB format."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found at {path}")
    img_bgr = cv2.imread(path)
    if img_bgr is None:
        raise ValueError(f"OpenCV failed to decode image at {path}")
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def crop_bounding_box(image_path: str, bbox: BoundingBox, output_path: str) -> str:
    """Extracts a cropped image corresponding to a normalized (or pixel) bounding box and saves to disk."""
    with Image.open(image_path) as img:
        w, h = img.size
        if bbox.width <= 1.0 and bbox.height <= 1.0 and w > 1 and h > 1:
            px = int(bbox.x * w)
            py = int(bbox.y * h)
            pw = max(10, int(bbox.width * w))
            ph = max(10, int(bbox.height * h))
        else:
            px = int(bbox.x)
            py = int(bbox.y)
            pw = max(10, int(bbox.width))
            ph = max(10, int(bbox.height))

        x1 = max(0, min(px, w - 1))
        y1 = max(0, min(py, h - 1))
        x2 = max(x1 + 10, min(px + pw, w))
        y2 = max(y1 + 10, min(py + ph, h))

        cropped = img.crop((x1, y1, x2, y2))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cropped.save(output_path, format="JPEG", quality=90)
    return output_path


def align_and_detect_changes(
    checkout_path: str,
    checkin_path: str,
    output_diff_dir: Optional[str] = None,
    min_area_pixels: int = 250,
) -> Tuple[AlignmentResult, List[BoundingBox]]:
    """
    Geometrically aligns checkout and checkin images using ORB + RANSAC homography,
    computes structural difference heatmap, and returns connected-component
    candidate change regions.
    """
    img_ref = load_image_rgb(checkout_path)
    img_target = load_image_rgb(checkin_path)

    h_ref, w_ref = img_ref.shape[:2]
    h_tar, w_tar = img_target.shape[:2]

    # Convert to grayscale for feature matching
    gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_RGB2GRAY)
    gray_tar = cv2.cvtColor(img_target, cv2.COLOR_RGB2GRAY)

    # 1. ORB Keypoint & Descriptor Extraction
    orb = cv2.ORB_create(nfeatures=2500, fastThreshold=12)
    kp_ref, desc_ref = orb.detectAndCompute(gray_ref, None)
    kp_tar, desc_tar = orb.detectAndCompute(gray_tar, None)

    # Default alignment metrics
    inlier_count = 0
    alignment_confidence = 0.0
    homography_matrix: Optional[List[List[float]]] = None
    insufficient_overlap = False
    warped_tar = None

    if desc_ref is not None and desc_tar is not None and len(kp_ref) >= 10 and len(kp_tar) >= 10:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(desc_ref, desc_tar)
        # Sort matches by distance
        matches = sorted(matches, key=lambda m: m.distance)

        # We need at least 10 high-quality matches for robust RANSAC
        if len(matches) >= 10:
            good_matches = matches[: min(len(matches), 150)]
            pts_ref = np.float32([kp_ref[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            pts_tar = np.float32([kp_tar[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Compute homography mapping target (checkin) -> ref (checkout)
            H, mask = cv2.findHomography(pts_tar, pts_ref, cv2.RANSAC, 5.0)

            if H is not None and mask is not None:
                inlier_count = int(np.sum(mask))
                # Validate homography determinant sanity
                det = np.linalg.det(H[:2, :2])
                if inlier_count >= 12 and 0.2 < abs(det) < 5.0:
                    homography_matrix = H.tolist()
                    alignment_confidence = round(
                        min(1.0, inlier_count / max(1, len(good_matches))), 3
                    )
                    # Warp target into reference coordinates
                    warped_tar = cv2.warpPerspective(img_target, H, (w_ref, h_ref))
                else:
                    insufficient_overlap = True
            else:
                insufficient_overlap = True
        else:
            insufficient_overlap = True
    else:
        insufficient_overlap = True

    # If alignment failed or had insufficient overlap, resize target as fallback comparison
    if warped_tar is None:
        warped_tar = cv2.resize(img_target, (w_ref, h_ref), interpolation=cv2.INTER_AREA)
        alignment_confidence = 0.0

    # 2. Structural & Luminance Difference Analysis
    gray_warped_tar = cv2.cvtColor(warped_tar, cv2.COLOR_RGB2GRAY)

    # Bilateral filter to smooth sensor noise while preserving edge boundaries
    blur_ref = cv2.bilateralFilter(gray_ref, 7, 50, 50)
    blur_tar = cv2.bilateralFilter(gray_warped_tar, 7, 50, 50)

    abs_diff = cv2.absdiff(blur_ref, blur_tar)
    diff_score = round(float(np.mean(abs_diff)) / 255.0, 4)

    # Morphological thresholding
    _, thresh = cv2.threshold(abs_diff, 35, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    cleaned_diff = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    cleaned_diff = cv2.morphologyEx(cleaned_diff, cv2.MORPH_CLOSE, kernel)

    # 3. Connected Components and Candidate Change Bounding Boxes
    contours, _ = cv2.findContours(cleaned_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bboxes: List[BoundingBox] = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= min_area_pixels:
            x, y, w, h = cv2.boundingRect(cnt)
            # Add padding around proposed bounding box
            pad = 12
            x_pad = max(0, x - pad)
            y_pad = max(0, y - pad)
            w_pad = min(w_ref - x_pad, w + 2 * pad)
            h_pad = min(h_ref - y_pad, h + 2 * pad)

            # Store normalized 0.0 to 1.0 coordinates
            norm_x = round(float(x_pad) / w_ref, 4)
            norm_y = round(float(y_pad) / h_ref, 4)
            norm_w = round(float(w_pad) / w_ref, 4)
            norm_h = round(float(h_pad) / h_ref, 4)

            bboxes.append(BoundingBox(x=norm_x, y=norm_y, width=norm_w, height=norm_h))

    # Sort bounding boxes by area descending, take top candidate regions (max 8)
    bboxes = sorted(bboxes, key=lambda b: b.width * b.height, reverse=True)[:8]

    # 4. Generate Visual Heatmap Overlay
    diff_heatmap_path = None
    if output_diff_dir:
        os.makedirs(output_diff_dir, exist_ok=True)
        heatmap_id = str(uuid.uuid4())
        diff_heatmap_path = os.path.join(output_diff_dir, f"diff_{heatmap_id}.jpg")

        # Colorize difference map (JET / INFERNO)
        heatmap_color = cv2.applyColorMap(abs_diff, cv2.COLORMAP_JET)
        # Blend onto checkout reference image (65% original, 35% heatmap)
        blend = cv2.addWeighted(
            cv2.cvtColor(img_ref, cv2.COLOR_RGB2BGR), 0.65, heatmap_color, 0.35, 0
        )

        # Draw numbered bounding boxes on heatmap using denormalized pixel coords
        for i, box in enumerate(bboxes, start=1):
            px_x = int(box.x * w_ref)
            px_y = int(box.y * h_ref)
            px_w = int(box.width * w_ref)
            px_h = int(box.height * h_ref)
            cv2.rectangle(
                blend, (px_x, px_y), (px_x + px_w, px_y + px_h), (0, 165, 255), 2
            )
            cv2.putText(
                blend,
                f"#{i}",
                (px_x + 4, max(20, px_y + 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 165, 255),
                2,
            )

        cv2.imwrite(diff_heatmap_path, blend)

    result = AlignmentResult(
        is_aligned=(not insufficient_overlap and alignment_confidence >= 0.2),
        inlier_count=inlier_count,
        homography_matrix=homography_matrix,
        alignment_confidence=alignment_confidence,
        insufficient_overlap=insufficient_overlap,
        difference_score=diff_score,
        diff_heatmap_path=diff_heatmap_path,
    )

    return result, bboxes
