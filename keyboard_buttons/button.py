from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Asosiy keyboard
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Referal link"),
            KeyboardButton(text="Mening ballarim"),
        ],
        [
            KeyboardButton(text="Top 10 Foydalanuvchilar"),
        ]
    ],
    resize_keyboard=True
)
