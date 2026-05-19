import logging
from anthropic import AsyncAnthropic
from config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
_MODEL = "claude-haiku-4-5"

_SYSTEM_PROMPT = """\
Ты аналитик технических проектов. Твоя задача — делать краткий, но содержательный разбор \
GitHub-репозиториев на русском языке для Telegram-канала об интересных open-source проектах.

Формат ответа — строго следующий (без лишних заголовков и markdown-блоков):

Проект от [организация или автор]. [X]k звёзд, [Y]k форков.

Суть одной строкой: [одно предложение]

Проблема, которую решает
[2–3 предложения о боли, которую решает проект]

Как работает
1. [шаг]
2. [шаг]
3. [шаг]

Пример
[конкретный пример использования, начинается с «вместо того чтобы...» или аналогично]

Для каких задач актуально
✅ [задача]
✅ [задача]
✅ [задача]

Требования
[минимальные требования для запуска — язык, зависимости, API-ключи]

Придерживайся этого формата точно. Пиши живо и по делу, без воды.\
"""


async def analyze_repo(repo: dict, readme: str) -> str:
    """Generate a structured Russian-language analysis of a GitHub repo using Claude."""
    owner_repo = repo["name"]
    parts = owner_repo.split("/")
    org = parts[0] if parts else owner_repo

    user_content = (
        f"Репозиторий: {repo['url']}\n"
        f"Название: {owner_repo}\n"
        f"Язык: {repo.get('language') or 'не указан'}\n"
        f"Звёзды: {repo.get('stars', '?')}\n"
        f"Прирост звёзд за период: {repo.get('stars_today') or 'нет данных'}\n"
        f"Описание: {repo.get('description') or 'нет описания'}\n"
    )
    if readme:
        user_content += f"\nREADME (первые {len(readme)} символов):\n{readme}"
    else:
        user_content += "\nREADME: недоступен"

    try:
        response = await _client.messages.create(
            model=_MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_content}],
        )
        return response.content[0].text.strip()
    except Exception as exc:
        logger.error("Claude analysis failed for %s: %s", owner_repo, exc)
        # Fallback: plain summary without LLM
        return (
            f"<b><a href=\"{repo['url']}\">{owner_repo}</a></b>\n"
            f"⭐ {repo.get('stars', '?')} звёзд\n"
            + (f"💻 {repo['language']}\n" if repo.get("language") else "")
            + (f"📝 {repo['description'][:200]}\n" if repo.get("description") else "")
        )
