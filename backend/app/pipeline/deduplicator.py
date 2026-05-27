"""
Deduplication logic for the opportunity pipeline.

Strategy:
1. Primary: exact URL match (fastest, most reliable)
2. Secondary: normalized title + organization fuzzy match (catches reposts)
"""
import logging
import re
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Normalize text for comparison — lowercase, strip punctuation/spaces."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


async def is_duplicate(db: AsyncSession, url: str, title: str, organization: Optional[str] = None) -> bool:
    """
    Check if an opportunity already exists in the database.
    Returns True if it's a duplicate.
    """
    # 1. Exact URL match
    result = await db.execute(
        select(Opportunity).where(Opportunity.link == url)
    )
    if result.scalar_one_or_none():
        logger.debug(f"Duplicate found by URL: {url}")
        return True

    # 2. Title + organization fuzzy match (normalized)
    if title:
        norm_title = normalize_text(title)
        # Fetch recent opportunities with similar titles
        result = await db.execute(
            select(Opportunity).where(
                func.lower(Opportunity.title).contains(norm_title[:50])
            ).limit(5)
        )
        existing = result.scalars().all()

        for opp in existing:
            existing_norm = normalize_text(opp.title)
            # Simple similarity: if 80%+ of words match
            title_words = set(norm_title.split())
            existing_words = set(existing_norm.split())
            if title_words and existing_words:
                overlap = len(title_words & existing_words)
                similarity = overlap / max(len(title_words), len(existing_words))
                if similarity >= 0.8:
                    # Also check organization if available
                    if organization and opp.organization:
                        if normalize_text(organization) == normalize_text(opp.organization):
                            logger.debug(f"Duplicate found by title+org similarity: {title}")
                            return True
                    elif similarity >= 0.9:
                        logger.debug(f"Duplicate found by title similarity ({similarity:.0%}): {title}")
                        return True

    return False


async def get_existing_by_url(db: AsyncSession, url: str) -> Optional[Opportunity]:
    """Fetch an existing opportunity by URL for update."""
    result = await db.execute(
        select(Opportunity).where(Opportunity.link == url)
    )
    return result.scalar_one_or_none()
