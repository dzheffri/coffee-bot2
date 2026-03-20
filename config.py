import os

TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
SUPER_ADMIN_IDS = [566408696]

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не задана")

if not DATABASE_URL:
    raise ValueError("Переменная окружения DATABASE_URL не задана")
