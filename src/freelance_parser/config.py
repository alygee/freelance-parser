import os
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv


def _split(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _read(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


@dataclass
class Settings:
    bot_token: str
    chat_id: str
    poll_interval: int
    db_path: str
    keywords: list[str]
    stop_words: list[str]
    rss_feeds: dict[str, str]
    kwork_url: str
    freelancer_url: str
    reddit_url: str
    weblancer_url: str
    openai_api_key: str
    openai_model: str
    profile: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        feeds = {}
        for pair in _split(os.getenv("RSS_FEEDS", "")):
            name, _, url = pair.partition("=")
            feeds[name] = url
        return cls(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            poll_interval=int(os.getenv("POLL_INTERVAL", "180")),
            db_path=os.getenv("DB_PATH", "orders.db"),
            keywords=_split(os.getenv("KEYWORDS", "")),
            stop_words=_split(os.getenv("STOP_WORDS", "")),
            rss_feeds=feeds,
            kwork_url=os.getenv("KWORK_URL", ""),
            freelancer_url=os.getenv("FREELANCER_URL", ""),
            reddit_url=os.getenv("REDDIT_URL", ""),
            weblancer_url=os.getenv("WEBLANCER_URL", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            profile=_read(os.getenv("PROFILE_PATH", "profile.txt")),
        )
