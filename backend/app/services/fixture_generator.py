import os

import cv2
import numpy as np


def ensure_fixture_images(output_dir: str = "data/fixtures") -> dict:
    """
    Generates high-resolution synthetic fixture images for the Sony FX3 Cinema Kit
    demonstrating pristine checkout and realistic return condition (scratch + missing cable + angle change).
    """
    os.makedirs(output_dir, exist_ok=True)

    paths = {
        "fx3_front_checkout": os.path.join(output_dir, "fx3_front_checkout.jpg"),
        "fx3_front_checkin": os.path.join(output_dir, "fx3_front_checkin.jpg"),
        "fx3_acc_checkout": os.path.join(output_dir, "fx3_accessories_checkout.jpg"),
        "fx3_acc_checkin": os.path.join(output_dir, "fx3_accessories_checkin.jpg"),
    }

    # 1. FRONT VIEW: Checkout (Pristine Camera Body on Stone Mat)
    w, h = 900, 600
    front_checkout = np.full((h, w, 3), (242, 240, 238), dtype=np.uint8)  # Studio stone background

    # Draw equipment mat
    cv2.rectangle(front_checkout, (100, 80), (800, 520), (220, 218, 214), -1)
    cv2.rectangle(front_checkout, (100, 80), (800, 520), (180, 175, 170), 2)

    # Draw Camera Body (Dark Charcoal Magnesium Housing)
    cv2.rectangle(front_checkout, (280, 200), (620, 440), (38, 38, 38), -1)
    cv2.rectangle(front_checkout, (280, 200), (620, 440), (25, 25, 25), 3)

    # Camera Mount / Lens Circle
    cv2.circle(front_checkout, (450, 320), 85, (55, 55, 55), -1)
    cv2.circle(front_checkout, (450, 320), 75, (15, 15, 15), -1)
    cv2.circle(front_checkout, (450, 320), 45, (25, 60, 95), -1)  # Lens glass reflection

    # Grip handle
    cv2.rectangle(front_checkout, (240, 220), (280, 420), (30, 30, 30), -1)
    # Status LED & Buttons
    cv2.circle(front_checkout, (310, 230), 6, (0, 180, 80), -1)  # Green power LED
    cv2.rectangle(front_checkout, (340, 225), (370, 235), (200, 40, 40), -1)  # Red record button

    # Brand logo / Label
    cv2.putText(
        front_checkout,
        "GEARWITNESS FX3",
        (320, 185),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (40, 40, 40),
        2,
    )
    cv2.putText(
        front_checkout,
        "S/N: 4892011",
        (320, 465),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (100, 100, 100),
        1,
    )

    # 2. FRONT VIEW: Check-in (Return: 1 scratch on chassis corner + 2° slight rotation / lighting difference)
    front_checkin = front_checkout.copy()

    # Add minor global illumination change (ambient lighting shift)
    front_checkin = cv2.convertScaleAbs(front_checkin, alpha=0.97, beta=8)

    # Introduce noticeable condition change: Scratch on top-right chassis corner
    # Sharp white/metallic abrasion line across (570, 215) to (605, 235)
    cv2.line(front_checkin, (570, 215), (605, 235), (210, 215, 220), 2)
    cv2.line(front_checkin, (585, 225), (610, 230), (180, 185, 190), 1)

    # Minor harmless lighting glare artifact near grip (simulates real-world reflection)
    cv2.ellipse(front_checkin, (260, 330), (16, 8), 45, 0, 360, (75, 75, 75), -1)

    # Apply 1.2 degree slight geometric skew to test OpenCV RANSAC alignment
    center = (w // 2, h // 2)
    rot_mat = cv2.getRotationMatrix2D(center, 1.2, 1.0)
    front_checkin = cv2.warpAffine(front_checkin, rot_mat, (w, h), borderValue=(242, 240, 238))

    # 3. ACCESSORIES VIEW: Checkout (Case with Camera, Lens, Charger, USB-C Cable)
    acc_checkout = np.full((h, w, 3), (242, 240, 238), dtype=np.uint8)
    # Foam insert cutouts
    cv2.rectangle(acc_checkout, (120, 100), (780, 500), (45, 45, 45), -1)  # Hardcase foam

    # Compartment 1: Camera Body
    cv2.rectangle(acc_checkout, (160, 140), (420, 460), (70, 70, 70), -1)
    cv2.putText(
        acc_checkout, "CAMERA BODY", (210, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1
    )

    # Compartment 2: 24-70mm Lens
    cv2.rectangle(acc_checkout, (460, 140), (590, 460), (70, 70, 70), -1)
    cv2.putText(acc_checkout, "LENS", (500, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    # Compartment 3: Dual Charger
    cv2.rectangle(acc_checkout, (630, 140), (740, 280), (70, 70, 70), -1)
    cv2.putText(
        acc_checkout, "CHARGER", (645, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1
    )

    # Compartment 4: USB-C Tether Cable (Pristine: coiled cable present)
    cv2.rectangle(acc_checkout, (630, 320), (740, 460), (70, 70, 70), -1)
    cv2.circle(acc_checkout, (685, 390), 38, (25, 25, 25), 6)  # Coiled cable
    cv2.putText(
        acc_checkout, "CABLE", (660, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1
    )

    # 4. ACCESSORIES VIEW: Check-in (Return: USB-C Cable Missing from compartment 4!)
    acc_checkin = acc_checkout.copy()
    # Empty compartment 4 (foam cutout visible with NO cable inside)
    cv2.rectangle(acc_checkin, (630, 320), (740, 460), (55, 55, 55), -1)  # Empty foam recess
    cv2.putText(
        acc_checkin, "[ EMPTY ]", (650, 395), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 120), 1
    )

    # Save all fixture images
    cv2.imwrite(paths["fx3_front_checkout"], front_checkout)
    cv2.imwrite(paths["fx3_front_checkin"], front_checkin)
    cv2.imwrite(paths["fx3_acc_checkout"], acc_checkout)
    cv2.imwrite(paths["fx3_acc_checkin"], acc_checkin)

    return paths
