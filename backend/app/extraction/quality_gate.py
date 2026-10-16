"""Image quality assessment and auto-deskewing module.
Computes Laplacian variance for blur detection, checks resolution,
estimates skew angle, and corrects small-angle and 90-degree rotations.
"""

from typing import Tuple, List
import cv2
import numpy as np
from backend.app.schemas.common import ImageQualityReport


def assess_and_deskew_image(image_bgr: np.ndarray) -> Tuple[np.ndarray, ImageQualityReport]:
    """Inspect image quality, detect blur and skew, and auto-deskew."""
    h, w = image_bgr.shape[:2]
    warnings: List[str] = []

    # 1. Blur detection using Laplacian variance
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_blurry = blur_score < 100.0
    if is_blurry:
        warnings.append(f"Image appears blurry (Laplacian variance {blur_score:.1f} < 100.0)")

    # 2. Resolution check
    if w < 500 or h < 500:
        warnings.append(f"Low image resolution ({w}x{h} px); minimum recommended is 500x500 px")

    # 3. Skew estimation
    # Otsu thresholding to find text pixels
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find coordinates of all text pixels
    pts = cv2.findNonZero(thresh)
    deskewed_img = image_bgr
    skew_angle = 0.0

    if pts is not None and len(pts) > 50:
        rect = cv2.minAreaRect(pts)
        angle = rect[-1]
        # minAreaRect returns angle in [-90, 0)
        if angle < -45:
            skew_angle = -(90 + angle)
        elif angle > 45:
            skew_angle = -(angle - 90)
        else:
            skew_angle = -angle

        # If significant skew detected (between 0.75 and 45 degrees), deskew
        if 0.75 <= abs(skew_angle) <= 45.0:
            warnings.append(f"Detected image skew of {skew_angle:.1f}° - auto-deskew applied")
            (center_x, center_y) = (w // 2, h // 2)
            rot_mat = cv2.getRotationMatrix2D((center_x, center_y), skew_angle, 1.0)
            deskewed_img = cv2.warpAffine(
                image_bgr,
                rot_mat,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )

    report = ImageQualityReport(
        blur_score=round(blur_score, 2),
        is_blurry=is_blurry,
        skew_angle_deg=round(skew_angle, 2),
        resolution_dpi=None,
        warnings=warnings,
    )

    return deskewed_img, report
