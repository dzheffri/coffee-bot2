from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


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

    # Кнопки для админа и супер-админа
    if is_admin or user_id in super_admin_ids:
        keyboard.append([
            KeyboardButton(text="📷 Режим: нарахування"),
            KeyboardButton(text="✅ Режим: списання")
        ])
        keyboard.append([
            KeyboardButton(
                text="📱 Відкрити сканер",
                web_app=WebAppInfo(
                    url="https://dzheffri.github.io/coffee-bot2/scanner.html"
                )
            )
        ])
        keyboard.append([
            KeyboardButton(text="📷 Сканувати QR (фото)")
        ])

    # Только для супер-админа
    if user_id in super_admin_ids:
        keyboard.append([
            KeyboardButton(text="📊 Статистика")
        ])
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
