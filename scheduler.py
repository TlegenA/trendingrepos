import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import CHANNEL_ID, WEEKLY_DAY, WEEKLY_HOUR
from handlers import send_digest_to_chat

logger = logging.getLogger(__name__)


async def _send_weekly_digest(bot: Bot) -> None:
    logger.info("Sending weekly digest to channel %s", CHANNEL_ID)
    ok = await send_digest_to_chat(bot, CHANNEL_ID, since="weekly")
    if ok:
        logger.info("Weekly digest sent successfully")
    else:
        logger.error("Weekly digest: fetch returned no repos")


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
