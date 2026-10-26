# freelance-parser

Собирает заказы с фриланс-бирж (RSS), фильтрует по ключевым словам и присылает новые в Telegram.

## Запуск

```bash
cp .env.example .env   # заполнить TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID
uv sync
uv run freelance-parser
```

Через Docker: `docker compose up -d --build`.

Токен бота выдаёт @BotFather, свой chat_id можно узнать у @userinfobot.
Без токена заказы просто пишутся в лог.

## Настройки (.env)

| Переменная | Описание |
|---|---|
| `KEYWORDS` | ключевые слова через запятую |
| `STOP_WORDS` | минус-слова |
| `RSS_FEEDS` | источники в формате `имя=url,имя2=url2` |
| `OPENAI_API_KEY` | ключ OpenAI API; если задан, к заказу в Telegram добавляется черновик отклика |
| `OPENAI_MODEL` | модель для черновиков, по умолчанию `gpt-5-mini` |
| `PROFILE_PATH` | файл с описанием вашего опыта для черновиков (пример — `profile.example.txt`) |
| `KWORK_URL` | страница проектов Kwork с нужной категорией; пусто — Kwork отключён |
| `FREELANCER_URL` | запрос к API Freelancer.com (`jobs[]=13` — Python, `292` — ML); пусто — отключён |
| `REDDIT_URL` | RSS сабреддитов (`r/forhire+jobbit`), берутся только посты `[Hiring]`; пусто — отключён |
| `POLL_INTERVAL` | интервал опроса в секундах |

## Новый источник

Реализуйте класс с полем `name` и методом `async fetch() -> list[Order]`
(см. `sources/rss.py`) и добавьте его в список `sources` в `main.py`.

## Тесты

```bash
uv run pytest
```

Автоматические отклики не делаем: это нарушает правила бирж.
