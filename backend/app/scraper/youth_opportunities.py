"""
Scraper for YouthOpportunities.org (youthop.com) — global youth opportunity platform.
"""
import logging
from typing import List
from bs4 import BeautifulSoup
from app.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class YouthOpportunitiesScraper(BaseScraper):
    source_name = "YouthOpportunities"
    base_url = "https://youthop.com"

    LISTING_URLS = [
        "https://youthop.com/scholarships",
        "https://youthop.com/fellowships",
        "https://youthop.com/grants",
        "https://youthop.com/competitions",
        "https://youthop.com/exchange-programs",
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
                urls = self._parse_listing(soup)
                all_urls.extend(urls)
                logger.info(f"[{self.source_name}] Found {len(urls)} URLs from {listing_url}")

            except Exception as e:
                logger.error(f"[{self.source_name}] Failed to parse listing {listing_url}: {e}")

        unique_urls = list(dict.fromkeys(all_urls))
        logger.info(f"[{self.source_name}] Total unique URLs: {len(unique_urls)}")
        return unique_urls[:30]

    def _parse_listing(self, soup: BeautifulSoup) -> List[str]:
        """Extract opportunity links from youthop listing page."""
        urls = []

        # youthop uses card-style listings with direct links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if (
                "youthop.com" in href
                and "/opportunities/" in href
                and href not in urls
            ):
                urls.append(href)

        # Also check for relative URLs
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/opportunities/"):
                full_url = f"https://youthop.com{href}"
                if full_url not in urls:
                    urls.append(full_url)

        return urls
