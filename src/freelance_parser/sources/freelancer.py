import httpx

from ..models import Order
from .rss import USER_AGENT

BASE_URL = "https://www.freelancer.com/projects"


class FreelancerSource:
    """Freelancer.com public API; filter by skills via `jobs[]` in the URL."""

    name = "freelancer"

    def __init__(self, url: str, client: httpx.AsyncClient):
        self.url = url
        self.client = client

    async def fetch(self) -> list[Order]:
        resp = await self.client.get(self.url, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        return self.parse(resp.json())

    def parse(self, data: dict) -> list[Order]:
        if data.get("status") != "success":
            raise ValueError(f"Freelancer API: {data.get('message', data.get('status'))}")
        return [
            Order(
                source=self.name,
                id=str(project["id"]),
                title=project.get("title", ""),
                url=f"{BASE_URL}/{project['seo_url']}",
                description=project.get("description") or project.get("preview_description", ""),
                budget=_budget(project),
            )
            for project in data["result"]["projects"]
        ]


def _budget(project: dict) -> str:
    budget = project.get("budget") or {}
    low, high = budget.get("minimum"), budget.get("maximum")
    if not low and not high:
        return ""
    currency = project.get("currency") or {}
    sign, code = currency.get("sign", ""), currency.get("code", "")
    amount = f"{sign}{low:g}–{high:g}" if low and high else f"от {sign}{low:g}" if low else f"до {sign}{high:g}"
    suffix = "/час" if project.get("type") == "hourly" else ""
    return f"{amount} {code}{suffix}".strip()
