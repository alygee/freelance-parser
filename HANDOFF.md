# Handoff: Freelance orders parser — Python/ML orders + reply drafts

**Generated**: 2026-10-26
**Branch**: main (in sync with origin/main, clean tree)
**Status**: Ready for real-credentials test and server deploy

## Goal

Bot that collects freelance orders (FL.ru, Kwork), keeps only Python/ML ones, and sends them to Telegram with an OpenAI-drafted reply the user sends manually. User is a senior frontend dev moving into Python/ML; project is also a portfolio piece.

## Completed

- [x] Keyword filter matches from word start (`cffa33c`): "бот" no longer matches "разработка"
- [x] FL.ru RSS `https://www.fl.ru/rss/all.xml?category=5` verified live (200, orders parsed)
- [x] Kwork source (`95502ca`), verified live, fills `Order.budget`
- [x] OpenAI reply drafts in Telegram message (`4f5c2b5`), keywords refocused on Python/ML
- [x] Docker image built and run successfully; `profile.txt` mounted, `.dockerignore` added (`e551843`, user's commit)
- [x] `uv run pytest` → `8 passed`

## Not Yet Done

- [ ] Real run with `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `OPENAI_API_KEY` (never tested end-to-end with real Telegram/OpenAI)
- [ ] Confirm `OPENAI_MODEL` default `gpt-5-mini` is a valid model name (unverified guess)
- [ ] Deploy to a VPS (steps below); check FL.ru/Kwork reachable from a foreign IP
- [ ] Telegram send error still kills the poll loop (order already marked seen)
- [ ] Ideas: Telegram channels (Telethon), Freelancer.com API, multi-page Kwork, Kwork categories beyond `c=41`

## Failed Approaches (Don't Repeat These)

- **Habr Freelance**: `freelance.habr.com/tasks.rss` → HTTP 410, "Сервис Хабр Фриланс закрылся навсегда"; robots.txt `Disallow: /`. Service is dead, don't add it.
- **Kwork JSON via regex** `window\.stateData\s*=\s*(\{.*?\});\s*</script>` → `JSONDecodeError: Extra data`. Use `json.JSONDecoder().raw_decode(html, index_of_first_brace)` (as in `sources/kwork.py`).
- **Substring keyword matching** → false positives ("бот" in "разработка", "1с" in "21с"). Replaced with `(?<!\w)` word-start regex.
- **`docker build` on the dev machine** timed out downloading wheels from PyPI; `docker build --network host` worked. Local network quirk, not a Dockerfile bug.

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Drafts are only suggestions, never auto-sent | Exchange ToS; user replies manually |
| OpenAI and Telegram called via raw httpx | Minimal deps, consistent style |
| `profile.txt` (condensed, no PII) instead of `resume.txt` in the prompt | Resume contains phone/email/birth date; must not go to OpenAI |
| Prompt forbids inventing experience | User has little commercial Python; drafts must stay honest |
| Drafter failure → send order without draft | Notification is more important than draft |
| Removed generic keywords (бот, скрипт, автоматизация, telegram) | User wants Python orders; those let through any-language jobs |
| Kwork parsed from embedded `window.stateData` JSON | No RSS; JSON is more stable than HTML markup; `/projects` not in robots.txt Disallow |

## Current State

**Working**: FL.ru + Kwork fetch, filter, SQLite dedup, Docker image; tests pass.
**Broken**: nothing known. Real Telegram/OpenAI untested.
**Uncommitted Changes**: none.

## Files to Know

| File | Why It Matters |
|------|----------------|
| `src/freelance_parser/main.py` | `poll_once`, `make_draft`, source/notifier/drafter wiring |
| `src/freelance_parser/drafter.py` | `OpenAIDrafter`, `INSTRUCTIONS` prompt |
| `src/freelance_parser/sources/kwork.py` | Kwork parser + budget formatting |
| `src/freelance_parser/filters.py` | Word-start keyword/stop-word regex |
| `src/freelance_parser/notifier.py` | Message format; draft in `<blockquote>`, truncated to 3500 chars |
| `src/freelance_parser/config.py` | All env vars |
| `docker-compose.yml` | Mounts `./data` and `./profile.txt` |
| `profile.example.txt` | Template; real `profile.txt`, `resume.txt`, `.env` are gitignored |

## Code Context

```python
async def poll_once(sources, matches, storage, notifier, drafter=None) -> None
async def make_draft(drafter, order) -> str          # "" on no drafter or httpx/KeyError/ValueError
class OpenAIDrafter:  async def draft(self, order: Order) -> str   # POST /v1/chat/completions, timeout 60
class TelegramNotifier:  async def send(self, order: Order, draft: str = "") -> None
class KworkSource:  name = "kwork"; parse(html: str) -> list[Order]  # raises ValueError if no stateData
```

Env vars: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `POLL_INTERVAL` (180), `DB_PATH`, `KEYWORDS`, `STOP_WORDS`, `RSS_FEEDS` (`name=url,...`), `KWORK_URL` (empty = off), `OPENAI_API_KEY` (empty = no drafts), `OPENAI_MODEL`, `PROFILE_PATH` (missing file → empty profile, silently).

Kwork order fields used: `wantsListData.wants[]` → `id`, `name`, `description`, `priceLimit` ("500.00"), `possiblePriceLimit`. Order URL `https://kwork.ru/projects/{id}`.

## Resume Instructions

1. `uv sync && uv run pytest` → expect `8 passed`
2. Fill `.env`: Telegram token (@BotFather), chat id (@userinfobot; user must `/start` the bot), `OPENAI_API_KEY`
3. `uv run freelance-parser` (delete `orders.db` to re-see old orders)
   - Expected: `Новый заказ: ...` logs and Telegram messages with "Черновик отклика"
   - `Не удалось подготовить отклик: 404/400` → wrong `OPENAI_MODEL`; `403`/region error → OpenAI blocks Russian IPs
4. Deploy: VPS outside Russia (OpenAI), `curl -fsSL https://get.docker.com | sh`, `git clone git@github.com:alygee/freelance-parser.git`, copy `.env` and `profile.txt`, `docker compose up -d --build`, `docker compose logs -f`

## Edge Cases & Error Handling

- Source HTTP error or Kwork markup change (`ValueError`) → logged, other sources continue
- OpenAI error/timeout → order sent without draft
- Telegram send error → propagates and kills the loop; order already stored as seen (not handled)
- Malformed `RSS_FEEDS` entry without `=` → empty URL (not validated)
- Kwork: only first page (12 orders) read

## Warnings

- Communicate with the user in Russian.
- Don't commit or push without asking.
- Never send `resume.txt` contents (PII) to external APIs.
- Polite intervals (180s), no captcha/anti-bot bypass, no auto-replies.
- OpenAI API is billed separately from ChatGPT Plus.
