import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import CHANNEL_ID, WEEKLY_DAY, WEEKLY_HOUR
from parser import fetch_trending
from handlers import format_repos

logger = logging.getLogger(__name__)


async def _send_weekly_digest(bot: Bot) -> None:
    logger.info("Sending weekly digest to channel %s", CHANNEL_ID)
    repos = await fetch_trending(since="weekly")

    if not repos:
        logger.error("Weekly digest: fetch returned no repos")
        return

    text = format_repos(repos, since="weekly")
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        logger.info("Weekly digest sent successfully")
    except Exception as exc:
        logger.error("Failed to send weekly digest: %s", exc)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _send_weekly_digest,
        trigger="cron",
        day_of_week=WEEKLY_DAY.lower(),
        hour=WEEKLY_HOUR,
        minute=0,
        kwargs={"bot": bot},
    )
    return scheduler
