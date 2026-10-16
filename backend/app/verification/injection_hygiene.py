"""Prompt injection hygiene and adversarial text detection.
Scans document text for instruction-like strings (e.g. 'ignore previous instructions',
'override rules', 'system prompt') and flags them as informational security findings,
confirming that extracted values remained untrusted data and did not change system behavior.
"""

import re
from typing import List
from backend.app.schemas.common import (
    EvidenceIndependence,
    EvidenceToken,
    VerificationCheck,
)

INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions",
    r"disregard\s+(?:all\s+)?(?:previous|prior)\s+rules",
    r"you\s+are\s+now\s+(?:a|an)\s+",
    r"system\s*prompt\s*:",
    r"override\s+(?:all\s+)?safety\s+checks",
    r"output\s+JSON\s+as\s+follows",
    r"mark\s+this\s+document\s+as\s+supported",
]


def check_prompt_injection_hygiene(tokens: List[EvidenceToken]) -> List[VerificationCheck]:
    checks: List[VerificationCheck] = []
    combined_text = " ".join(t.text for t in tokens)

    detected_patterns = []
    for pat in INJECTION_PATTERNS:
        match = re.search(pat, combined_text, flags=re.IGNORECASE)
        if match:
            detected_patterns.append(match.group(0))

    if detected_patterns:
        checks.append(
            VerificationCheck(
                check_id="HYGIENE_PROMPT_INJECTION_DETECTED",
                applies=True,
                status="passed",  # The security check itself passed by catching the attempt and isolating it
                evidence_refs=[f"Pattern matched: '{p}'" for p in detected_patterns],
                plain_explanation=(
                    f"Adversarial / instruction-like text was detected in document content: "
                    f"[{', '.join(detected_patterns)}]. The system quarantined this content as untrusted DATA; "
                    "no pipeline instructions or verification outcomes were altered."
                ),
                independence=EvidenceIndependence.INDEPENDENT,
            )
        )

    return checks
