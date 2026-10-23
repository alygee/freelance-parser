import re

from .models import Order


def _compile(words: list[str]) -> re.Pattern[str] | None:
    # Match from the start of a word: "бот" matches "ботов", but not "разработка".
    if not words:
        return None
    alternatives = "|".join(re.escape(w.lower()) for w in words)
    return re.compile(rf"(?<!\w)(?:{alternatives})")


class KeywordFilter:
    def __init__(self, keywords: list[str], stop_words: list[str]):
        self.keywords = _compile(keywords)
        self.stop_words = _compile(stop_words)

    def __call__(self, order: Order) -> bool:
        text = f"{order.title} {order.description}".lower()
        if self.stop_words and self.stop_words.search(text):
            return False
        return self.keywords is None or bool(self.keywords.search(text))
