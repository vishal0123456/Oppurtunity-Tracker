from app.scraper.opportunity_desk import OpportunityDeskScraper
from app.scraper.youth_opportunities import YouthOpportunitiesScraper
from app.scraper.rss_scraper import RSSFeedScraper
from app.scraper.global_grants import F6SStartupScraper, DevexOpportunityScraper


def get_all_scrapers():
    """Return all registered scraper instances."""
    return [
        OpportunityDeskScraper(),
        YouthOpportunitiesScraper(),
        RSSFeedScraper(),
        F6SStartupScraper(),
        DevexOpportunityScraper(),
    ]


__all__ = [
    "OpportunityDeskScraper",
    "YouthOpportunitiesScraper",
    "RSSFeedScraper",
    "F6SStartupScraper",
    "DevexOpportunityScraper",
    "get_all_scrapers",
]
