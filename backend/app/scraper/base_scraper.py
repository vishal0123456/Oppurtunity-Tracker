"""
Abstract base class for all scrapers.
Each scraper must implement fetch_listing_urls() and fetch_page_text().
"""
import logging
import httpx
from abc import ABC, abstractmethod
from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Honest bot identification — declared before DEFAULT_HEADERS uses it
SCRAPER_USER_AGENT = "OpportunityTrackerBot/1.0 (educational aggregator; links back to source)"

# Shared HTTP headers
DEFAULT_HEADERS = {
    "User-Agent": SCRAPER_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

REQUEST_TIMEOUT = 30  # seconds


def is_scraping_allowed(url: str) -> bool:
    """
    Check robots.txt before scraping a URL.
    Returns True if allowed or if robots.txt is unreachable.
    """
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        allowed = rp.can_fetch(SCRAPER_USER_AGENT, url)
        if not allowed:
            logger.warning(f"robots.txt disallows scraping: {url}")
        return allowed
    except Exception:
        # If robots.txt is unreachable, proceed (benefit of the doubt)
        return True


class BaseScraper(ABC):
    """Base class for all opportunity scrapers."""

    source_name: str = "unknown"
    base_url: str = ""

    @abstractmethod
    async def fetch_listing_urls(self) -> List[str]:
        """Return a list of individual opportunity URLs from the listing page."""
        ...

    async def fetch_page_text(self, url: str) -> Optional[str]:
        """
        Fetch a single opportunity page and return its cleaned text content.
        Checks robots.txt first. Returns None on failure or if disallowed.
        """
        if not is_scraping_allowed(url):
            logger.info(f"[{self.source_name}] Skipping (robots.txt): {url}")
            return None
        try:
            async with httpx.AsyncClient(
                headers=DEFAULT_HEADERS,
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return self._extract_text(response.text)
        except httpx.TimeoutException:
            logger.warning(f"[{self.source_name}] Timeout fetching: {url}")
        except httpx.HTTPStatusError as e:
            logger.warning(f"[{self.source_name}] HTTP {e.response.status_code} for: {url}")
        except Exception as e:
            logger.error(f"[{self.source_name}] Error fetching {url}: {e}")
        return None

    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch raw HTML (used by listing page parsers)."""
        try:
            async with httpx.AsyncClient(
                headers=DEFAULT_HEADERS,
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"[{self.source_name}] Error fetching HTML {url}: {e}")
        return None

    def _extract_text(self, html: str) -> str:
        """
        Extract clean readable text from HTML.
        Removes scripts, styles, nav, footer elements.
        """
        soup = BeautifulSoup(html, "lxml")

        # Remove noise elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
            tag.decompose()

        # Get text with reasonable spacing
        text = soup.get_text(separator="\n", strip=True)

        # Collapse excessive blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
