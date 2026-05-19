import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_TRENDING_URL = "https://github.com/trending"
_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
}


async def fetch_trending(language: str = "", since: str = "weekly") -> list[dict] | None:
    url = f"{_TRENDING_URL}/{language}?since={since}"
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url, headers=_HEADERS)
            response.raise_for_status()
    except Exception as exc:
        logger.error("Failed to fetch %s: %s", url, exc)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    repos: list[dict] = []

    for article in soup.select("article.Box-row")[:10]:
        try:
            name_tag = article.select_one("h2 a")
            if not name_tag:
                continue

            href = name_tag.get("href", "")
            name = href.strip("/")
            repo_url = f"https://github.com{href}"

            desc_tag = article.select_one("p.col-9")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            stars_tag = article.select_one('a[href*="stargazers"]')
            stars = stars_tag.get_text(strip=True) if stars_tag else "0"

            period_tag = article.select_one("span.d-inline-block.float-sm-right")
            stars_period = period_tag.get_text(strip=True) if period_tag else ""

            lang_tag = article.select_one('[itemprop="programmingLanguage"]')
            lang = lang_tag.get_text(strip=True) if lang_tag else ""

            repos.append({
                "name": name,
                "url": repo_url,
                "description": description,
                "stars": stars,
                "stars_today": stars_period,
                "language": lang,
            })
        except Exception as exc:
            logger.error("Error parsing repo article: %s", exc)

    return repos
