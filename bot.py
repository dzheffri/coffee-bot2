import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import TOKEN, SUPER_ADMIN_IDS
from keyboards import get_keyboard
from db import is_admin
from handlers import user, admin

BOT_TOKEN = TOKEN
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "for_you_me_secret_2026"

WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "").rstrip("/")
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}" if WEBHOOK_BASE_URL else ""

PORT = int(os.getenv("PORT", 8080))
HOST = "0.0.0.0"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user.register(dp)
admin.register(dp, bot)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    try:
        user_id = message.from_user.id
        current_is_admin = is_admin(user_id)

        keyboard = get_keyboard(
            user_id=user_id,
            super_admin_ids=SUPER_ADMIN_IDS,
            is_admin=current_is_admin
        )

        await message.answer(
            "👋 Вітаємо у програмі лояльності For-You-Me ☕\n\n"
            "Скануй свій QR-код під час покупки та збирай чашки.\n"
            "За кожні 7 чашок ти отримуєш безкоштовну каву 🎁",
            reply_markup=keyboard
        )
    except Exception as e:
        print("START ERROR:", e)
        await message.answer("❌ Сталася помилка при відкритті меню.")


async def set_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота")
    ])


async def on_startup(bot: Bot):
    print("🚀 Бот запускається у режимі WEBHOOK")

    if not WEBHOOK_BASE_URL:
        raise RuntimeError("Не задана змінна WEBHOOK_BASE_URL")

    await set_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET
    )

    print(f"✅ Webhook встановлено: {WEBHOOK_URL}")


dp.startup.register(on_startup)


def root_healthcheck(request):
    return web.Response(text="OK", status=200)


async def start():
    app = web.Application()

    app.router.add_get("/", root_healthcheck)
    app.router.add_get("/health", root_healthcheck)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    print(f"🌐 HTTP server start on {HOST}:{PORT}")

    # держим процесс живым
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(start())
