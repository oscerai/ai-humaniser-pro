"""Tests for regulatory_classifier.py — no API calls, pure keyword matching."""
import os
import pytest


def test_regulatory_text_classified_true():
    from regulatory_classifier import is_regulated_document
    assert is_regulated_document(
        "This product shall comply with ISO 13485 and EU MDR Annex I requirements."
    ) is True


def test_general_text_classified_false():
    from regulatory_classifier import is_regulated_document
    assert is_regulated_document(
        "Today I went to the market and bought some apples and oranges for my lunch."
    ) is False


def test_single_keyword_false():
    from regulatory_classifier import is_regulated_document
    # "shall" alone is only 1 keyword — below threshold
    assert is_regulated_document("The team shall complete the project by Friday.") is False


def test_rmr_text_classified_true():
    from regulatory_classifier import is_regulated_document
    extract_path = os.path.join(os.path.dirname(__file__), "..", "test-regulatory-extract.txt")
    if not os.path.exists(extract_path):
        pytest.skip("test-regulatory-extract.txt not present — run Step 1 first")
    sample = open(extract_path).read()[:500]
    assert is_regulated_document(sample) is True


def test_empty_text_false():
    from regulatory_classifier import is_regulated_document
    assert is_regulated_document("") is False
    assert is_regulated_document("   ") is False


def test_iec62304_classified_true():
    from regulatory_classifier import is_regulated_document
    assert is_regulated_document(
        "Software lifecycle processes shall conform to IEC 62304 requirements for medical device software."
    ) is True
