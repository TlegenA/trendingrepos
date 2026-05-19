import logging
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from parser import fetch_trending, fetch_readme
from analyzer import analyze_repo
from config import CHANNEL_ID

logger = logging.getLogger(__name__)
router = Router()

_DIGEST_COUNT = 5


async def send_digest_to_chat(bot: Bot, chat_id: str | int, since: str = "weekly") -> bool:
    """Fetch top repos, analyze each with Claude, send as separate messages. Returns True on success."""
    repos = await fetch_trending(since=since)
    if not repos:
        return False

    top = repos[:_DIGEST_COUNT]
    period_labels = {"daily": "дня", "weekly": "недели", "monthly": "месяца"}
    label = period_labels.get(since, "недели")

    await bot.send_message(
        chat_id=chat_id,
        text=f"🔥 <b>GitHub Trending — топ {_DIGEST_COUNT} {label}</b>",
        parse_mode="HTML",
    )

    for repo in top:
        readme = await fetch_readme(repo["name"])
        analysis = await analyze_repo(repo, readme)

        text = (
            f'<a href="{repo["url"]}">{repo["name"]}</a>\n\n'
            f"{analysis}"
        )

        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    return True


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
        "/trending — топ-5 за неделю с AI-разбором\n"
        "/trending python — топ-5 по языку\n"
        "/trending daily — топ за день\n"
        "/trending monthly — топ за месяц\n"
        "/senddigest — отправить дайджест в канал прямо сейчас",
        parse_mode="HTML",
    )


@router.message(Command("trending"))
async def cmd_trending(message: Message, bot: Bot) -> None:
    args = (message.text or "").split()[1:]

    language = ""
    since = "weekly"
    _periods = {"daily", "weekly", "monthly"}

    for arg in args:
        low = arg.lower()
        if low in _periods:
            since = low
        else:
            language = low

    await message.answer("⏳ Загружаю данные и анализирую репозитории...")

    repos = await fetch_trending(language=language, since=since)
    if repos is None:
        await message.answer("❌ Не удалось получить данные, попробуйте позже.")
        return

    if not repos:
        note = f" для языка «{language}»" if language else ""
        await message.answer(f"Репозитории{note} не найдены.")
        return

    top = repos[:_DIGEST_COUNT]
    for repo in top:
        readme = await fetch_readme(repo["name"])
        analysis = await analyze_repo(repo, readme)

        text = (
            f'<a href="{repo["url"]}">{repo["name"]}</a>\n\n'
            f"{analysis}"
        )

        await message.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


@router.message(Command("senddigest"))
async def cmd_senddigest(message: Message, bot: Bot) -> None:
    if not CHANNEL_ID:
        await message.answer("❌ CHANNEL_ID не задан в переменных окружения.")
        return

    await message.answer("⏳ Загружаю данные и анализирую репозитории...")

    ok = await send_digest_to_chat(bot, CHANNEL_ID, since="weekly")
    if ok:
        await message.answer("✅ Дайджест отправлен в канал!")
    else:
        await message.answer("❌ Не удалось получить данные, попробуйте позже.")
