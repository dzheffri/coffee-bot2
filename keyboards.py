from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


def get_keyboard(user_id, super_admin_ids, is_admin=False):
    is_super_admin = user_id in super_admin_ids

    # Обычный пользователь
    if not is_admin and not is_super_admin:
        keyboard = [
            [
                KeyboardButton(text="📱 Мій QR-код"),
                KeyboardButton(text="☕ Мої чашки")
            ],
            [
                KeyboardButton(text="🎁 Мої безкоштовні кави")
            ]
        ]
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )

    # Обычный админ и супер-админ
    keyboard = [
        [
            KeyboardButton(text="📷 Режим: нарахування"),
            KeyboardButton(text="✅ Режим: списання")
        ],
        [
            KeyboardButton(
                text="📱 Відкрити сканер",
                web_app=WebAppInfo(
                    url="https://dzheffri.github.io/coffee-bot2/scanner.html"
                )
            )
        ]
    ]

    # Только супер-админ
    if is_super_admin:
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
