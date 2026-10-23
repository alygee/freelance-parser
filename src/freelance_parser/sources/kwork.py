import json

import httpx

from ..models import Order
from .rss import USER_AGENT

BASE_URL = "https://kwork.ru/projects"


class KworkSource:
    """Kwork has no RSS; orders are embedded as JSON in `window.stateData`."""

    name = "kwork"

    def __init__(self, url: str, client: httpx.AsyncClient):
        self.url = url
        self.client = client

    async def fetch(self) -> list[Order]:
        resp = await self.client.get(self.url, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        return self.parse(resp.text)

    def parse(self, html: str) -> list[Order]:
        start = html.find("window.stateData")
        if start == -1:
            raise ValueError("window.stateData не найден, разметка Kwork изменилась")
        data, _ = json.JSONDecoder().raw_decode(html, html.index("{", start))
        wants = data.get("wantsListData", {}).get("wants", [])
        return [
            Order(
                source=self.name,
                id=str(want["id"]),
                title=want.get("name", ""),
                url=f"{BASE_URL}/{want['id']}",
                description=want.get("description", ""),
                budget=_budget(want),
            )
            for want in wants
        ]


def _budget(want: dict) -> str:
    price = want.get("priceLimit")
    if not price:
        return ""
    price = price.removesuffix(".00")
    possible = want.get("possiblePriceLimit")
    if possible and possible != price:
        return f"до {price} ₽ (допустимо до {possible} ₽)"
    return f"до {price} ₽"
