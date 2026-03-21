import os
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


async def on_shutdown(bot: Bot):
    print("⛔ Бот завершує роботу")
    await bot.delete_webhook()


dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


async def healthcheck(request):
    return web.Response(text="OK")


def main():
    app = web.Application()

    app.router.add_get("/", healthcheck)
    app.router.add_get("/health", healthcheck)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    print(f"🌐 HTTP server start on {HOST}:{PORT}")
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
