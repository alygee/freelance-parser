from .models import Order


class KeywordFilter:
    def __init__(self, keywords: list[str], stop_words: list[str]):
        self.keywords = [k.lower() for k in keywords]
        self.stop_words = [s.lower() for s in stop_words]

    def __call__(self, order: Order) -> bool:
        text = f"{order.title} {order.description}".lower()
        if any(s in text for s in self.stop_words):
            return False
        return not self.keywords or any(k in text for k in self.keywords)
