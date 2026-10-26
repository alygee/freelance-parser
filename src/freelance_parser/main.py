import asyncio
import logging

import httpx

from .config import Settings
from .drafter import OpenAIDrafter
from .filters import KeywordFilter
from .notifier import TelegramNotifier
from .sources import FreelancerSource, KworkSource, RedditSource, RssSource, Source
from .storage import Storage

log = logging.getLogger("freelance_parser")


async def poll_once(sources: list[Source], matches, storage: Storage, notifier, drafter=None) -> None:
    for source in sources:
        try:
            orders = await source.fetch()
        except (httpx.HTTPError, ValueError) as e:
            log.warning("%s: ошибка загрузки: %s", source.name, e)
            continue
        for order in orders:
            if matches(order) and storage.add_if_new(order):
                log.info("Новый заказ: %s", order.title)
                if notifier:
                    await notifier.send(order, await make_draft(drafter, order))


async def make_draft(drafter, order) -> str:
    if not drafter:
        return ""
    try:
        return await drafter.draft(order)
    except (httpx.HTTPError, KeyError, ValueError) as e:
        log.warning("Не удалось подготовить отклик: %s", e)
        return ""


async def main() -> None:
    settings = Settings.from_env()
    storage = Storage(settings.db_path)
    matches = KeywordFilter(settings.keywords, settings.stop_words)
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        sources = [RssSource(name, url, client) for name, url in settings.rss_feeds.items()]
        if settings.kwork_url:
            sources.append(KworkSource(settings.kwork_url, client))
        if settings.freelancer_url:
            sources.append(FreelancerSource(settings.freelancer_url, client))
        if settings.reddit_url:
            sources.append(RedditSource(settings.reddit_url, client))
        notifier = None
        if settings.bot_token and settings.chat_id:
            notifier = TelegramNotifier(settings.bot_token, settings.chat_id, client)
        else:
            log.warning("Telegram не настроен, заказы будут только в логе")
        drafter = None
        if settings.openai_api_key:
            drafter = OpenAIDrafter(settings.openai_api_key, settings.openai_model, settings.profile, client)
        while True:
            await poll_once(sources, matches, storage, notifier, drafter)
            await asyncio.sleep(settings.poll_interval)


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())


if __name__ == "__main__":
    run()
