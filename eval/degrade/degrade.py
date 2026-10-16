"""Image degradation generator for research evaluation robustness benchmark.
Implements 6 degradation types across 3 severities:
1. Gaussian blur
2. Downscaling (low resolution)
3. Rotation (small angle and 90 degrees)
4. JPEG compression artifacts
5. Gaussian noise
6. Partial field occlusion
"""

import cv2
import numpy as np


def apply_gaussian_blur(image_bgr: np.ndarray, severity: int) -> np.ndarray:
    # Kernel sizes must be odd: 5, 9, 15
    ksize = 3 + severity * 4
    return cv2.GaussianBlur(image_bgr, (ksize, ksize), 0)


def apply_downscaling(image_bgr: np.ndarray, severity: int) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    scale_factors = {1: 0.6, 2: 0.4, 3: 0.25}
    factor = scale_factors.get(severity, 0.5)
    small = cv2.resize(image_bgr, (int(w * factor), int(h * factor)), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def apply_rotation(image_bgr: np.ndarray, severity: int) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    center = (w // 2, h // 2)
    angles = {1: 4.0, 2: 12.0, 3: 90.0}
    angle = angles.get(severity, 5.0)
    mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image_bgr, mat, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def apply_jpeg_compression(image_bgr: np.ndarray, severity: int) -> np.ndarray:
    qualities = {1: 50, 2: 25, 3: 10}
    quality = qualities.get(severity, 30)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, enc = cv2.imencode(".jpg", image_bgr, encode_param)
    return cv2.imdecode(enc, cv2.IMREAD_COLOR)


def apply_gaussian_noise(image_bgr: np.ndarray, severity: int) -> np.ndarray:
    sigmas = {1: 15.0, 2: 35.0, 3: 65.0}
    sigma = sigmas.get(severity, 20.0)
    noise = np.random.normal(0, sigma, image_bgr.shape)
    noisy = np.clip(image_bgr.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return noisy


def apply_partial_occlusion(image_bgr: np.ndarray, severity: int) -> np.ndarray:
    out = image_bgr.copy()
    h, w = out.shape[:2]
    # Draw a simulated coffee stain / smudge / dark block in bottom third
    box_heights = {1: int(h * 0.05), 2: int(h * 0.12), 3: int(h * 0.22)}
    bh = box_heights.get(severity, int(h * 0.1))
    bw = int(w * 0.35)
    y1 = int(h * 0.6)
    x1 = int(w * 0.3)
    # Fill with gray/dark smudge
    out[y1 : y1 + bh, x1 : x1 + bw] = (40, 40, 40)
    return out


DEGRADATION_DISPATCH = {
    "blur": apply_gaussian_blur,
    "downscaling": apply_downscaling,
    "rotation": apply_rotation,
    "jpeg": apply_jpeg_compression,
    "noise": apply_gaussian_noise,
    "occlusion": apply_partial_occlusion,
}


def apply_degradation(image_bgr: np.ndarray, deg_type: str, severity: int = 1) -> np.ndarray:
    fn = DEGRADATION_DISPATCH.get(deg_type)
    if not fn:
        raise ValueError(f"Unknown degradation type '{deg_type}'")
    return fn(image_bgr, severity)
