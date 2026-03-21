import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand

from config import TOKEN, SUPER_ADMIN_IDS
from keyboards import get_keyboard
from db import is_admin
from handlers import user, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

BOT_TOKEN = TOKEN

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
    except Exception:
        logging.exception("START ERROR")
        await message.answer("❌ Сталася помилка при відкритті меню.")


async def set_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота")
    ])


async def main():
    logging.info("🚀 Бот запускається у режимі POLLING")

    await bot.delete_webhook(drop_pending_updates=False)
    await set_commands()

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
