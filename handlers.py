import re
import logging
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from parser import fetch_trending
from config import CHANNEL_ID

logger = logging.getLogger(__name__)
router = Router()

_PERIODS = {"daily", "weekly", "monthly"}
_PERIOD_LABEL = {"daily": "дня", "weekly": "недели", "monthly": "месяца"}
_PERIOD_STARS = {"daily": "за день", "weekly": "за неделю", "monthly": "за месяц"}


def _extract_count(text: str) -> str:
    match = re.search(r"[\d,]+", text)
    return match.group() if match else text


def format_repos(repos: list[dict], since: str = "weekly") -> str:
    period = _PERIOD_LABEL.get(since, "недели")
    stars_label = _PERIOD_STARS.get(since, "за период")
    parts = [f"🔥 GitHub Trending — топ {period}\n"]

    for i, repo in enumerate(repos, 1):
        line = f'{i}. <a href="{repo["url"]}">{repo["name"]}</a>\n'
        line += f'   ⭐ {repo["stars"]} звезд'
        if repo["stars_today"]:
            count = _extract_count(repo["stars_today"])
            line += f" | +{count} {stars_label}"
        line += "\n"
        if repo["language"]:
            line += f'   💻 {repo["language"]}\n'
        if repo["description"]:
            desc = repo["description"]
            if len(desc) > 100:
                desc = desc[:100] + "..."
            line += f"   📝 {desc}\n"
        parts.append(line)

    return "\n".join(parts)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Привет! Я слежу за GitHub Trending и присылаю дайджесты топ-репозиториев.\n\n"
        "Используй /help для просмотра доступных команд."
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📋 <b>Команды:</b>\n\n"
        "/trending — топ-10 за неделю (все языки)\n"
        "/trending python — топ-10 по языку\n"
        "/trending daily — топ за день\n"
        "/trending monthly — топ за месяц\n"
        "/senddigest — отправить дайджест в канал прямо сейчас",
        parse_mode="HTML",
    )


@router.message(Command("trending"))
async def cmd_trending(message: Message) -> None:
    args = (message.text or "").split()[1:]

    language = ""
    since = "weekly"

    for arg in args:
        low = arg.lower()
        if low in _PERIODS:
            since = low
        else:
            language = low

    await message.answer("⏳ Загружаю данные...")
    repos = await fetch_trending(language=language, since=since)

    if repos is None:
        await message.answer("❌ Не удалось получить данные, попробуйте позже.")
        return

    if not repos:
        note = f" для языка «{language}»" if language else ""
        await message.answer(f"Репозитории{note} не найдены.")
        return

    await message.answer(
        format_repos(repos, since=since),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.message(Command("senddigest"))
async def cmd_senddigest(message: Message, bot: Bot) -> None:
    if not CHANNEL_ID:
        await message.answer("❌ CHANNEL_ID не задан в переменных окружения.")
        return

    await message.answer("⏳ Загружаю данные и отправляю в канал...")
    repos = await fetch_trending(since="weekly")

    if repos is None:
        await message.answer("❌ Не удалось получить данные, попробуйте позже.")
        return

    text = format_repos(repos, since="weekly")
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        await message.answer("✅ Дайджест отправлен в канал!")
    except Exception as exc:
        logger.error("senddigest failed: %s", exc)
        await message.answer(f"❌ Ошибка при отправке: {exc}")
