"""Tests for the AI Humaniser Pro modules: pipeline, known_new_contract_checker, profiles."""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest


# ---------------------------------------------------------------------------
# Unit tests — _split_paragraphs (pure function, no external dependencies)
# ---------------------------------------------------------------------------

class TestSplitParagraphs:
    """Tests for pipeline._split_paragraphs — the only truly pure function in the module."""

    def _fn(self):
        from pipeline import _split_paragraphs
        return _split_paragraphs

    def test_two_paragraphs(self):
        fn = self._fn()
        result = fn("Para one\n\nPara two")
        assert result == ["Para one", "Para two"]

    def test_empty_string_returns_empty(self):
        fn = self._fn()
        assert fn("") == []

    def test_single_paragraph(self):
        fn = self._fn()
        assert fn("Only one paragraph here.") == ["Only one paragraph here."]

    def test_whitespace_only_paragraphs_dropped(self):
        fn = self._fn()
        result = fn("Para one\n\n   \n\nPara two")
        assert result == ["Para one", "Para two"]

    def test_strips_leading_trailing_whitespace(self):
        fn = self._fn()
        result = fn("  Para one  \n\n  Para two  ")
        assert result == ["Para one", "Para two"]

    def test_three_paragraphs(self):
        fn = self._fn()
        result = fn("A\n\nB\n\nC")
        assert result == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# Integration tests — check_known_new (uses spaCy)
# ---------------------------------------------------------------------------

class TestCheckKnownNew:
    """Integration tests for known_new_contract_checker.check_known_new."""

    def test_returns_list_of_dicts(self):
        from known_new_contract_checker import check_known_new
        result = check_known_new([
            "The risk is significant. This matters for patient safety.",
            "Furthermore the device must demonstrate compliance.",
        ])
        assert isinstance(result, list)
        assert len(result) == 1
        assert all(k in result[0] for k in ["pair_index", "p_n_ending_concept", "p_n1_opening_concept", "reorderable"])

    def test_pair_index_is_zero_for_first_pair(self):
        from known_new_contract_checker import check_known_new
        result = check_known_new([
            "Risk management is essential for device safety.",
            "Compliance documentation supports the regulatory submission.",
        ])
        assert result[0]["pair_index"] == 0

    def test_empty_list_returns_empty(self):
        from known_new_contract_checker import check_known_new
        assert check_known_new([]) == []

    def test_single_paragraph_returns_empty(self):
        from known_new_contract_checker import check_known_new
        assert check_known_new(["Only one paragraph."]) == []

    def test_paragraphs_below_min_words_excluded(self):
        from known_new_contract_checker import check_known_new
        # "Hi" has 1 word < 4 minimum — both will be excluded → no pairs
        result = check_known_new(["Hi", "Bye"])
        assert result == []

    def test_reorderable_is_bool(self):
        from known_new_contract_checker import check_known_new
        result = check_known_new([
            "The device requires regular maintenance for safe operation.",
            "Furthermore manufacturers must document all risk control measures.",
        ])
        assert isinstance(result[0]["reorderable"], bool)


# ---------------------------------------------------------------------------
# Integration tests — PROTECTED_TERMS patch (key regression guard)
# ---------------------------------------------------------------------------

class TestProtectedTermsPatch:
    """Verify that the monkey-patch in profiles.regulatory prevents protected term drops."""

    def test_formal_profile_does_not_drop_demonstrate(self):
        from profiles.regulatory import PROTECTED_TERMS
        from texthumanize import humanize
        para = "The device shall demonstrate compliance with applicable standards."
        result = humanize(para, profile="formal", intensity=20)
        result_text = result.text if hasattr(result, "text") else str(result)
        violated = [
            t for t in PROTECTED_TERMS
            if t.lower() in para.lower() and t.lower() not in result_text.lower()
        ]
        assert violated == [], f"Protected terms dropped: {violated}"

    def test_protected_terms_count_above_68(self):
        from profiles.regulatory import PROTECTED_TERMS
        assert len(PROTECTED_TERMS) > 68

    def test_inflected_forms_present(self):
        from profiles.regulatory import PROTECTED_TERMS
        required = {"verifies", "validating", "maintains", "establishes", "complying"}
        missing = required - set(PROTECTED_TERMS)
        assert not missing, f"Missing inflected forms: {missing}"

    def test_modal_compounds_present(self):
        from profiles.regulatory import PROTECTED_TERMS
        required = {"shall not", "must not", "may not", "should not"}
        missing = required - set(PROTECTED_TERMS)
        assert not missing, f"Missing modal compounds: {missing}"
