import os
import cv2
from aiogram import types
from config import SUPER_ADMIN_IDS
from db import (
    add_cup_by_token,
    get_cups_by_token,
    get_user_by_token,
    award_free_coffee,
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


def scan_qr(photo_path):
    img = cv2.imread(photo_path)

    if img is None:
        return None

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if data:
        return data

    return None


def extract_target_user_id(message: types.Message):
    if getattr(message, "forward_from", None):
        return message.forward_from.id

    if message.text and message.text.isdigit():
        return int(message.text)

    return None


def register(dp, bot):
    @dp.message(lambda message: message.text == "📷 Режим: нарахування")
    async def scan_qr_button(message: types.Message):
        if not is_staff(message.from_user.id):
            return

        admin_modes[message.from_user.id] = "scan"
        await message.answer(
            "📷 Режим: нарахування чашки увімкнено\n\n"
            "Тепер натисни «📱 Відкрити сканер» або надішли фото QR-коду"
        )

    @dp.message(lambda message: message.text == "✅ Режим: списання")
    async def redeem_free_coffee_button(message: types.Message):
        if not is_staff(message.from_user.id):
            return

        admin_modes[message.from_user.id] = "redeem"
        await message.answer(
            "✅ Режим: списання безкоштовної кави увімкнено\n\n"
            "Тепер натисни «📱 Відкрити сканер» або надішли фото QR-коду"
        )

    @dp.message(lambda message: message.text == "📊 Статистика")
    async def show_stats(message: types.Message):
        if not is_staff(message.from_user.id):
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

        admin_modes[message.from_user.id] = "add_admin"
        await message.answer(
            "➕ Режим: додавання адміністратора\n\n"
            "Перешли будь-яке повідомлення від працівника\n"
            "або надішли його Telegram ID"
        )

    @dp.message(lambda message: message.text == "➖ Видалити адміністратора")
    async def remove_admin_mode(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        admin_modes[message.from_user.id] = "remove_admin"
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

        admin_modes[message.from_user.id] = "broadcast"
        await message.answer(
            "📣 Режим: розсилка\n\n"
            "Надішли текст повідомлення, який потрібно відправити всім користувачам"
        )

    @dp.message(
        lambda message: (
            message.text is not None
            and admin_modes.get(message.from_user.id) in ["add_admin", "remove_admin"]
        ) or getattr(message, "forward_from", None) is not None
    )
    async def handle_admin_manage(message: types.Message):
        if message.from_user.id not in SUPER_ADMIN_IDS:
            return

        mode = admin_modes.get(message.from_user.id)
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
            and admin_modes.get(message.from_user.id) == "broadcast"
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

    @dp.message(lambda message: message.web_app_data is not None)
    async def handle_webapp_qr(message: types.Message):
        if not is_staff(message.from_user.id):
            return

        mode = admin_modes.get(message.from_user.id)

        if mode not in ["scan", "redeem"]:
            await message.answer(
                "Оберіть дію перед скануванням:\n"
                "📷 Режим: нарахування — щоб нарахувати чашку\n"
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
            add_cup_by_token(token)
            cups = get_cups_by_token(token)

            if cups >= 7:
                award_free_coffee(user_id)
                free_balance = get_free_coffee_balance_by_token(token)

                await message.answer(
                    "🎉 7/7! Клієнту нараховано безкоштовну каву\n"
                    f"🎁 Зараз безкоштовних кав на балансі: {free_balance}"
                )

                try:
                    await bot.send_message(
                        user_id,
                        "🎉 Вітаємо!\n"
                        "Ти зібрав 7 чашок і отримав безкоштовну каву ☕\n\n"
                        f"🎁 Безкоштовних кав на балансі: {free_balance}"
                    )
                except:
                    pass
            else:
                await message.answer(f"✅ Нараховано чашку: {cups}/7 ☕")

                try:
                    await bot.send_message(
                        user_id,
                        f"☕ Тобі додали чашку.\nЗараз у тебе: {cups}/7"
                    )
                except:
                    pass

        elif mode == "redeem":
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

    @dp.message(lambda message: message.photo)
    async def handle_qr_photo(message: types.Message):
        if not is_staff(message.from_user.id):
            return

        mode = admin_modes.get(message.from_user.id)
        if mode not in ["scan", "redeem"]:
            await message.answer(
                "Оберіть дію перед скануванням:\n"
                "📷 Режим: нарахування — щоб нарахувати чашку\n"
                "✅ Режим: списання — щоб списати бонус"
            )
            return

        temp_file = f"temp_qr_{message.from_user.id}.jpg"

        try:
            file_info = await bot.get_file(message.photo[-1].file_id)
            await bot.download_file(file_info.file_path, destination=temp_file)

            data = scan_qr(temp_file)

            if not data:
                await message.answer("❌ QR-код не знайдено на фото")
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
                add_cup_by_token(token)
                cups = get_cups_by_token(token)

                if cups >= 7:
                    award_free_coffee(user_id)
                    free_balance = get_free_coffee_balance_by_token(token)

                    await message.answer(
                        "🎉 7/7! Клієнту нараховано безкоштовну каву\n"
                        f"🎁 Зараз безкоштовних кав на балансі: {free_balance}"
                    )

                    try:
                        await bot.send_message(
                            user_id,
                            "🎉 Вітаємо!\n"
                            "Ти зібрав 7 чашок і отримав безкоштовну каву ☕\n\n"
                            f"🎁 Безкоштовних кав на балансі: {free_balance}"
                        )
                    except:
                        pass
                else:
                    await message.answer(f"✅ Нараховано чашку: {cups}/7 ☕")

                    try:
                        await bot.send_message(
                            user_id,
                            f"☕ Тобі додали чашку.\nЗараз у тебе: {cups}/7"
                        )
                    except:
                        pass

            elif mode == "redeem":
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

        except Exception as e:
            await message.answer(f"❌ Помилка під час обробки QR: {e}")

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
