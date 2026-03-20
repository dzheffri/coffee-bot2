import os

TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_IDS = [566408696]

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не задана")
