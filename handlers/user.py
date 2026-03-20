from aiogram import types
from aiogram.types.input_file import FSInputFile
from db import get_user_token, add_user, get_cups, get_free_coffee_balance
from utils.qr_generator import generate_qr


def format_cups_progress(cups: int) -> str:
    filled = "☕" * cups
    empty = "▫️" * (7 - cups)
    return f"{filled}{empty} ({cups}/7)"


def register(dp):
    @dp.message(lambda message: message.text == "📱 Мій QR-код")
    async def send_qr(message: types.Message):
        add_user(message.from_user.id)
        token = get_user_token(message.from_user.id)
        qr_path = generate_qr(token)
        photo = FSInputFile(qr_path)

        await message.answer_photo(
            photo=photo,
            caption="🎟 Ось твій персональний QR-код"
        )

    @dp.message(lambda message: message.text == "☕ Мої чашки")
    async def show_cups(message: types.Message):
        cups = get_cups(message.from_user.id)
        progress = format_cups_progress(cups)

        await message.answer(
            "☕ Твої чашки\n\n"
            f"{progress}\n\n"
            "Збери 7 чашок та отримай безкоштовну каву 🎁"
        )

    @dp.message(lambda message: message.text == "🎁 Мої безкоштовні кави")
    async def show_free_coffee(message: types.Message):
        balance = get_free_coffee_balance(message.from_user.id)

        await message.answer(
            "🎁 Твої безкоштовні кави\n\n"
            f"Зараз у тебе: {balance}"
        )
