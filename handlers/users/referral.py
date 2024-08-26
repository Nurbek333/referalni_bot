from baza.sqlite import Database
from aiogram.types import Message
from loader import dp, db, bot, ADMINS
from aiogram import F, Dispatcher
from keyboard_buttons.button import menu_button

async def handle_referral(message: Message):
    args = message.get_args()
    if args:
        referal_id = int(args)
        # Referalni bazaga yozish va ballarni yangilash
        db.add_referral(message.from_user.id, referal_id)
        await message.answer(f"Sizni taklif qilgan foydalanuvchi: {referal_id}")
    else:
        await message.answer("Botga xush kelibsiz!")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_referral, commands=['start'])