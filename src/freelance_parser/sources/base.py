from typing import Protocol

from ..models import Order


class Source(Protocol):
    name: str

    async def fetch(self) -> list[Order]: ...
