# Telegram Bot

Простой Telegram бот, который отвечает на команды /start и /stop.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Получите токен бота от [@BotFather](https://t.me/botfather) в Telegram

3. Создайте файл `.env` и добавьте ваш токен:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## Запуск

```bash
export TELEGRAM_BOT_TOKEN=your_bot_token_here
python bot.py
```

## Команды

- `/start` - бот отвечает "привет имя_пользователя"
- `/stop` - бот отвечает "пока имя_пользователя"
