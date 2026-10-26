import httpx

from ..models import Order
from .rss import RssSource


class RedditSource(RssSource):
    """Subreddit RSS (e.g. r/forhire); keeps only "[Hiring]" posts, not freelancers' "[For Hire]" ads."""

    def __init__(self, url: str, client: httpx.AsyncClient):
        super().__init__("reddit", url, client)

    def parse(self, content: bytes) -> list[Order]:
        return [order for order in super().parse(content) if order.title.lower().startswith("[hiring")]
