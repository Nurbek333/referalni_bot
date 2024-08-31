from aiogram.types import Message
from loader import dp, db, bot
from aiogram.filters import CommandStart,Command
from keyboard_buttons.button import main_keyboard
import io
from baza.sqlite import Database
import pandas as pd
from aiogram.types import BufferedInputFile

from filters.check_sub_channel import IsCheckSubChannels
from loader import bot,dp,CHANNELS
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message,InlineKeyboardButton


@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    text_parts = message.text.split()

    # Get the referral code if it exists
    referrer_id = int(text_parts[1]) if len(text_parts) > 1 and text_parts[1].isdigit() else None

    # Add the user if they don't exist in the database
    if not db.user_exists(user_id):
        db.add_user(user_id, username, referrer_id)

        # Add referral if the referrer_id is valid
        if referrer_id and db.user_exists(referrer_id):
            db.add_referral(referrer_id, user_id)

            # Referrerga 1-daraja ballarini qo'shish
            db.add_points(referrer_id, 1, level=1)

            # Referrerning foydalanuvchisiga xabar yuborish
            referrer_username = db.get_username(referrer_id)
            await bot.send_message(
                referrer_id, 
                f"<b>Sizning referalingiz orqali <code>{username}</code> botga kirdi!</b>", 
                parse_mode="html"
            )

    await message.answer("Salom! Quyidagi tugmalar orqali botdan foydalaning:", reply_markup=main_keyboard)

@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message:Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index,channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
    inline_channel.adjust(1,repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)


@dp.message(lambda message: message.text == "Referal link")
async def referal_link(message: Message):
    user_id = message.from_user.id
    referal_link = f"https://t.me/dwefe_bot?start={user_id}"
    photo = "https://elements-cover-images-0.imgix.net/bf00ec3e-a269-471f-aaca-bf940f26d67c?q=80&w=316&fit=max&fm=jpeg&s=e261ce5ef60df18f3d047fb88ee5502c"
    response_text = (
        f"🌟 <b>Sizning referal havolangiz tayyor!</b> 🌟\n\n"
        "<b>Sizning referal havolangizni do'stlaringizga ulashing va botdan ko'proq foyda ko'ring:</b>\n\n"
        f"➡️ <code>{referal_link}</code>\n\n"
        "📈 <b>Har bir yangi foydalanuvchi uchun siz ball olasiz!</b> \n\n"
        "<b>Katta bonuslarga ega bo'lish uchun imkoniyatni qo'ldan boy bermang:</b>\n\n"
        "1️⃣ <b>Ko'proq ball yig'ing</b>\n\n"
        "2️⃣ <b>Eksklyuziv sovg'alarga ega bo'ling</b>\n\n"
        "3️⃣ <b>Maxsus chegirmalar va imkoniyatlardan foydalaning</b>\n\n"
        "🤝 <b>Do'stlaringizni taklif qiling va imkoniyatlaringizni kengaytiring!</b>"
    )
    await message.answer_photo(photo=photo, caption=response_text, parse_mode="html")

@dp.message(lambda message: message.text == "Mening ballarim")
async def my_points(message: Message):
    user_id = message.from_user.id
    points = db.get_user_points(user_id)
    photo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtWRPo-AEN1M9MvQbhJsxNdpHx-83Sld_z3DLGfVVQoIOl2iwFidtclCUfadqWN_it25Q&usqp=CAU"
    response_text = (
        f"🎉 Sizning hozirgi ballaringiz: *{points:.1f}* 🎉\n\n"
        "💡 *Ballaringizni yig'ish orqali siz botdagi maxsus imkoniyatlardan foydalanishingiz mumkin.*\n\n"
        "🔓 *Bonuslar ro'yxati:* \n\n"
        "1️⃣  *10 ball* - 🎁 Maxsus sovg'a\n\n"
        "2️⃣  *20 ball* - ⚙️ Qo'shimcha funksiyalar\n\n"
        "3️⃣  *50 ball* - 💸 Chegirmali takliflar\n\n"
        "🔗 *Referal havolangizni do'stlaringiz bilan ulashing va ko'proq ball yig'ing!*"
    )
    await message.answer_photo(photo=photo, caption=response_text, parse_mode="Markdown")



# Bu yerda har bir o'rin uchun mos stikerlarni ro'yxat qilib olamiz
stickers = [
    "🥇",  # 1-o'rin
    "🥈",  # 2-o'rin
    "🥉",  # 3-o'rin
    "🏅",  # 4-o'rin
    "🎖",  # 5-o'rin
    "🏆",  # 6-o'rin
    "🎗",  # 7-o'rin
    "🎟",  # 8-o'rin
    "🔖",  # 9-o'rin
    "🎫"   # 10-o'rin
]

@dp.message(lambda message: message.text == "Top 10 Foydalanuvchilar")
async def handle_top_users(message: Message):
    top_users = db.get_top_users_by_points()
    if not top_users:
        await message.answer("No users found.")
        return
    
    text = "🏆 Top Users by Points 🏆\n\n"
    for idx, user in enumerate(top_users):
        sticker = stickers[idx] if idx < len(stickers) else "🔸"  # Agar ro'yxatda stikerlar tugasa, oddiy belgi ishlatamiz
        text += f"<b>{sticker} Username: {user[1]}, Points: {user[2]}</b>\n\n"
    
    await message.answer(text)




@dp.message(Command("foyda"))
async def export_to_excel(message: Message):
    # Admin IDni belgilash (bu yerda adminning Telegram ID sini qo'ying)
    ADMIN_ID = 6214256605

    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizda ushbu buyrug'ni bajarish huquqi yo'q.")
        return

    # Foydalanuvchi ma'lumotlarini olish (masalan, database dan)
    users = db.select_all_users()

    # Ma'lumotlarni pandas DataFrame formatida olish
    df = pd.DataFrame(users, columns=["user_id", "username", "points", "referrer_id", "level_1_points", "level_2_points", "level_3_points"])

    # Excel faylga saqlash
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Users', index=False)
    
    buffer.seek(0)  # Fayl o'qish uchun boshlanishiga qaytarish

    # Faylni Diskka Saqlash
    with open('users_data.xlsx', 'wb') as f:
        f.write(buffer.getvalue())


    await bot.send_document(
        message.from_user.id, 
        BufferedInputFile.from_file('C:\\Users\\Professional\\Desktop\\Simple-Aiogram-Template-master\\users_data.xlsx')
    )


    # Faylni diskdan o'chirish (agar kerak bo'lsa)
    import os
    # os.path('users_data.xlsx')
    os.remove('users_data.xlsx')

    await message.answer("Ma'lumotlar Excel faylga saqlandi va yuborildi.")




@dp.message(Command('my_points'))
async def my_points(message: Message):
    user_id = message.from_user.id
    points = db.get_user_points(user_id)
    photo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtWRPo-AEN1M9MvQbhJsxNdpHx-83Sld_z3DLGfVVQoIOl2iwFidtclCUfadqWN_it25Q&usqp=CAU"
    response_text = (
        f"🎉 Sizning hozirgi ballaringiz: *{points:.1f}* 🎉\n\n"
        "💡 *Ballaringizni yig'ish orqali siz botdagi maxsus imkoniyatlardan foydalanishingiz mumkin.*\n\n"
        "🔓 *Bonuslar ro'yxati:* \n\n"
        "1️⃣  *10 ball* - 🎁 Maxsus sovg'a\n\n"
        "2️⃣  *20 ball* - ⚙️ Qo'shimcha funksiyalar\n\n"
        "3️⃣  *50 ball* - 💸 Chegirmali takliflar\n\n"
        "🔗 *Referal havolangizni do'stlaringiz bilan ulashing va ko'proq ball yig'ing!*"
    )
    await message.answer_photo(photo=photo, caption=response_text, parse_mode="Markdown")


@dp.message(Command('referal'))
async def referal_link(message: Message):
    user_id = message.from_user.id
    referal_link = f"https://t.me/dwefe_bot?start={user_id}"
    photo = "https://elements-cover-images-0.imgix.net/bf00ec3e-a269-471f-aaca-bf940f26d67c?q=80&w=316&fit=max&fm=jpeg&s=e261ce5ef60df18f3d047fb88ee5502c"
    response_text = (
        f"🌟 <b>Sizning referal havolangiz tayyor!</b> 🌟\n\n"
        "<b>Sizning referal havolangizni do'stlaringizga ulashing va botdan ko'proq foyda ko'ring:</b>\n\n"
        f"➡️ <code>{referal_link}</code>\n\n"
        "📈 <b>Har bir yangi foydalanuvchi uchun siz ball olasiz!</b> \n\n"
        "<b>Katta bonuslarga ega bo'lish uchun imkoniyatni qo'ldan boy bermang:</b>\n\n"
        "1️⃣ <b>Ko'proq ball yig'ing</b>\n\n"
        "2️⃣ <b>Eksklyuziv sovg'alarga ega bo'ling</b>\n\n"
        "3️⃣ <b>Maxsus chegirmalar va imkoniyatlardan foydalaning</b>\n\n"
        "🤝 <b>Do'stlaringizni taklif qiling va imkoniyatlaringizni kengaytiring!</b>"
    )
    await message.answer_photo(photo=photo, caption=response_text, parse_mode="html")
