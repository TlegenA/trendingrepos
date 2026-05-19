import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
WEEKLY_DAY: str = os.getenv("WEEKLY_DAY", "mon")
WEEKLY_HOUR: int = int(os.getenv("WEEKLY_HOUR", "9"))
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
