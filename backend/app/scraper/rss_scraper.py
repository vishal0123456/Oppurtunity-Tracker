"""
RSS Feed Scraper — fetches opportunities from RSS/Atom feeds.
Covers many sources at once with minimal code.

Sources cover:
- Scholarships & Fellowships (global)
- Startup & VC programs
- Research opportunities
- Women-focused programs
- India-specific opportunities
- Africa / Middle East / Asia opportunities
- Conferences & exhibitions
- Government grants
"""
import logging
import feedparser
from typing import List
from app.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Curated list of RSS feeds for opportunities — grouped by category
RSS_FEEDS = [
    # ── Scholarships & Fellowships ──────────────────────────────────────────
    {"url": "https://opportunitydesk.org/feed/",                                    "source": "OpportunityDesk"},
    {"url": "https://www.scholars4dev.com/feed/",                                   "source": "Scholars4Dev"},
    {"url": "https://www.afterschoolafrica.com/feed/",                              "source": "AfterSchoolAfrica"},
    {"url": "https://www.opportunitiesforafricans.com/feed/",                       "source": "OpportunitiesForAfricans"},

    # ── Startup, VC & Accelerators ──────────────────────────────────────────
    {"url": "https://techcrunch.com/tag/startup/feed/",                             "source": "TechCrunch Startups"},
    {"url": "https://venturebeat.com/feed/",                                        "source": "VentureBeat"},
    {"url": "https://www.eu-startups.com/feed/",                                    "source": "EU Startups"},
    {"url": "https://yourstory.com/feed",                                           "source": "YourStory India"},

    # ── Research & Academia ─────────────────────────────────────────────────
    {"url": "https://www.nature.com/nature/articles?type=career-column&format=rss", "source": "Nature Careers"},
    {"url": "https://www.researchprofessionalnews.com/rss/",                        "source": "Research Professional"},

    # ── Women & Diversity ───────────────────────────────────────────────────
    {"url": "https://www.womenforhire.com/feed/",                                   "source": "Women For Hire"},

    # ── General Opportunities ───────────────────────────────────────────────
    {"url": "https://www.idealist.org/en/jobs?rss=1",                               "source": "Idealist"},
    {"url": "https://www.unglobalcompact.org/news/feed",                            "source": "UN Global Compact"},

    # ── India-specific ──────────────────────────────────────────────────────
    {"url": "https://www.startupindia.gov.in/content/sih/en/rss.xml",              "source": "Startup India"},

    # ── Conferences & Events ────────────────────────────────────────────────
    {"url": "https://www.eventbrite.com/d/online/free--events/rss/",               "source": "Eventbrite Free Events"},

    # ── Climate & Social Impact ─────────────────────────────────────────────
    {"url": "https://www.greenbiz.com/feeds/news",                                  "source": "GreenBiz"},
]


class RSSFeedScraper(BaseScraper):
    source_name = "RSSFeeds"
    base_url = ""

    async def fetch_listing_urls(self) -> List[str]:
        """Parse all RSS feeds and return article URLs."""
        all_urls = []

        for feed_config in RSS_FEEDS:
            try:
                urls = await self._parse_feed(feed_config["url"], feed_config["source"])
                all_urls.extend(urls)
            except Exception as e:
                logger.error(f"[RSS] Failed to parse feed {feed_config['url']}: {e}")

        unique_urls = list(dict.fromkeys(all_urls))
        logger.info(f"[RSS] Total unique URLs from all feeds: {len(unique_urls)}")
        return unique_urls[:80]  # Increased cap to match more feeds

    async def _parse_feed(self, feed_url: str, source_name: str) -> List[str]:
        """Parse a single RSS feed and return entry URLs."""
        try:
            # feedparser is synchronous but fast
            feed = feedparser.parse(feed_url)

            if feed.bozo and not feed.entries:
                logger.warning(f"[RSS] Feed parse error for {feed_url}: {feed.bozo_exception}")
                return []

            urls = []
            for entry in feed.entries[:15]:  # Limit per feed
                link = entry.get("link", "")
                if link and link.startswith("http"):
                    urls.append(link)

            logger.info(f"[RSS:{source_name}] Found {len(urls)} entries")
            return urls

        except Exception as e:
            logger.error(f"[RSS] Error parsing {feed_url}: {e}")
            return []
