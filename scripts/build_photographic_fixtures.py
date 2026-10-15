import cv2
import numpy as np
from PIL import Image

def build_realistic_fixtures():
    # Source paths
    front_raw = r"C:\Users\Abhijeet Nardele\.gemini\antigravity-ide\brain\bb914e9f-1531-4e54-b413-c7468c063511\fx3_front_pristine_1792012060495.jpg"
    acc_raw = r"C:\Users\Abhijeet Nardele\.gemini\antigravity-ide\brain\bb914e9f-1531-4e54-b413-c7468c063511\fx3_accessories_kit_1792012078316.jpg"

    w, h = 900, 600

    # 1. FRONT VIEW: Checkout (Pristine FX3 on workbench)
    img_front = Image.open(front_raw).convert("RGB")
    img_front = img_front.resize((w, h), Image.Resampling.LANCZOS)
    front_checkout = np.array(img_front)
    # Convert RGB to BGR for OpenCV
    front_checkout_bgr = cv2.cvtColor(front_checkout, cv2.COLOR_RGB2BGR)
    cv2.imwrite("data/fixtures/fx3_front_checkout.jpg", front_checkout_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print("Saved data/fixtures/fx3_front_checkout.jpg")

    # 2. FRONT VIEW: Checkin (Realistic Scratch in bbox1 + Glare in bbox2 + 0.8 deg rotation)
    front_checkin_bgr = front_checkout_bgr.copy()
    
    # bbox1: x=0.55*900=495, y=0.48*600=288, w=135, h=60 (region: 495..630, 288..348)
    # Add a realistic metallic scratch across the top anodized body
    # Draw an organic multi-segment silver/metallic scratch with subtle dark bevel
    scratch_points = [
        (525, 305), (540, 312), (555, 316), (572, 323), (590, 327), (605, 332)
    ]
    for i in range(len(scratch_points) - 1):
        pt1 = scratch_points[i]
        pt2 = scratch_points[i+1]
        # Dark shadow bevel under scratch
        cv2.line(front_checkin_bgr, (pt1[0], pt1[1] + 1), (pt2[0], pt2[1] + 1), (40, 45, 50), 2, cv2.LINE_AA)
        # Shiny exposed aluminum scratch
        cv2.line(front_checkin_bgr, pt1, pt2, (230, 235, 240), 2, cv2.LINE_AA)
        # Highlight core
        cv2.line(front_checkin_bgr, pt1, pt2, (255, 255, 255), 1, cv2.LINE_AA)

    # Secondary minor micro-scratches nearby
    cv2.line(front_checkin_bgr, (548, 322), (565, 328), (220, 225, 230), 1, cv2.LINE_AA)
    cv2.line(front_checkin_bgr, (580, 332), (598, 336), (210, 215, 220), 1, cv2.LINE_AA)

    # bbox2: x=0.32*900=288, y=0.40*600=240, w=90, h=60 (region: 288..378, 240..300)
    # Add specular glare highlight on mounting cage
    overlay = front_checkin_bgr.copy()
    cv2.ellipse(overlay, (325, 270), (28, 14), 35, 0, 360, (255, 255, 255), -1)
    # Blur overlay for soft lighting bloom
    overlay = cv2.GaussianBlur(overlay, (21, 21), 0)
    cv2.addWeighted(overlay, 0.35, front_checkin_bgr, 0.65, 0, front_checkin_bgr)

    # Slight camera angle perspective / 0.8 degree rotation shift
    center = (w // 2, h // 2)
    rot_mat = cv2.getRotationMatrix2D(center, 0.8, 1.0)
    front_checkin_bgr = cv2.warpAffine(front_checkin_bgr, rot_mat, (w, h), borderMode=cv2.BORDER_REFLECT)
    cv2.imwrite("data/fixtures/fx3_front_checkin.jpg", front_checkin_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print("Saved data/fixtures/fx3_front_checkin.jpg")

    # 3. ACCESSORIES VIEW: Checkout (Pelican hardcase with cable)
    img_acc = Image.open(acc_raw).convert("RGB")
    img_acc = img_acc.resize((w, h), Image.Resampling.LANCZOS)
    acc_checkout = np.array(img_acc)
    acc_checkout_bgr = cv2.cvtColor(acc_checkout, cv2.COLOR_RGB2BGR)
    cv2.imwrite("data/fixtures/fx3_accessories_checkout.jpg", acc_checkout_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print("Saved data/fixtures/fx3_accessories_checkout.jpg")

    # 4. ACCESSORIES VIEW: Checkin (Empty foam cutout in cable compartment)
    acc_checkin_bgr = acc_checkout_bgr.copy()
    
    # bbox3: x=0.70*900=630, y=0.53*600=318, w=108, h=120 (region: 630..738, 318..438)
    # The coiled cable is in this region. We replace it with dark cut-out foam texture
    # Create empty foam texture by sampling adjacent dark foam (e.g. from y=200..300, x=530..600)
    sample_foam = acc_checkout_bgr[250:330, 520:600]
    sample_foam_resized = cv2.resize(sample_foam, (120, 130))
    # Darken slightly to represent the empty cavity depth
    dark_cavity = (sample_foam_resized * 0.65).astype(np.uint8)
    
    # Smoothly blend the empty cavity into the cable area (x=625..745, y=315..445)
    mask = np.zeros((130, 120), dtype=np.uint8)
    cv2.ellipse(mask, (60, 65), (55, 60), 0, 0, 360, 255, -1)
    mask = cv2.GaussianBlur(mask, (15, 15), 0)
    mask_3d = mask[:, :, np.newaxis] / 255.0

    target_region = acc_checkin_bgr[315:445, 625:745]
    blended = (dark_cavity * mask_3d + target_region * (1.0 - mask_3d)).astype(np.uint8)
    acc_checkin_bgr[315:445, 625:745] = blended

    # Slight ambient lighting shift for check-in
    acc_checkin_bgr = cv2.convertScaleAbs(acc_checkin_bgr, alpha=0.98, beta=3)
    cv2.imwrite("data/fixtures/fx3_accessories_checkin.jpg", acc_checkin_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print("Saved data/fixtures/fx3_accessories_checkin.jpg")

if __name__ == "__main__":
    build_realistic_fixtures()
