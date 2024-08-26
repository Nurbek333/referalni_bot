from aiogram.types import Message
from loader import dp, db, bot
from aiogram.filters import CommandStart
from keyboard_buttons.button import main_keyboard

# Foydalanuvchi botni boshlaganda yoki referal orqali kirganda
@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    text_parts = message.text.split()

    # Agar referal kodi mavjud bo'lsa, uni olish
    if len(text_parts) > 1:
        referrer_id = text_parts[1]
    else:
        referrer_id = None

    # Agar foydalanuvchi hali bazada yo'q bo'lsa
    if not db.user_exists(user_id):
        db.add_user(user_id, message.from_user.username)

        # Agar referal kodi mavjud bo'lsa
        if referrer_id:
            if db.user_exists(referrer_id):
                db.add_referral(referrer_id, user_id)
                db.add_points(referrer_id, 1)
                referrer_username = db.get_username(referrer_id)
                await bot.send_message(referrer_id, f"Sizning referalingiz orqali {message.from_user.username} botga kirdi!")

    await message.answer("Salom! Quyidagi tugmalar orqali botdan foydalaning:", reply_markup=main_keyboard)

# Referal link tugmasi
@dp.message(lambda message: message.text == "Referal link")
async def referal_link(message: Message):
    user_id = message.from_user.id
    referal_link = f"https://t.me/dwefe_bot?start={user_id}"
    await message.answer(f"Sizning referal havolangiz: {referal_link}")

# Mening ballarim tugmasi
@dp.message(lambda message: message.text == "Mening ballarim")
async def my_points(message: Message):
    user_id = message.from_user.id
    points = db.get_user_points(user_id)
    photo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtWRPo-AEN1M9MvQbhJsxNdpHx-83Sld_z3DLGfVVQoIOl2iwFidtclCUfadqWN_it25Q&usqp=CAU"
    response_text = (f"🎉 Sizning hozirgi ballaringiz:   *{points}* 🎉\n\n"
                     "💡 *Ballaringizni yig'ish orqali siz botdagi maxsus imkoniyatlardan foydalanishingiz mumkin.*\n\n"
                     "🔓 *Bonuslar ro'yxati:* \n\n"
                     "1️⃣  *10 ball* - 🎁 Maxsus sovg'a\n\n"
                     "2️⃣  *20 ball* - ⚙️ Qo'shimcha funksiyalar\n\n"
                     "3️⃣  *50 ball* - 💸 Chegirmali takliflar\n\n"
                     "🔗 *Referal havolangizni do'stlaringiz bilan ulashing va ko'proq ball yig'ing!*")
    await message.answer_photo(photo=photo, caption=response_text, parse_mode='Markdown')
