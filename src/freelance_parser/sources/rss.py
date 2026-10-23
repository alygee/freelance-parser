import feedparser
import httpx

from ..models import Order

USER_AGENT = "Mozilla/5.0 (compatible; freelance-parser/0.1)"


class RssSource:
    def __init__(self, name: str, url: str, client: httpx.AsyncClient):
        self.name = name
        self.url = url
        self.client = client

    async def fetch(self) -> list[Order]:
        resp = await self.client.get(self.url, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        return self.parse(resp.content)

    def parse(self, content: bytes) -> list[Order]:
        feed = feedparser.parse(content)
        return [
            Order(
                source=self.name,
                id=entry.get("id") or entry.get("link", ""),
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                description=entry.get("summary", ""),
            )
            for entry in feed.entries
        ]
