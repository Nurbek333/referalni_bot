from aiogram.types import Message
from loader import dp
from aiogram.filters import Command

#about commands
@dp.message(Command("about"))
async def about_commands(message:Message):
    user_id = message.from_user.id
    referal_link = f"https://t.me/dwefe_bot?start={user_id}"
    response_text = ("<b>🤖 Bot haqida:</b>\n"

    "<b>Ushbu bot sizga va do'stlaringizga o'yin yoki xizmatlar uchun ball to'plash imkonini beradi. Botdan foydalanish orqali turli imtiyozlarga ega bo'lishingiz mumkin! 🎉</b>\n"

    "<b>🎯 Referal tizimi qanday ishlaydi?</b>\n"

    "1. <b>👤 1-daraja: Sizning to'g'ridan-to'g'ri referallaringiz. Ular har bir harakatda sizga ball olib keladi.</b>\n"
    "2. <b>👥 2-daraja: Sizning referallaringizning referallari. Ularning harakatlari uchun ham siz ball to'playsiz.</b>\n"
    "3. <b>👨‍👩‍👧‍👦 3-daraja: 3-darajali referallar orqali ham ball yig'ishingiz mumkin.</b>\n"

    "<b>🔗 Referal havolangizni do'stlaringiz bilan ulashing va ko'proq ball to'plang!</b>\n"

    f"<b>Sizning shaxsiy referal havolangiz:</b> <code>{referal_link}</code>\n"

    "<b>📊 Ballaringizni kuzatib boring:</b> `Menign ballarim`\n"

    "<b>🆘 Yordam kerak bo'lsa:</b> `/help`\n"

    "<b>💼 Admin bilan bog'lanish:</b> @admin_username\n"

    "<b>🔥 Omad tilaymiz!</b>")
    await message.answer(text=response_text, parse_mode="html")

