# GitHub Trending Telegram Bot

Telegram-бот, который парсит GitHub Trending и отправляет еженедельные дайджесты топ-репозиториев в канал или чат.

## Что умеет бот

- Показывает топ-10 репозиториев GitHub Trending по команде
- Фильтрует по языку программирования и периоду (день / неделя / месяц)
- Автоматически отправляет еженедельный дайджест в указанный канал

## Команды

| Команда | Описание |
|---|---|
| `/start` | Приветствие и краткое описание |
| `/help` | Список команд |
| `/trending` | Топ-10 за неделю (все языки) |
| `/trending python` | Топ-10 по языку |
| `/trending daily` | Топ за день |
| `/trending monthly` | Топ за месяц |

## Запуск локально

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/your-username/github-trending-bot.git
   cd github-trending-bot
   ```

2. Создать `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Заполнить переменные:
   - `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
   - `CHANNEL_ID` — ID канала или chat_id (например `-1001234567890`)
   - `WEEKLY_DAY` — день недели для рассылки (`mon`/`tue`/…/`sun`)
   - `WEEKLY_HOUR` — час отправки в UTC (например `9`)

3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Запустить бота:
   ```bash
   python bot.py
   ```

## Деплой на Railway

1. Создать проект на [Railway.app](https://railway.app) и подключить этот GitHub-репозиторий.
2. В настройках проекта перейти в **Variables** и добавить переменные окружения:
   - `BOT_TOKEN`
   - `CHANNEL_ID`
   - `WEEKLY_DAY`
   - `WEEKLY_HOUR`
3. Railway автоматически прочитает `Procfile` и запустит `python bot.py` как worker-процесс (не веб-сервис — бот работает через long polling).

## Структура проекта

```
github-trending-bot/
├── bot.py          # точка входа, запуск бота и планировщика
├── parser.py       # парсинг GitHub Trending
├── handlers.py     # обработчики команд и форматирование
├── scheduler.py    # еженедельная автоматическая рассылка
├── config.py       # конфиг из переменных окружения
├── requirements.txt
├── .env.example
├── .gitignore
└── Procfile
```
