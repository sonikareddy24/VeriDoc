"""Financial amount and date normalizers with edge-case handling.
Handles Indian lakh grouping (e.g. 1,23,456.78), international grouping (123,456.78),
bracket negative notation (e.g. (1,500.00)), currency symbols, and ambiguous dates.
"""

import re
from datetime import datetime
from typing import Optional, Tuple

CURRENCY_MAP = {
    "₹": "INR",
    "rs.": "INR",
    "rs": "INR",
    "inr": "INR",
    "$": "USD",
    "usd": "USD",
    "€": "EUR",
    "eur": "EUR",
    "£": "GBP",
    "gbp": "GBP",
    "a$": "AUD",
    "aud": "AUD",
    "c$": "CAD",
    "cad": "CAD",
    "sgd": "SGD",
    "aed": "AED",
}

MONTH_NAMES = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def normalize_amount(raw_text: Optional[str]) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """Normalize monetary string to (float_value, currency_code, raw_clean_str).

    Handles:
    - Currency prefixes/suffixes: '₹ 1,50,000.00', '1500 USD', '$ 2,450.50'
    - Indian lakh comma grouping: '12,34,567.89'
    - International grouping: '1,234,567.89'
    - Negative brackets: '(1,200.00)' -> -1200.00
    - Explicit signs: '-1,200.00', '+500.00'
    - Dr/Cr indicators: '500.00 DR' -> -500.00, '500.00 CR' -> 500.00
    """
    if not raw_text or not isinstance(raw_text, str):
        return None, None, None

    text = raw_text.strip()
    if not text:
        return None, None, None

    # Detect currency and remove it from text to prevent currency dot (e.g. 'Rs.') contaminating decimals
    currency: Optional[str] = None
    lower_text = text.lower()
    for symbol, code in sorted(CURRENCY_MAP.items(), key=lambda x: -len(x[0])):
        pattern = rf"(^|\s){re.escape(symbol)}(\s|$|[0-9])"
        if re.search(pattern, lower_text):
            currency = code
            # Remove the symbol from text
            text = re.sub(re.escape(symbol), " ", text, flags=re.IGNORECASE)
            break

    lower_text = text.lower()

    # Check for negative signs or brackets
    is_negative = False
    if text.startswith("(") and text.endswith(")"):
        is_negative = True
        text = text[1:-1].strip()
    elif text.startswith("-"):
        is_negative = True
        text = text[1:].strip()
    elif text.endswith("-"):
        is_negative = True
        text = text[:-1].strip()
    elif re.search(r"\b(dr|debit)\b", lower_text):
        is_negative = True

    # Strip currency symbols and letters, leaving digits, commas, dots
    cleaned = re.sub(r"[^\d.,]", "", text).strip()
    if not cleaned:
        return None, currency, None

    # Strip leading/trailing dots or commas that may be noise
    cleaned = cleaned.strip(".,")
    if not cleaned:
        return None, currency, None

    # Determine decimal separator
    if "." in cleaned and "," in cleaned:
        last_dot = cleaned.rfind(".")
        last_comma = cleaned.rfind(",")
        if last_dot > last_comma:
            # Comma is thousands/lakhs, dot is decimal: remove commas
            numeric_str = cleaned.replace(",", "")
        else:
            # European format: dot is thousands, comma is decimal
            numeric_str = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        parts = cleaned.split(",")
        if len(parts[-1]) == 2:
            # Likely decimal comma e.g. "1250,50"
            numeric_str = cleaned.replace(",", ".")
        else:
            # Thousands separator e.g. "1,250" or "1,25,000"
            numeric_str = cleaned.replace(",", "")
    else:
        numeric_str = cleaned

    try:
        val = float(numeric_str)
        if is_negative and val > 0:
            val = -val
        return round(val, 2), currency, numeric_str
    except ValueError:
        return None, currency, None


def normalize_date(raw_text: Optional[str]) -> Tuple[Optional[str], Optional[str], bool]:
    """Normalize date strings into ISO format YYYY-MM-DD.

    Returns:
        (iso_date, raw_snippet, is_ambiguous)
    If day and month are both <= 12 in numerical dates with slash/dash (e.g. '04/05/2023'),
    is_ambiguous is flagged True so the pipeline does not guess silently.
    """
    if not raw_text or not isinstance(raw_text, str):
        return None, None, False

    text = raw_text.strip()
    if not text:
        return None, None, False

    # Try ISO YYYY-MM-DD
    iso_match = re.search(r"\b(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\b", text)
    if iso_match:
        y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        try:
            dt = datetime(y, m, d)
            return dt.strftime("%Y-%m-%d"), iso_match.group(0), False
        except ValueError:
            pass

    # Try textual month: DD-Mon-YYYY or Mon DD, YYYY or DD Month YYYY
    text_month_match = re.search(
        r"\b(\d{1,2})[\s\-\./]+([A-Za-z]{3,9})[\s\-\.,]+(\d{4})\b", text
    )
    if text_month_match:
        d = int(text_month_match.group(1))
        m_name = text_month_match.group(2).lower()
        y = int(text_month_match.group(3))
        m = MONTH_NAMES.get(m_name)
        if m:
            try:
                dt = datetime(y, m, d)
                return dt.strftime("%Y-%m-%d"), text_month_match.group(0), False
            except ValueError:
                pass

    # Month DD, YYYY
    text_month_prefix = re.search(
        r"\b([A-Za-z]{3,9})[\s\-\.]+(\d{1,2})[\s\-\.,]+(\d{4})\b", text
    )
    if text_month_prefix:
        m_name = text_month_prefix.group(1).lower()
        d = int(text_month_prefix.group(2))
        y = int(text_month_prefix.group(3))
        m = MONTH_NAMES.get(m_name)
        if m:
            try:
                dt = datetime(y, m, d)
                return dt.strftime("%Y-%m-%d"), text_month_prefix.group(0), False
            except ValueError:
                pass

    # Numerical date: DD/MM/YYYY or MM/DD/YYYY
    num_match = re.search(r"\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b", text)
    if num_match:
        part1 = int(num_match.group(1))
        part2 = int(num_match.group(2))
        y = int(num_match.group(3))

        # Check ambiguity
        if part1 <= 12 and part2 <= 12:
            # Both can be month or day!
            try:
                dt = datetime(y, part2, part1)  # DD/MM/YYYY
                return dt.strftime("%Y-%m-%d"), num_match.group(0), True
            except ValueError:
                pass
        elif part1 > 12 and part2 <= 12:
            # Must be DD/MM/YYYY
            try:
                dt = datetime(y, part2, part1)
                return dt.strftime("%Y-%m-%d"), num_match.group(0), False
            except ValueError:
                pass
        elif part2 > 12 and part1 <= 12:
            # Must be MM/DD/YYYY (US style)
            try:
                dt = datetime(y, part1, part2)
                return dt.strftime("%Y-%m-%d"), num_match.group(0), False
            except ValueError:
                pass

    return None, None, False
