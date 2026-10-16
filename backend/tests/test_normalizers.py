"""Unit tests for amount and date normalizers."""

from backend.app.extraction.normalizers import normalize_amount, normalize_date


def test_amount_normalizer_indian_lakhs():
    val, cur, _ = normalize_amount("₹ 1,23,456.78")
    assert val == 123456.78
    assert cur == "INR"

    val, cur, _ = normalize_amount("Rs. 15,00,000.00")
    assert val == 1500000.00
    assert cur == "INR"


def test_amount_normalizer_international():
    val, cur, _ = normalize_amount("$ 1,234,567.89")
    assert val == 1234567.89
    assert cur == "USD"

    val, cur, _ = normalize_amount("€ 450.50")
    assert val == 450.50
    assert cur == "EUR"


def test_amount_normalizer_negative_and_brackets():
    val, cur, _ = normalize_amount("(1,500.00)")
    assert val == -1500.00

    val, cur, _ = normalize_amount("-2,400.50")
    assert val == -2400.50

    val, cur, _ = normalize_amount("750.00 DR")
    assert val == -750.00


def test_date_normalizer_iso():
    dt, snippet, ambiguous = normalize_date("Transaction on 2023-11-25 settled")
    assert dt == "2023-11-25"
    assert ambiguous is False


def test_date_normalizer_textual_month():
    dt, snippet, ambiguous = normalize_date("Pay Date: 28-Feb-2024")
    assert dt == "2024-02-28"
    assert ambiguous is False

    dt, snippet, ambiguous = normalize_date("Dated October 15, 2023")
    assert dt == "2023-10-15"
    assert ambiguous is False


def test_date_normalizer_ambiguity():
    # Day > 12: unambiguously DD/MM/YYYY
    dt, snippet, ambiguous = normalize_date("25/04/2023")
    assert dt == "2023-04-25"
    assert ambiguous is False

    # Both <= 12: should flag ambiguous=True
    dt, snippet, ambiguous = normalize_date("05/06/2023")
    assert dt == "2023-06-05"
    assert ambiguous is True
