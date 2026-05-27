"""
APScheduler setup — runs the pipeline automatically every day.
Configured via environment variables.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler():
    """Register scheduled jobs and start the scheduler."""
    from app.pipeline.runner import run_pipeline

    scheduler.add_job(
        run_pipeline,
        trigger=CronTrigger(
            hour=settings.PIPELINE_RUN_HOUR,
            minute=settings.PIPELINE_RUN_MINUTE,
        ),
        id="daily_pipeline",
        name="Daily Opportunity Discovery Pipeline",
        replace_existing=True,
        misfire_grace_time=3600,  # Allow up to 1 hour late start
    )

    scheduler.start()
    logger.info(
        f"Scheduler started. Pipeline runs daily at "
        f"{settings.PIPELINE_RUN_HOUR:02d}:{settings.PIPELINE_RUN_MINUTE:02d} UTC"
    )


def shutdown_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down.")
