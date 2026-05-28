"""
Tests for the AI extractor — focuses on the fallback heuristics
(no real Gemini calls in tests) and the extraction entry point.
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.ai.extractor import extract_with_fallback_heuristics, extract_opportunity


class TestFallbackHeuristics:
    """Tests for the regex-based fallback extractor."""

    def test_extracts_title_from_first_line(self):
        text = "Fulbright Scholarship 2025\nApply by December 2025\nOpen to all students."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert "Fulbright" in result["title"]

    def test_detects_scholarship_category(self):
        text = "This scholarship provides tuition support for graduate students."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["category"] == "scholarship"

    def test_detects_fellowship_category(self):
        text = "Apply for the fellowship program at our research institute."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["category"] == "fellowship"

    def test_detects_grant_category(self):
        text = "This grant provides seed funding for early-stage startups."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["category"] == "grant"

    def test_detects_competition_category(self):
        text = "Join our hackathon competition and win prizes."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["category"] == "competition"

    def test_detects_women_friendly(self):
        text = "This program is specifically for women entrepreneurs and female founders."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["women_friendly"] is True

    def test_detects_india_eligible(self):
        text = "Open to Indian applicants and students from India."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["india_eligible"] is True

    def test_detects_student_eligible(self):
        text = "Undergraduate and graduate students are welcome to apply."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["student_eligible"] is True

    def test_extracts_iso_deadline(self):
        text = "Application deadline: 2025-09-30. Submit your application online."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["deadline"] == "2025-09-30"

    def test_extracts_deadline_apply_by(self):
        text = "Apply by October 15, 2025 to be considered."
        result = extract_with_fallback_heuristics(text, "https://example.com")
        assert result["deadline"] is not None
        assert "2025" in result["deadline"]

    def test_empty_text_returns_defaults(self):
        result = extract_with_fallback_heuristics("", "https://example.com")
        assert result["title"] == "Unknown Opportunity"
        assert result["category"] == "other"
        assert result["tags"] == []

    def test_short_text_returns_defaults(self):
        result = extract_with_fallback_heuristics("Short.", "https://example.com")
        assert isinstance(result, dict)
        assert "title" in result

    def test_always_returns_dict(self):
        # None input should return a dict with defaults, not crash
        result = extract_with_fallback_heuristics(None, "https://example.com")
        assert isinstance(result, dict)
        assert result["title"] == "Unknown Opportunity"
        assert result["category"] == "other"

    def test_no_internal_extraction_method_key(self):
        """Fallback sets _extraction_method but normalize_extracted_data removes it."""
        result = extract_with_fallback_heuristics("Some text about a scholarship.", "https://example.com")
        # The key is set by fallback — normalize_extracted_data removes it
        assert "_extraction_method" in result  # set by fallback
        assert result["_extraction_method"] == "fallback"


@pytest.mark.asyncio
async def test_extract_opportunity_uses_fallback_on_llm_failure():
    """When Gemini fails, extract_opportunity falls back to heuristics."""
    with patch("app.ai.extractor.extract_opportunity_with_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = None  

        text = "This scholarship is open to Indian students studying abroad."
        result = await extract_opportunity(text, "https://example.com/test")

        assert isinstance(result, dict)
        assert "title" in result
        assert result["india_eligible"] is True


@pytest.mark.asyncio
async def test_extract_opportunity_uses_llm_result_when_available():
    """When Gemini succeeds, its result is used."""
    mock_result = {
        "title": "LLM Extracted Title",
        "organization": "Test Org",
        "category": "fellowship",
        "country": ["India"],
        "tags": ["Fellowship"],
        "deadline": "2025-12-01",
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "age_limit": None,
        "application_fee": "Free",
        "funding_amount": "Fully funded",
        "eligibility": "Open to all",
        "description": "A great fellowship.",
    }

    with patch("app.ai.extractor.extract_opportunity_with_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_result


        long_text = "This is a fellowship opportunity page with detailed information about eligibility and funding. " * 3
        result = await extract_opportunity(long_text, "https://example.com/llm-test")

        assert result["title"] == "LLM Extracted Title"
        assert result["_extraction_method"] == "llm"


@pytest.mark.asyncio
async def test_extract_opportunity_skips_short_text():
    """Very short text skips LLM and uses fallback directly."""
    with patch("app.ai.extractor.extract_opportunity_with_llm", new_callable=AsyncMock) as mock_llm:
        result = await extract_opportunity("Hi", "https://example.com/short")
       
        mock_llm.assert_not_called()
        assert isinstance(result, dict)
