"""
AI Categorizer — enriches extracted opportunity data with additional tags
and validates/normalizes the category field.
"""
import logging
from typing import List

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {
    "scholarship", "fellowship", "accelerator", "vc_program", "grant",
    "competition", "conference", "exhibition", "exchange_program",
    "travel_program", "government_scheme", "giveaway", "other"
}

VALID_TAGS = {
    "AI", "Startup", "Women", "Research", "Design", "MBA", "Engineering",
    "Climate", "Travel", "Social Impact", "Hackathon", "Student", "Founder",
    "Grant", "Fellowship", "Scholarship", "Tech", "Health", "Education",
    "Finance", "Arts", "Sports", "Leadership", "Government"
}

TAG_KEYWORD_MAP = {
    "AI": ["artificial intelligence", "machine learning", "deep learning", "nlp", "ai startup", "llm"],
    "Startup": ["startup", "entrepreneur", "venture", "founder", "early-stage"],
    "Women": ["women", "female", "girl", "woman founder", "women-led"],
    "Research": ["research", "phd", "doctoral", "academic", "scientist", "lab"],
    "Design": ["design", "ux", "ui", "creative", "product design"],
    "MBA": ["mba", "business school", "management"],
    "Engineering": ["engineering", "stem", "computer science", "software", "hardware"],
    "Climate": ["climate", "sustainability", "green", "environment", "clean energy", "carbon"],
    "Travel": ["travel", "exchange", "abroad", "international", "visa"],
    "Social Impact": ["social impact", "ngo", "nonprofit", "community", "social enterprise"],
    "Hackathon": ["hackathon", "hack", "buildathon", "sprint"],
    "Student": ["student", "undergraduate", "graduate", "university", "college"],
    "Founder": ["founder", "co-founder", "ceo", "startup founder"],
    "Grant": ["grant", "funding", "seed", "award money"],
    "Fellowship": ["fellowship", "fellow"],
    "Scholarship": ["scholarship", "tuition", "academic award"],
    "Tech": ["technology", "tech", "software", "saas", "platform"],
    "Health": ["health", "medical", "biotech", "healthcare", "wellness"],
    "Education": ["education", "edtech", "learning", "school"],
    "Finance": ["fintech", "finance", "banking", "investment"],
    "Arts": ["arts", "music", "film", "creative arts", "culture"],
    "Leadership": ["leadership", "leader", "executive", "management"],
    "Government": ["government", "ministry", "public sector", "policy"],
}


def normalize_category(raw_category: str) -> str:
    """Normalize and validate category string."""
    if not raw_category:
        return "other"
    normalized = raw_category.lower().strip().replace(" ", "_").replace("-", "_")
    return normalized if normalized in VALID_CATEGORIES else "other"


def enrich_tags(extracted_data: dict) -> List[str]:
    """
    Combine LLM-extracted tags with rule-based keyword matching.
    Returns a deduplicated, validated list of tags.
    """
    llm_tags = set()
    for tag in (extracted_data.get("tags") or []):
        if tag in VALID_TAGS:
            llm_tags.add(tag)

    searchable = " ".join(filter(None, [
        extracted_data.get("title", ""),
        extracted_data.get("description", ""),
        extracted_data.get("eligibility", ""),
        extracted_data.get("organization", ""),
        extracted_data.get("category", ""),
    ])).lower()

    rule_tags = set()
    for tag, keywords in TAG_KEYWORD_MAP.items():
        if any(kw in searchable for kw in keywords):
            rule_tags.add(tag)

    category = extracted_data.get("category", "")
    category_tag_map = {
        "scholarship": "Scholarship",
        "fellowship": "Fellowship",
        "grant": "Grant",
        "competition": "Hackathon",
        "accelerator": "Startup",
    }
    if category in category_tag_map:
        rule_tags.add(category_tag_map[category])

    if extracted_data.get("women_friendly"):
        rule_tags.add("Women")
    if extracted_data.get("student_eligible"):
        rule_tags.add("Student")

    all_tags = list(llm_tags | rule_tags)
    logger.debug(f"Tags enriched: {all_tags}")
    return all_tags


def normalize_extracted_data(data: dict) -> dict:
    """
    Normalize and validate all fields from the extraction result.
    Ensures types are correct before DB insertion.
    """
    data["category"] = normalize_category(data.get("category", ""))
    data["tags"] = enrich_tags(data)

    for field in ["country", "tags"]:
        if not isinstance(data.get(field), list):
            data[field] = []

    for field in ["is_remote", "women_friendly", "india_eligible", "student_eligible"]:
        val = data.get(field)
        if isinstance(val, str):
            data[field] = val.lower() in ("true", "yes", "1")
        elif val is None:
            data[field] = False

    data.pop("_extraction_method", None)
    return data
