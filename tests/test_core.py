from freelance_parser.filters import KeywordFilter
from freelance_parser.main import poll_once
from freelance_parser.models import Order
from freelance_parser.sources.kwork import KworkSource
from freelance_parser.sources.rss import RssSource
from freelance_parser.storage import Storage

RSS = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>t</title>
<item><title>Telegram-бот на Python</title><link>https://example.com/1</link><guid>1</guid></item>
<item><title>Сайт на WordPress</title><link>https://example.com/2</link><guid>2</guid></item>
</channel></rss>""".encode()


def make(title: str, oid: str = "1") -> Order:
    return Order(source="test", id=oid, title=title, url="https://example.com")


def test_filter_keywords_and_stop_words():
    f = KeywordFilter(["python", "бот"], ["wordpress"])
    assert f(make("Нужен бот для магазина"))
    assert not f(make("Python-плагин для WordPress"))
    assert not f(make("Логотип для кафе"))


def test_filter_matches_word_start_only():
    f = KeywordFilter(["бот"], ["1с"])
    assert f(make("Определение ботов поисковиков"))
    assert not f(make("Разработка HMI-интерфейса на C++"))
    assert f(make("Бот для заказа 21с"))
    assert not f(make("Бот для 1С"))


def test_storage_dedup(tmp_path):
    s = Storage(str(tmp_path / "t.db"))
    assert s.add_if_new(make("a"))
    assert not s.add_if_new(make("a"))


def test_rss_parse():
    orders = RssSource("fl", "", client=None).parse(RSS)
    assert [o.id for o in orders] == ["1", "2"]
    assert orders[0].url == "https://example.com/1"


async def test_poll_once_sends_only_new_matching(tmp_path):
    class FakeSource:
        name = "fake"

        async def fetch(self):
            return RssSource("fake", "", None).parse(RSS)

    class FakeNotifier:
        sent = []

        async def send(self, order):
            self.sent.append(order.title)

    notifier = FakeNotifier()
    storage = Storage(str(tmp_path / "t.db"))
    matches = KeywordFilter(["python"], ["wordpress"])
    await poll_once([FakeSource()], matches, storage, notifier)
    await poll_once([FakeSource()], matches, storage, notifier)
    assert notifier.sent == ["Telegram-бот на Python"]


KWORK_HTML = """<html><script>window.stateData = {"wantsListData": {"wants": [
{"id": 42, "name": "Парсер сайта", "description": "Нужен скрипт", "priceLimit": "500.00", "possiblePriceLimit": "1500"}
]}};</script></html>"""


def test_kwork_parse():
    [order] = KworkSource("", None).parse(KWORK_HTML)
    assert order.id == "42"
    assert order.url == "https://kwork.ru/projects/42"
    assert order.budget == "до 500 ₽ (допустимо до 1500 ₽)"
