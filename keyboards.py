from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_keyboard(user_id, super_admin_ids, is_admin=False):
    keyboard = [
        [
            KeyboardButton(text="📱 Мій QR-код"),
            KeyboardButton(text="☕ Мої чашки")
        ],
        [
            KeyboardButton(text="🎁 Мої безкоштовні кави")
        ]
    ]

    if is_admin or user_id in super_admin_ids:
        keyboard.append([
            KeyboardButton(text="📷 Сканувати QR"),
            KeyboardButton(text="✅ Списати безкоштовну каву")
        ])
        keyboard.append([
            KeyboardButton(text="📊 Статистика")
        ])

    if user_id in super_admin_ids:
        keyboard.append([
            KeyboardButton(text="➕ Додати адміністратора"),
            KeyboardButton(text="➖ Видалити адміністратора")
        ])
        keyboard.append([
            KeyboardButton(text="👤 Список адміністраторів"),
            KeyboardButton(text="📣 Зробити розсилку")
        ])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )