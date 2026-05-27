"""
Scraper for additional global opportunity sources:
- UN Volunteers (unv.org)
- Devex (devex.com) — international development opportunities
- F6S (f6s.com) — startup programs and accelerators
- Eventbrite (via RSS) — conferences and exhibitions

These complement OpportunityDesk and YouthOpportunities with more
startup/VC/conference/exhibition coverage.
"""
import logging
from typing import List
from bs4 import BeautifulSoup
from app.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class F6SStartupScraper(BaseScraper):
    """
    Scrapes F6S.com for startup programs, accelerators, and grants.
    F6S is one of the largest startup program platforms globally.
    """
    source_name = "F6S"
    base_url = "https://www.f6s.com"

    LISTING_URLS = [
        "https://www.f6s.com/programs",
        "https://www.f6s.com/programs?type=accelerator",
        "https://www.f6s.com/programs?type=grant",
    ]

    async def fetch_listing_urls(self) -> List[str]:
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
        return unique_urls[:20]

    def _parse_listing(self, soup: BeautifulSoup) -> List[str]:
        urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # F6S program pages follow /program/<name> pattern
            if "/program/" in href and "f6s.com" in href and href not in urls:
                urls.append(href)
            elif href.startswith("/program/"):
                full = f"https://www.f6s.com{href}"
                if full not in urls:
                    urls.append(full)
        return urls


class DevexOpportunityScraper(BaseScraper):
    """
    Scrapes Devex.com for international development jobs, grants, and programs.
    Covers UN, NGO, government, and research opportunities globally.
    """
    source_name = "Devex"
    base_url = "https://www.devex.com"

    LISTING_URLS = [
        "https://www.devex.com/funding",
        "https://www.devex.com/news/funding",
    ]

    async def fetch_listing_urls(self) -> List[str]:
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
        return unique_urls[:20]

    def _parse_listing(self, soup: BeautifulSoup) -> List[str]:
        urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "devex.com" in href and ("/news/" in href or "/funding/" in href) and href not in urls:
                urls.append(href)
            elif href.startswith("/news/") or href.startswith("/funding/"):
                full = f"https://www.devex.com{href}"
                if full not in urls:
                    urls.append(full)
        return urls
