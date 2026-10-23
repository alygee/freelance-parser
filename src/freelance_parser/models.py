from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    source: str
    id: str
    title: str
    url: str
    description: str = ""
    budget: str = ""
