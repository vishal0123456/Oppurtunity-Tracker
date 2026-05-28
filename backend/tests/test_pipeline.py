"""
Tests for the pipeline deduplicator and data normalization.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.pipeline.deduplicator import normalize_text, is_duplicate
from app.ai.categorizer import normalize_category, enrich_tags, normalize_extracted_data


# ── Deduplicator tests ──

class TestNormalizeText:
    def test_lowercases(self):
        assert normalize_text("Hello World") == "hello world"

    def test_strips_punctuation(self):
        assert normalize_text("Hello, World!") == "hello world"

    def test_collapses_whitespace(self):
        assert normalize_text("hello   world") == "hello world"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_none_returns_empty(self):
        assert normalize_text(None) == ""

    def test_mixed(self):
        result = normalize_text("  Fulbright  Fellowship 2025!  ")
        assert result == "fulbright fellowship 2025"


@pytest.mark.asyncio
async def test_is_duplicate_by_url(db_session):
    """Exact URL match is detected as duplicate."""
    from app.models.opportunity import Opportunity
    opp = Opportunity(
        title="Test Opp",
        link="https://example.com/dup-url",
        category="scholarship",
        tags=[],
        country=[],
    )
    db_session.add(opp)
    await db_session.flush()

    result = await is_duplicate(db_session, "https://example.com/dup-url", "Test Opp")
    assert result is True


@pytest.mark.asyncio
async def test_is_duplicate_new_url(db_session):
    """New URL is not a duplicate."""
    result = await is_duplicate(db_session, "https://example.com/brand-new", "Brand New Opportunity")
    assert result is False


@pytest.mark.asyncio
async def test_is_duplicate_fuzzy_title(db_session):
    """High title similarity is detected as duplicate."""
    from app.models.opportunity import Opportunity
    opp = Opportunity(
        title="Fulbright Foreign Student Program 2025",
        organization="US Department of State",
        link="https://example.com/fulbright-original",
        category="scholarship",
        tags=[],
        country=[],
    )
    db_session.add(opp)
    await db_session.flush()

    
    result = await is_duplicate(
        db_session,
        "https://example.com/fulbright-repost",
        "Fulbright Foreign Student Program 2025",
        "US Department of State",
    )
    assert result is True


# ── Categorizer tests ───

class TestNormalizeCategory:
    def test_valid_category(self):
        assert normalize_category("scholarship") == "scholarship"

    def test_valid_with_spaces(self):
        assert normalize_category("exchange program") == "exchange_program"

    def test_valid_with_hyphens(self):
        assert normalize_category("vc-program") == "vc_program"

    def test_invalid_returns_other(self):
        assert normalize_category("random_thing") == "other"

    def test_empty_returns_other(self):
        assert normalize_category("") == "other"

    def test_none_returns_other(self):
        assert normalize_category(None) == "other"

    def test_uppercase_normalized(self):
        assert normalize_category("FELLOWSHIP") == "fellowship"

    def test_all_valid_categories(self):
        valid = [
            "scholarship", "fellowship", "accelerator", "vc_program", "grant",
            "competition", "conference", "exhibition", "exchange_program",
            "travel_program", "government_scheme", "giveaway", "other"
        ]
        for cat in valid:
            assert normalize_category(cat) == cat


class TestEnrichTags:
    def test_llm_tags_preserved(self):
        data = {"tags": ["AI", "Startup"], "title": "", "description": ""}
        tags = enrich_tags(data)
        assert "AI" in tags
        assert "Startup" in tags

    def test_invalid_llm_tags_filtered(self):
        data = {"tags": ["NotATag", "AI"], "title": "", "description": ""}
        tags = enrich_tags(data)
        assert "NotATag" not in tags
        assert "AI" in tags

    def test_keyword_based_enrichment(self):
        data = {
            "tags": [],
            "title": "Machine Learning Research Fellowship",
            "description": "PhD research in deep learning and NLP.",
            "eligibility": "",
            "organization": "",
            "category": "fellowship",
        }
        tags = enrich_tags(data)
        assert "AI" in tags
        assert "Research" in tags
        assert "Fellowship" in tags

    def test_women_friendly_adds_women_tag(self):
        data = {
            "tags": [],
            "title": "Test",
            "description": "",
            "eligibility": "",
            "organization": "",
            "category": "grant",
            "women_friendly": True,
        }
        tags = enrich_tags(data)
        assert "Women" in tags

    def test_student_eligible_adds_student_tag(self):
        data = {
            "tags": [],
            "title": "Test",
            "description": "",
            "eligibility": "",
            "organization": "",
            "category": "scholarship",
            "student_eligible": True,
        }
        tags = enrich_tags(data)
        assert "Student" in tags

    def test_no_duplicate_tags(self):
        data = {
            "tags": ["AI", "Startup"],
            "title": "AI Startup Accelerator",
            "description": "For AI startups.",
            "eligibility": "",
            "organization": "",
            "category": "accelerator",
        }
        tags = enrich_tags(data)
        assert len(tags) == len(set(tags))


class TestNormalizeExtractedData:
    def test_normalizes_category(self):
        data = {"category": "SCHOLARSHIP", "tags": [], "country": []}
        result = normalize_extracted_data(data)
        assert result["category"] == "scholarship"

    def test_normalizes_boolean_strings(self):
        data = {
            "category": "grant",
            "tags": [],
            "country": [],
            "is_remote": "true",
            "women_friendly": "yes",
            "india_eligible": "false",
            "student_eligible": "1",
        }
        result = normalize_extracted_data(data)
        assert result["is_remote"] is True
        assert result["women_friendly"] is True
        assert result["india_eligible"] is False
        assert result["student_eligible"] is True

    def test_none_booleans_become_false(self):
        data = {
            "category": "grant",
            "tags": [],
            "country": [],
            "is_remote": None,
            "women_friendly": None,
        }
        result = normalize_extracted_data(data)
        assert result["is_remote"] is False
        assert result["women_friendly"] is False

    def test_removes_internal_fields(self):
        data = {
            "category": "grant",
            "tags": [],
            "country": [],
            "_extraction_method": "llm",
        }
        result = normalize_extracted_data(data)
        assert "_extraction_method" not in result

    def test_non_list_arrays_become_empty(self):
        data = {
            "category": "grant",
            "tags": "AI, Startup", 
            "country": None,
        }
        result = normalize_extracted_data(data)
        assert isinstance(result["tags"], list)
        assert isinstance(result["country"], list)
