from aiogram import types
from config import SUPER_ADMIN_IDS
from db import (
    add_cups_by_token,
    get_user_by_token,
    redeem_free_coffee_by_token,
    get_free_coffee_balance_by_token,
    get_total_users,
    get_active_users,
    get_total_scans,
    get_total_free_coffee_available,
    get_total_free_coffee_earned,
    get_total_free_coffee_redeemed,
    add_admin,
    remove_admin,
    is_admin,
    get_all_admins,
    get_all_user_ids
)

admin_modes = {}


def is_staff(user_id: int) -> bool:
    return user_id in SUPER_ADMIN_IDS or is_admin(user_id)


def extract_target_user_id(message: types.Message):
    if getattr(message, "forward_from", None):
        return message.forward_from.id

    if message.text and message.text.isdigit():
        return int(message.text)

    return None


def get_mode_value(user_id: int):
    value = admin_modes.get(user_id)

    if isinstance(value, dict):
        return value.get("mode")

    return value


def register(dp, bot):
    @dp.message(lambda message: message.text == "📷 Режим: нарахування")
    async def scan_qr_button(message: types.Message):
        if not is_staff(message.from_user.id):
            return

        admin_modes[message.from_user.id] = {"mode": "scan"}
        await message.answer(
            "📷 Режим: нарахування увімкнено\n\n"
            "Натисни «📱 Відкрити сканер», відскануй QR клієнта,\n"
            "після цього бот попросить ввести кількість чашок"
        )

    @dp.message(lambda message: message.text == "✅ Режим: списання")
    async def redeem_free_coffee_button(message: types.Message):
        if not is_staff(message.from_user.id):
            return

        admin_modes[message.from_user.id] = {"mode": "redeem"}
        await message.answer(
            "✅ Режим: списання безкоштовної кави увімкнено\n\n"
            "Натисни «📱 Відкрити сканер» та відскануй QR клієнта"
        )

    @dp.message(lambda message: message.text == "📊 Статистика")
    async def show_stats(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        total_users = get_total_users()
        active_users = get_active_users()
        total_scans = get_total_scans()
        free_available = get_total_free_coffee_available()
        free_earned = get_total_free_coffee_earned()
        free_redeemed = get_total_free_coffee_redeemed()

        await message.answer(
            "📊 Статистика бота\n\n"
            f"👥 Усього користувачів: {total_users}\n"
            f"☕ Користувачів із чашками зараз: {active_users}\n"
            f"🔄 Усього нарахувань чашок: {total_scans}\n"
            f"🎁 Усього нараховано безкоштовних кав: {free_earned}\n"
            f"✅ Усього списано безкоштовних кав: {free_redeemed}\n"
            f"👜 Безкоштовних кав зараз на балансі: {free_available}"
        )

    @dp.message(lambda message: message.text == "➕ Додати адміністратора")
    async def add_admin_mode(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        admin_modes[message.from_user.id] = {"mode": "add_admin"}
        await message.answer(
            "➕ Режим: додавання адміністратора\n\n"
            "Перешли будь-яке повідомлення від працівника\n"
            "або надішли його Telegram ID"
        )

    @dp.message(lambda message: message.text == "➖ Видалити адміністратора")
    async def remove_admin_mode(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        admin_modes[message.from_user.id] = {"mode": "remove_admin"}
        await message.answer(
            "➖ Режим: видалення адміністратора\n\n"
            "Перешли будь-яке повідомлення від адміністратора\n"
            "або надішли його Telegram ID"
        )

    @dp.message(lambda message: message.text == "👤 Список адміністраторів")
    async def admins_list(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        admins = get_all_admins()

        if not admins:
            await message.answer("👤 Список адміністраторів порожній")
            return

        text = "👤 Адміністратори:\n\n"
        for admin_id in admins:
            text += f"• {admin_id}\n"

        await message.answer(text)

    @dp.message(lambda message: message.text == "📣 Зробити розсилку")
    async def start_broadcast_mode(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        admin_modes[message.from_user.id] = {"mode": "broadcast"}
        await message.answer(
            "📣 Режим: розсилка\n\n"
            "Надішли текст повідомлення, який потрібно відправити всім користувачам"
        )

    @dp.message(
        lambda message: (
            message.text is not None
            and get_mode_value(message.from_user.id) in ["add_admin", "remove_admin"]
        ) or getattr(message, "forward_from", None) is not None
    )
    async def handle_admin_manage(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        mode = get_mode_value(message.from_user.id)
        if mode not in ["add_admin", "remove_admin"]:
            return

        target_user_id = extract_target_user_id(message)

        if not target_user_id:
            await message.answer("❌ Не вдалося визначити ID користувача")
            return

        if target_user_id in SUPER_ADMIN_IDS:
            await message.answer("❌ Не можна змінювати права суперадміністратора")
            return

        if mode == "add_admin":
            add_admin(target_user_id)
            admin_modes.pop(message.from_user.id, None)
            await message.answer(
                f"✅ Адміністратора додано\n\n"
                f"ID: {target_user_id}\n"
                f"Після команди /start у нього з’являться адмінські кнопки"
            )

        elif mode == "remove_admin":
            remove_admin(target_user_id)
            admin_modes.pop(message.from_user.id, None)
            await message.answer(
                f"✅ Адміністратора видалено\n\n"
                f"ID: {target_user_id}"
            )

    @dp.message(
        lambda message: (
            message.text is not None
            and get_mode_value(message.from_user.id) == "broadcast"
        )
    )
    async def handle_broadcast_text(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        broadcast_text = message.text.strip()

        if not broadcast_text:
            await message.answer("❌ Текст розсилки порожній")
            return

        user_ids = get_all_user_ids()

        if not user_ids:
            admin_modes.pop(message.from_user.id, None)
            await message.answer("❌ У базі поки немає користувачів для розсилки")
            return

        sent_count = 0
        failed_count = 0

        for user_id in user_ids:
            try:
                await bot.send_message(
                    user_id,
                    f"📣 Нове повідомлення від For-You-Me\n\n{broadcast_text}"
                )
                sent_count += 1
            except:
                failed_count += 1

        admin_modes.pop(message.from_user.id, None)

        await message.answer(
            "✅ Розсилку завершено\n\n"
            f"📨 Успішно відправлено: {sent_count}\n"
            f"❌ Не вдалося відправити: {failed_count}"
        )

    @dp.message(
        lambda message: (
            message.text is not None
            and get_mode_value(message.from_user.id) == "await_cups"
        )
    )
    async def handle_cups_input(message: types.Message):
        if not is_staff(message.from_user.id):
            return

        state = admin_modes.get(message.from_user.id)

        if not isinstance(state, dict) or state.get("mode") != "await_cups":
            return

        text = (message.text or "").strip()

        if not text.isdigit():
            await message.answer("❌ Введи число, наприклад: 1, 2, 3")
            return

        count = int(text)

        if count <= 0:
            await message.answer("❌ Кількість чашок має бути більшою за 0")
            return

        if count > 20:
            await message.answer("❌ За один раз можна нарахувати максимум 20 чашок")
            return

        token = state.get("token")
        user_id = state.get("user_id")

        result = add_cups_by_token(token, count)

        if not result:
            admin_modes[message.from_user.id] = {"mode": "scan"}
            await message.answer("❌ Користувача не знайдено")
            return

        cups = result["cups"]
        earned_free = result["earned_free"]
        free_balance = result["free_balance"]

        admin_modes[message.from_user.id] = {"mode": "scan"}

        if earned_free > 0:
            await message.answer(
                f"✅ Нараховано чашок: {count}\n"
                f"☕ Залишок чашок: {cups}/7\n"
                f"🎁 Додано безкоштовних кав: {earned_free}\n"
                f"👜 Баланс безкоштовних кав: {free_balance}"
            )

            try:
                await bot.send_message(
                    user_id,
                    f"☕ Тобі нарахували {count} чашок.\n"
                    f"☕ Зараз чашок: {cups}/7\n"
                    f"🎁 Додано безкоштовних кав: {earned_free}\n"
                    f"👜 Баланс безкоштовних кав: {free_balance}"
                )
            except:
                pass
        else:
            await message.answer(
                f"✅ Нараховано чашок: {count}\n"
                f"☕ Зараз у клієнта: {cups}/7"
            )

            try:
                await bot.send_message(
                    user_id,
                    f"☕ Тобі нарахували {count} чашок.\n"
                    f"☕ Зараз у тебе: {cups}/7"
                )
            except:
                pass

    @dp.message(lambda message: message.web_app_data is not None)
    async def handle_webapp_qr(message: types.Message):
        if not is_staff(message.from_user.id):
            return

        mode = get_mode_value(message.from_user.id)

        if mode not in ["scan", "redeem"]:
            await message.answer(
                "Оберіть дію перед скануванням:\n"
                "📷 Режим: нарахування — щоб нарахувати чашки\n"
                "✅ Режим: списання — щоб списати бонус"
            )
            return

        data = message.web_app_data.data

        if not data:
            await message.answer("❌ Дані зі сканера не отримано")
            return

        if not data.startswith("coffee:"):
            await message.answer("❌ Це не QR-код нашого бота")
            return

        token = data.split("coffee:")[1]

        user_id = get_user_by_token(token)
        if not user_id:
            await message.answer("❌ Користувача не знайдено")
            return

        if mode == "scan":
            admin_modes[message.from_user.id] = {
                "mode": "await_cups",
                "token": token,
                "user_id": user_id
            }

            await message.answer(
                "✅ QR успішно відскановано\n\n"
                "Тепер введи кількість чашок числом\n"
                "Наприклад: 1, 2, 3"
            )
            return

        if mode == "redeem":
            result = redeem_free_coffee_by_token(token)

            if result == "NOT_FOUND":
                await message.answer("❌ Користувача не знайдено")
                return

            if result == "EMPTY":
                await message.answer("❌ У клієнта немає безкоштовної кави для списання")
                return

            free_balance = get_free_coffee_balance_by_token(token)

            await message.answer(
                "✅ Безкоштовну каву списано\n"
                f"🎁 Залишок безкоштовних кав: {free_balance}"
            )

            try:
                await bot.send_message(
                    user_id,
                    "✅ У тебе списали 1 безкоштовну каву\n"
                    f"🎁 Залишок на балансі: {free_balance}"
                )
            except:
                pass
