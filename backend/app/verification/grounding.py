"""Independent Evidence Grounding Check.
Searches the independent OCR token set and PDF text layer for extracted values.
Applies exact matching for numeric values and fuzzy token matching for text strings.
Distinguishes between independent evidence and same-source evidence.
"""

from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz

from backend.app.schemas.common import (
    EvidenceIndependence,
    EvidenceToken,
    ExtractedField,
    FieldStatus,
    VerificationCheck,
)


def verify_evidence_grounding(
    field_name: str,
    field: ExtractedField,
    tokens: List[EvidenceToken],
    fuzzy_threshold: float = 85.0,
) -> VerificationCheck:
    """Verifies whether an extracted field value is grounded in independent evidence tokens."""
    check_id = f"GROUNDING_{field_name.upper()}"

    if field.normalized_value is None and field.value is None:
        return VerificationCheck(
            check_id=check_id,
            applies=False,
            applies_reason=f"Field '{field_name}' has no extracted value to ground.",
            status="indeterminate",
            evidence_refs=[],
            plain_explanation=f"Skipped evidence grounding because field '{field_name}' is absent or unreadable.",
            independence=EvidenceIndependence.SAME_SOURCE,
        )

    # Convert target to string representations
    val = field.normalized_value if field.normalized_value is not None else field.value
    target_str = str(val).strip().lower()

    # Determine numeric vs text
    is_numeric = isinstance(val, (int, float))

    matched_tokens: List[EvidenceToken] = []
    has_independent_evidence = False

    for t in tokens:
        token_text = t.text.strip().lower()
        matched = False

        if is_numeric:
            # Exact numeric token match or substring match (e.g. "125000.00" in "1,25,000.00")
            clean_token_num = "".join(c for c in token_text if c.isdigit() or c == ".")
            clean_target_num = f"{float(val):.2f}"
            clean_target_alt = f"{float(val):.0f}" if float(val).is_integer() else clean_target_num

            if clean_token_num == clean_target_num or clean_token_num == clean_target_alt:
                matched = True
            elif clean_target_alt in token_text or clean_target_num in token_text:
                matched = True
        else:
            # Text matching: exact or fuzzy
            if target_str in token_text or token_text in target_str:
                matched = True
            elif fuzz.token_sort_ratio(target_str, token_text) >= fuzzy_threshold:
                matched = True

        if matched:
            matched_tokens.append(t)
            # Check independence: pdf_text_layer vs rapidocr
            if t.source == "pdf_text_layer" and field.extractor != "pdf_text_layer":
                has_independent_evidence = True
            elif field.extractor == "vlm_zero_shot" or field.extractor == "vlm_lora":
                # VLM is different model from OCR
                has_independent_evidence = True

    independence = (
        EvidenceIndependence.INDEPENDENT
        if has_independent_evidence
        else EvidenceIndependence.SAME_SOURCE
    )

    if not matched_tokens:
        return VerificationCheck(
            check_id=check_id,
            applies=True,
            status="failed",
            evidence_refs=[],
            plain_explanation=(
                f"Field '{field_name}' with claimed value '{val}' could NOT be located anywhere "
                "in the document OCR tokens or text layer."
            ),
            independence=independence,
        )

    # Found in tokens
    evidence_refs = [
        f"Page {t.page} (Source: {t.source}, BBox: {t.bbox}, Conf: {t.confidence or 'N/A'}): '{t.text}'"
        for t in matched_tokens[:3]
    ]

    if independence == EvidenceIndependence.SAME_SOURCE:
        explanation = (
            f"Field '{field_name}' ('{val}') was located in document text, but ONLY by the same OCR engine "
            f"used for extraction ({matched_tokens[0].source}). Because same-source evidence cannot self-certify, "
            "this field is classified as Uncertain rather than Supported."
        )
    else:
        explanation = (
            f"Field '{field_name}' ('{val}') is verified and grounded in independent evidence tokens "
            f"({len(matched_tokens)} occurrences found, e.g. via {matched_tokens[0].source})."
        )

    return VerificationCheck(
        check_id=check_id,
        applies=True,
        status="passed",
        evidence_refs=evidence_refs,
        plain_explanation=explanation,
        independence=independence,
    )
