"""APScheduler-based job scheduling."""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings

scheduler = AsyncIOScheduler()


async def _training_tick_job() -> None:
    """Run the nightly training tick."""
    # TODO: iterate all players, call training_service.compute_training_tick
    pass


async def _report_job() -> None:
    """Generate daily reports."""
    pass


def setup_scheduler() -> None:
    """Register recurring jobs and start the scheduler."""
    h, m = settings.training_tick_utc.split(":")
    scheduler.add_job(
        _training_tick_job,
        CronTrigger(hour=int(h), minute=int(m), timezone="UTC"),
        id="training_tick",
        replace_existing=True,
    )

    rh, rm = settings.reports_time.split(":")
    scheduler.add_job(
        _report_job,
        CronTrigger(hour=int(rh), minute=int(rm), timezone=settings.reports_tz),
        id="daily_reports",
        replace_existing=True,
    )

    scheduler.start()
