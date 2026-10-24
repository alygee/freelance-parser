import httpx

from .models import Order

API_URL = "https://api.openai.com/v1/chat/completions"

INSTRUCTIONS = """Ты помогаешь фрилансеру написать черновик отклика на заказ.
Пиши по-русски, 4–7 предложений, без приветствий-шаблонов и воды.
Покажи, что понял задачу, предложи план решения и задай 1–2 уточняющих вопроса.
Опирайся только на опыт из профиля, ничего не выдумывай. Если подходящего опыта
нет, опирайся на смежный (например, бэкенд, интеграции, автоматизацию).
Не называй цену и сроки — их фрилансер укажет сам.

Профиль фрилансера:
{profile}"""


class OpenAIDrafter:
    def __init__(self, api_key: str, model: str, profile: str, client: httpx.AsyncClient):
        self.api_key = api_key
        self.model = model
        self.profile = profile
        self.client = client

    @staticmethod
    def prompt(order: Order) -> str:
        text = f"Заказ: {order.title}\n\n{order.description}"
        if order.budget:
            text += f"\n\nБюджет: {order.budget}"
        return text

    async def draft(self, order: Order) -> str:
        resp = await self.client.post(
            API_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": INSTRUCTIONS.format(profile=self.profile)},
                    {"role": "user", "content": self.prompt(order)},
                ],
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
