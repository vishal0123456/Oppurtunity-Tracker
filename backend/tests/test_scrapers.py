"""
Tests for the scraper base class and individual scrapers.
Uses mocked HTTP responses — no real network calls.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bs4 import BeautifulSoup

from app.scraper.base_scraper import BaseScraper, is_scraping_allowed
from app.pipeline.deduplicator import normalize_text
from app.scraper.opportunity_desk import OpportunityDeskScraper
from app.scraper.youth_opportunities import YouthOpportunitiesScraper
from app.scraper.rss_scraper import RSSFeedScraper
from app.scraper import get_all_scrapers




def test_scraping_allowed_returns_true_on_error():
    """If robots.txt is unreachable, scraping is allowed by default."""
    with patch("app.scraper.base_scraper.RobotFileParser") as mock_rfp:
        mock_rfp.return_value.read.side_effect = Exception("Network error")
        result = is_scraping_allowed("https://example.com/page")
        assert result is True


def test_scraping_allowed_respects_disallow():
    """If robots.txt disallows, returns False."""
    with patch("app.scraper.base_scraper.RobotFileParser") as mock_rfp:
        instance = mock_rfp.return_value
        instance.read.return_value = None
        instance.can_fetch.return_value = False
        result = is_scraping_allowed("https://example.com/disallowed")
        assert result is False


def test_scraping_allowed_respects_allow():
    """If robots.txt allows, returns True."""
    with patch("app.scraper.base_scraper.RobotFileParser") as mock_rfp:
        instance = mock_rfp.return_value
        instance.read.return_value = None
        instance.can_fetch.return_value = True
        result = is_scraping_allowed("https://example.com/allowed")
        assert result is True




class ConcreteScraper(BaseScraper):
    """Minimal concrete implementation for testing BaseScraper."""
    source_name = "TestScraper"
    base_url = "https://example.com"

    async def fetch_listing_urls(self):
        return []


def test_extract_text_removes_scripts():
    scraper = ConcreteScraper()
    html = "<html><body><script>alert('x')</script><p>Hello World</p></body></html>"
    text = scraper._extract_text(html)
    assert "alert" not in text
    assert "Hello World" in text


def test_extract_text_removes_nav():
    scraper = ConcreteScraper()
    html = "<html><body><nav>Menu</nav><main><p>Content</p></main></body></html>"
    text = scraper._extract_text(html)
    assert "Menu" not in text
    assert "Content" in text


def test_extract_text_collapses_blank_lines():
    scraper = ConcreteScraper()
    html = "<html><body><p>Line 1</p><p>   </p><p>Line 2</p></body></html>"
    text = scraper._extract_text(html)
    lines = [l for l in text.split("\n") if l.strip()]
    assert "Line 1" in lines
    assert "Line 2" in lines


@pytest.mark.asyncio
async def test_fetch_page_text_skips_disallowed():
    """fetch_page_text returns None when robots.txt disallows."""
    scraper = ConcreteScraper()
    with patch("app.scraper.base_scraper.is_scraping_allowed", return_value=False):
        result = await scraper.fetch_page_text("https://example.com/disallowed")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_page_text_returns_none_on_timeout():
    """fetch_page_text returns None on timeout."""
    import httpx
    scraper = ConcreteScraper()
    with patch("app.scraper.base_scraper.is_scraping_allowed", return_value=True):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.TimeoutException("timeout")
            result = await scraper.fetch_page_text("https://example.com/timeout")
    assert result is None



def test_opportunity_desk_parse_listing_articles():
    """Parses article links from OpportunityDesk HTML."""
    scraper = OpportunityDeskScraper()
    html = """
    <html><body>
        <article><a href="https://opportunitydesk.org/2025/01/test-scholarship/">Test</a></article>
        <article><a href="https://opportunitydesk.org/2025/02/another-grant/">Another</a></article>
    </body></html>
    """
    soup = BeautifulSoup(html, "lxml")
    urls = scraper._parse_listing(soup, "https://opportunitydesk.org/category/scholarships/")
    assert len(urls) == 2
    assert all("opportunitydesk.org" in u for u in urls)


def test_opportunity_desk_parse_listing_deduplicates():
    """Duplicate URLs are removed."""
    scraper = OpportunityDeskScraper()
    html = """
    <html><body>
        <article><a href="https://opportunitydesk.org/2025/01/test/">Test</a></article>
        <article><a href="https://opportunitydesk.org/2025/01/test/">Test</a></article>
    </body></html>
    """
    soup = BeautifulSoup(html, "lxml")
    urls = scraper._parse_listing(soup, "https://opportunitydesk.org/")
    assert len(urls) == 1


def test_opportunity_desk_parse_listing_empty():
    """Returns empty list when no articles found."""
    scraper = OpportunityDeskScraper()
    html = "<html><body><p>No opportunities here.</p></body></html>"
    soup = BeautifulSoup(html, "lxml")
    urls = scraper._parse_listing(soup, "https://opportunitydesk.org/")
    assert isinstance(urls, list)


# ── YouthOpportunitiesScraper ──

def test_youth_opportunities_parse_listing():
    """Parses youthop.com opportunity links."""
    scraper = YouthOpportunitiesScraper()
    html = """
    <html><body>
        <a href="https://youthop.com/opportunities/test-fellowship-2025">Fellowship</a>
        <a href="/opportunities/another-grant-2025">Grant</a>
        <a href="https://external.com/unrelated">Unrelated</a>
    </body></html>
    """
    soup = BeautifulSoup(html, "lxml")
    urls = scraper._parse_listing(soup)
    assert any("youthop.com" in u for u in urls)
    assert not any("external.com" in u for u in urls)


def test_youth_opportunities_handles_relative_urls():
    """Relative /opportunities/ URLs are converted to absolute."""
    scraper = YouthOpportunitiesScraper()
    html = '<html><body><a href="/opportunities/test-2025">Test</a></body></html>'
    soup = BeautifulSoup(html, "lxml")
    urls = scraper._parse_listing(soup)
    assert any(u.startswith("https://youthop.com") for u in urls)


# ── RSSFeedScraper ───

@pytest.mark.asyncio
async def test_rss_scraper_handles_bad_feed():
    """RSS scraper returns empty list for a broken feed."""
    scraper = RSSFeedScraper()
    with patch("feedparser.parse") as mock_parse:
        mock_parse.return_value = MagicMock(bozo=True, entries=[], bozo_exception=Exception("bad feed"))
        urls = await scraper._parse_feed("https://bad-feed.example.com/rss", "BadFeed")
    assert urls == []


@pytest.mark.asyncio
async def test_rss_scraper_extracts_entry_links():
    """RSS scraper extracts links from feed entries."""
    scraper = RSSFeedScraper()
    mock_entry1 = MagicMock()
    mock_entry1.get = lambda k, d="": "https://example.com/article-1" if k == "link" else d
    mock_entry2 = MagicMock()
    mock_entry2.get = lambda k, d="": "https://example.com/article-2" if k == "link" else d

    with patch("feedparser.parse") as mock_parse:
        mock_parse.return_value = MagicMock(bozo=False, entries=[mock_entry1, mock_entry2])
        urls = await scraper._parse_feed("https://example.com/feed", "TestFeed")

    assert "https://example.com/article-1" in urls
    assert "https://example.com/article-2" in urls


# ── get_all_scrapers ──

def test_get_all_scrapers_returns_list():
    """get_all_scrapers returns a non-empty list of scraper instances."""
    scrapers = get_all_scrapers()
    assert isinstance(scrapers, list)
    assert len(scrapers) >= 3


def test_all_scrapers_have_source_name():
    """Every scraper has a non-empty source_name."""
    for scraper in get_all_scrapers():
        assert scraper.source_name
        assert isinstance(scraper.source_name, str)


def test_all_scrapers_have_fetch_listing_urls():
    """Every scraper implements fetch_listing_urls."""
    for scraper in get_all_scrapers():
        assert hasattr(scraper, "fetch_listing_urls")
        assert callable(scraper.fetch_listing_urls)
