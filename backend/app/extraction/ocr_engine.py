"""Dual-source text and visual OCR extraction engine.
Combines pdfplumber (digital text layer) and RapidOCR (independent optical recognition on rendered images)
without any copyleft/AGPL dependencies.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image
import pypdfium2 as pdfium
import pdfplumber
from rapidocr_onnxruntime import RapidOCR

from backend.app.core.logging import logger
from backend.app.schemas.common import EvidenceToken
from backend.app.extraction.quality_gate import assess_and_deskew_image


class OCREngine:
    def __init__(self):
        self._rapid_ocr = RapidOCR()

    def render_and_extract_tokens(
        self,
        file_path: str,
        mime_type: str,
        save_dir: Optional[Path] = None,
        doc_id: Optional[str] = None,
    ) -> Tuple[List[np.ndarray], List[EvidenceToken], List[str]]:
        """Renders pages to images and extracts all OCR and digital tokens with normalized bounding boxes.

        Returns:
            (page_images_bgr, evidence_tokens, quality_warnings)
        """
        path = Path(file_path)
        page_images: List[np.ndarray] = []
        tokens: List[EvidenceToken] = []
        warnings: List[str] = []

        if mime_type == "application/pdf":
            # 1. Render pages with pypdfium2
            pdf = pdfium.PdfDocument(file_path)
            for page_idx in range(len(pdf)):
                page = pdf[page_idx]
                # Render at 200 DPI (approx 2.77 scale factor from 72 DPI)
                bitmap = page.render(scale=2.77)
                pil_image = bitmap.to_pil()
                img_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

                # Quality gate and deskew
                deskewed_bgr, q_report = assess_and_deskew_image(img_bgr)
                page_images.append(deskewed_bgr)
                warnings.extend(q_report.warnings)

                if save_dir and doc_id:
                    page_file = save_dir / f"{doc_id}_page_{page_idx + 1}.png"
                    cv2.imwrite(str(page_file), deskewed_bgr)

            # 2. Extract digital text layer using pdfplumber if present
            try:
                with pdfplumber.open(file_path) as pdf_plumb:
                    for page_idx, page in enumerate(pdf_plumb.pages, start=1):
                        p_width = float(page.width)
                        p_height = float(page.height)
                        words = page.extract_words(keep_blank_chars=False)
                        for word in words:
                            text = word.get("text", "").strip()
                            if text:
                                # Normalize bbox to [0.0, 1.0]
                                x0 = max(0.0, min(1.0, float(word["x0"]) / p_width))
                                y0 = max(0.0, min(1.0, float(word["top"]) / p_height))
                                x1 = max(0.0, min(1.0, float(word["x1"]) / p_width))
                                y1 = max(0.0, min(1.0, float(word["bottom"]) / p_height))
                                tokens.append(
                                    EvidenceToken(
                                        text=text,
                                        page=page_idx,
                                        bbox=[round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)],
                                        confidence=1.0,  # Digital exact token
                                        source="pdf_text_layer",
                                    )
                                )
            except Exception as e:
                logger.warning(f"Could not read digital text layer: {e}")

        else:
            # Single image file (PNG / JPEG)
            pil_img = Image.open(file_path)
            img_bgr = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
            deskewed_bgr, q_report = assess_and_deskew_image(img_bgr)
            page_images.append(deskewed_bgr)
            warnings.extend(q_report.warnings)
            if save_dir and doc_id:
                cv2.imwrite(str(save_dir / f"{doc_id}_page_1.png"), deskewed_bgr)

        # 3. Run RapidOCR on each page image
        for page_idx, img_bgr in enumerate(page_images, start=1):
            h, w = img_bgr.shape[:2]
            ocr_results, _ = self._rapid_ocr(img_bgr)
            if ocr_results:
                for item in ocr_results:
                    # item format: [box_points, text, confidence]
                    # box_points is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                    box_pts, text, score = item[0], item[1].strip(), float(item[2])
                    if text:
                        pts = np.array(box_pts)
                        min_x, max_x = float(pts[:, 0].min()), float(pts[:, 0].max())
                        min_y, max_y = float(pts[:, 1].min()), float(pts[:, 1].max())

                        # Normalize
                        x0 = max(0.0, min(1.0, min_x / w))
                        y0 = max(0.0, min(1.0, min_y / h))
                        x1 = max(0.0, min(1.0, max_x / w))
                        y1 = max(0.0, min(1.0, max_y / h))

                        tokens.append(
                            EvidenceToken(
                                text=text,
                                page=page_idx,
                                bbox=[round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)],
                                confidence=round(score, 4),
                                source="rapidocr",
                            )
                        )

        return page_images, tokens, warnings


ocr_engine = OCREngine()
