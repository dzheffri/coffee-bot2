import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import TOKEN, SUPER_ADMIN_IDS
from keyboards import get_keyboard
from db import is_admin
from handlers import user, admin

bot = Bot(token=TOKEN)
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


async def main():
    print("Бот запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())