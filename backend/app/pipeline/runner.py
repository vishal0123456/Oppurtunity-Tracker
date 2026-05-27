"""
Pipeline Runner — orchestrates the full scrape → extract → normalize → store cycle.

Flow:
1. For each scraper, fetch listing URLs
2. For each URL, check if already in DB (dedup)
3. Fetch page text
4. Run AI extraction
5. Normalize and validate data
6. Save to DB
7. Mark expired opportunities
"""
import asyncio
import logging
from datetime import date
from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.scraper import get_all_scrapers
from app.ai.extractor import extract_opportunity
from app.ai.categorizer import normalize_extracted_data
from app.pipeline.deduplicator import is_duplicate, get_existing_by_url
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)


async def save_opportunity(db: AsyncSession, data: dict, url: str, source_name: str) -> Optional[Opportunity]:
    """
    Save a new opportunity or update an existing one.
    Returns the saved Opportunity or None on failure.
    """
    try:
        # Parse deadline string to date object
        deadline = None
        raw_deadline = data.get("deadline")
        if raw_deadline:
            try:
                from datetime import datetime
                if isinstance(raw_deadline, str):
                    # Try ISO format first
                    deadline = datetime.strptime(raw_deadline[:10], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                logger.debug(f"Could not parse deadline: {raw_deadline}")

        # Check for existing record to update
        existing = await get_existing_by_url(db, url)

        if existing:
            # Update fields that may have changed
            existing.deadline = deadline or existing.deadline
            existing.is_expired = existing.is_expired
            existing.updated_at = date.today()
            await db.flush()
            logger.debug(f"Updated existing opportunity: {existing.title}")
            return existing

        # Create new opportunity
        opp = Opportunity(
            title=data.get("title", "Unknown Opportunity")[:500],
            organization=data.get("organization", "")[:300] if data.get("organization") else None,
            description=data.get("description"),
            category=data.get("category", "other"),
            tags=data.get("tags", []),
            country=data.get("country", []),
            is_remote=bool(data.get("is_remote", False)),
            women_friendly=bool(data.get("women_friendly", False)),
            india_eligible=bool(data.get("india_eligible", False)),
            student_eligible=bool(data.get("student_eligible", False)),
            age_limit=data.get("age_limit"),
            eligibility=data.get("eligibility"),
            funding_amount=data.get("funding_amount"),
            application_fee=data.get("application_fee"),
            link=url,
            source_url=url,
            source_name=source_name,
            deadline=deadline,
            is_expired=False,
        )

        db.add(opp)
        await db.flush()
        logger.info(f"Saved new opportunity: {opp.title}")
        return opp

    except Exception as e:
        logger.error(f"Failed to save opportunity from {url}: {e}")
        await db.rollback()
        return None


async def mark_expired_opportunities(db: AsyncSession):
    """Mark all opportunities whose deadline has passed as expired."""
    today = date.today()
    result = await db.execute(
        update(Opportunity)
        .where(Opportunity.deadline < today, Opportunity.is_expired == False)
        .values(is_expired=True)
    )
    count = result.rowcount
    if count > 0:
        logger.info(f"Marked {count} opportunities as expired.")


async def run_pipeline(max_per_scraper: int = 30) -> dict:
    """
    Main pipeline entry point.
    Returns a summary dict with counts.
    """
    logger.info("=" * 60)
    logger.info("PIPELINE STARTED")
    logger.info("=" * 60)

    stats = {
        "scrapers_run": 0,
        "urls_found": 0,
        "duplicates_skipped": 0,
        "extraction_failures": 0,
        "saved": 0,
        "errors": 0,
    }

    scrapers = get_all_scrapers()

    async with AsyncSessionLocal() as db:
        for scraper in scrapers:
            logger.info(f"Running scraper: {scraper.source_name}")
            stats["scrapers_run"] += 1

            try:
                urls = await scraper.fetch_listing_urls()
                urls = urls[:max_per_scraper]
                stats["urls_found"] += len(urls)
                logger.info(f"[{scraper.source_name}] Processing {len(urls)} URLs")

            except Exception as e:
                logger.error(f"[{scraper.source_name}] Listing fetch failed: {e}")
                stats["errors"] += 1
                continue

            for url in urls:
                try:
                    # Quick dedup check before fetching the full page
                    if await is_duplicate(db, url, "", None):
                        stats["duplicates_skipped"] += 1
                        continue

                    # Fetch page content
                    raw_text = await scraper.fetch_page_text(url)
                    if not raw_text:
                        logger.warning(f"No text fetched from: {url}")
                        stats["extraction_failures"] += 1
                        continue

                    # AI extraction
                    extracted = await extract_opportunity(raw_text, url)
                    if not extracted or not extracted.get("title"):
                        stats["extraction_failures"] += 1
                        continue

                    # Normalize and enrich
                    normalized = normalize_extracted_data(extracted)

                    # Full dedup check with title
                    if await is_duplicate(db, url, normalized.get("title", ""), normalized.get("organization")):
                        stats["duplicates_skipped"] += 1
                        continue

                    # Save to DB
                    saved = await save_opportunity(db, normalized, url, scraper.source_name)
                    if saved:
                        stats["saved"] += 1

                    # Small delay to be respectful to servers and avoid rate limits
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"Error processing URL {url}: {e}")
                    stats["errors"] += 1
                    continue

        # Commit all changes
        await db.commit()

        # Mark expired opportunities
        await mark_expired_opportunities(db)
        await db.commit()

    logger.info("=" * 60)
    logger.info(f"PIPELINE COMPLETE: {stats}")
    logger.info("=" * 60)
    return stats


if __name__ == "__main__":
    """Allow running the pipeline directly: python -m app.pipeline.runner"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    asyncio.run(run_pipeline())
