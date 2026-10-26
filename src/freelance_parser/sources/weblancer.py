import html
import re

import httpx

from ..models import Order
from .rss import USER_AGENT

BASE_URL = "https://www.weblancer.net"

ARTICLE = re.compile(r"<article.*?</article>", re.S)
TITLE = re.compile(r'<h2[^>]*>\s*<a[^>]*href="(?P<href>[^"]*-(?P<id>\d+)/?)"[^>]*>(?P<title>.*?)</a>', re.S)
BUDGET = re.compile(r'<span class="text-green-600[^"]*">(.*?)</span>', re.S)
DESCRIPTION = re.compile(r"<p(?:\s[^>]*)?>(.*?)</p>", re.S)
TAG = re.compile(r"<[^>]+>")


class WeblancerSource:
    """Weblancer has no RSS and its /api/ is disallowed in robots.txt; orders are parsed from `<article>` cards."""

    name = "weblancer"

    def __init__(self, url: str, client: httpx.AsyncClient):
        self.url = url
        self.client = client

    async def fetch(self) -> list[Order]:
        resp = await self.client.get(self.url, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        return self.parse(resp.text)

    def parse(self, page: str) -> list[Order]:
        orders = []
        for article in ARTICLE.findall(page):
            title = TITLE.search(article)
            if not title:
                continue
            budget = BUDGET.search(article)
            description = DESCRIPTION.search(article)
            orders.append(
                Order(
                    source=self.name,
                    id=title["id"],
                    title=_text(title["title"]),
                    url=BASE_URL + title["href"],
                    description=_text(description[1]) if description else "",
                    budget=_text(budget[1]) if budget else "",
                )
            )
        if not orders:
            raise ValueError("карточки заказов не найдены, разметка Weblancer изменилась")
        return orders


def _text(fragment: str) -> str:
    return " ".join(html.unescape(TAG.sub("", fragment)).split())
