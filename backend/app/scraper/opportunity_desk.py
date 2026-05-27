"""
Scraper for OpportunityDesk.org — one of the largest opportunity listing sites.
Fetches the latest opportunities from the homepage listing.
"""
import logging
from typing import List
from bs4 import BeautifulSoup
from app.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class OpportunityDeskScraper(BaseScraper):
    source_name = "OpportunityDesk"
    base_url = "https://opportunitydesk.org"

    # Pages to scrape from the listing
    LISTING_URLS = [
        "https://opportunitydesk.org/category/scholarships/",
        "https://opportunitydesk.org/category/fellowships/",
        "https://opportunitydesk.org/category/grants/",
        "https://opportunitydesk.org/category/competitions/",
        "https://opportunitydesk.org/category/conferences/",
    ]

    async def fetch_listing_urls(self) -> List[str]:
        """Scrape listing pages and return individual opportunity URLs."""
        all_urls = []

        for listing_url in self.LISTING_URLS:
            try:
                html = await self.fetch_html(listing_url)
                if not html:
                    continue

                soup = BeautifulSoup(html, "lxml")
                urls = self._parse_listing(soup, listing_url)
                all_urls.extend(urls)
                logger.info(f"[{self.source_name}] Found {len(urls)} URLs from {listing_url}")

            except Exception as e:
                logger.error(f"[{self.source_name}] Failed to parse listing {listing_url}: {e}")

        # Deduplicate
        unique_urls = list(dict.fromkeys(all_urls))
        logger.info(f"[{self.source_name}] Total unique URLs: {len(unique_urls)}")
        return unique_urls[:30]  # Limit per run to control API costs

    def _parse_listing(self, soup: BeautifulSoup, base: str) -> List[str]:
        """Extract article links from a listing page."""
        urls = []
        seen = set()

        # OpportunityDesk uses article tags with h2 > a links
        articles = soup.find_all("article")
        for article in articles:
            link_tag = article.find("a", href=True)
            if link_tag:
                href = link_tag["href"]
                if href.startswith("http") and "opportunitydesk.org" in href and href not in seen:
                    urls.append(href)
                    seen.add(href)

        # Fallback: find all post title links (only if article parsing found nothing)
        if not urls:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if (
                    "opportunitydesk.org" in href
                    and "/20" in href  # year in URL pattern
                    and href not in seen
                ):
                    urls.append(href)
                    seen.add(href)

        return urls
