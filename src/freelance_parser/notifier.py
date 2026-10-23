import html

import httpx

from .models import Order


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str, client: httpx.AsyncClient):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id
        self.client = client

    @staticmethod
    def format(order: Order) -> str:
        text = f"<b>{html.escape(order.title)}</b>\n[{order.source}]"
        if order.budget:
            text += f" · {html.escape(order.budget)}"
        return f"{text}\n{order.url}"

    async def send(self, order: Order) -> None:
        resp = await self.client.post(
            self.url,
            json={"chat_id": self.chat_id, "text": self.format(order), "parse_mode": "HTML"},
        )
        resp.raise_for_status()
