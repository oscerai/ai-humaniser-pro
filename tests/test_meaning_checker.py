"""Tests for meaning_checker.py — all proxy calls mocked."""
from unittest.mock import patch, MagicMock
import json
import pytest


def _mock_proxy_response(text: str):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"content": [{"text": text}]}).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_identical_text_preserved():
    from meaning_checker import check_meaning_preserved
    result = check_meaning_preserved(
        "The risk assessment was conducted per ISO 13485.",
        "The risk assessment was conducted per ISO 13485.",
    )
    assert result["preserved"] is True
    assert "unchanged" in result["reason"].lower()


def test_meaning_changed_detected():
    from meaning_checker import check_meaning_preserved
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _mock_proxy_response("CHANGED: Requirement changed from mandatory to optional.")
        result = check_meaning_preserved(
            "Verification is required before release.",
            "Verification is optional before release.",
        )
    assert result["preserved"] is False
    assert "optional" in result["reason"].lower()


def test_proxy_failure_returns_preserved():
    from meaning_checker import check_meaning_preserved
    with patch("urllib.request.urlopen", side_effect=OSError("connection refused")):
        result = check_meaning_preserved(
            "The device shall comply with Annex I.",
            "The device must comply with Annex I.",
        )
    assert result["preserved"] is True
    assert "proxy unavailable" in result["reason"]


def test_preserved_response_parsed():
    from meaning_checker import check_meaning_preserved
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _mock_proxy_response("PRESERVED: Only connector phrase added at start.")
        result = check_meaning_preserved("Risk was assessed.", "This risk was assessed.")
    assert result["preserved"] is True
    assert "connector" in result["reason"].lower()


def test_empty_original_returns_preserved():
    from meaning_checker import check_meaning_preserved
    result = check_meaning_preserved("", "Some rewritten text here.")
    assert result["preserved"] is True
