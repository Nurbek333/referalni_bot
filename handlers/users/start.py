from aiogram.types import Message
from loader import dp, db, bot, ADMINS
from aiogram.filters import CommandStart,Command
from keyboard_buttons.button import main_keyboard
import io
from aiogram.types import InputFile
from filters.admin import IsBotAdminFilter
import pandas as pd
from aiogram.types import BufferedInputFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from filters.check_sub_channel import IsCheckSubChannels
from loader import bot,dp,CHANNELS
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message,InlineKeyboardButton
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

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
    top_users = db.get_top_users_by_referrals()
    if not top_users:
        await message.answer("No users found.")
        return
    
    text = "🏆 Top Users by Points 🏆\n\n"
    for idx, user in enumerate(top_users):
        sticker = stickers[idx] if idx < len(stickers) else "🔸"  # Agar ro'yxatda stikerlar tugasa, oddiy belgi ishlatamiz
        text += f"<b>{sticker} Username: {user[1]}, Referrals: {user[2]}</b>\n\n"
    
    await message.answer(text)

# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from aiogram.types import FSInputFile

# # PDF yaratish funksiyasi
# def generate_referral_pdf(users_with_referrals):
#     pdf_file = "referral_stats.pdf"
#     c = canvas.Canvas(pdf_file, pagesize=letter)
#     width, height = letter
#     y = height - 40  # PDFni yuqorisidan boshlaymiz

#     c.setFont("Helvetica-Bold", 16)
#     c.drawString(100, y, "Foydalanuvchilar va ularning referral soni:")
    
#     y -= 30
#     c.setFont("Helvetica", 12)

#     if not users_with_referrals:
#         c.drawString(100, y, "Hozircha hech kim referral qilmagan.")
#     else:
#         for idx, (user_id, username, referrals_count) in enumerate(users_with_referrals, start=1):
#             c.drawString(100, y, f"{idx}. {username} - Referral soni: {referrals_count}")
#             y -= 20  # Har bir qator orasida bo'sh joy qoldiramiz

#     c.save()
#     return pdf_file


# @dp.message(Command("admins_referal"),IsBotAdminFilter(ADMINS))
# async def show_referral_stats(message: Message):
#     users_with_referrals = db.get_users_with_referral_counts()

#     # PDF yaratish
#     pdf_file = generate_referral_pdf(users_with_referrals)
    
#     # PDF file’ni jo'natish
#     pdf_document = FSInputFile(pdf_file)
#     await message.answer_document(pdf_document)



@dp.message(lambda message: message.text == "Natijalar")
async def export_to_pdf(message: Message):
    ADMIN_ID = 6214256605
    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizda ushbu buyrug'ni bajarish huquqi yo'q.")
        return

   # Foydalanuvchi ma'lumotlarini olish (masalan, database dan)
    users = db.select_all_users()

    # Ma'lumotlarni pandas DataFrame formatida olish
    df = pd.DataFrame(users, columns=["user_id", "username", "points", "referrer_id", "level_1_points", "level_2_points", "level_3_points"])

    # PDF faylga saqlash
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Jadval uchun ma'lumotlar
    data = [df.columns.tolist()] + df.values.tolist()

    # Jadval yaratish
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONT', (0,1), (-1,-1), 'Helvetica')
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)  # Fayl o'qish uchun boshlanishiga qaytarish

    # PDF faylni yuborish
    pdf_file = BufferedInputFile(buffer.read(), filename='users_data.pdf')
    await bot.send_document(
        message.from_user.id, 
        pdf_file
    )

    # Faylni diskdan o'chirish (agar kerak bo'lsa)
    buffer.close()

    await message.answer("Ma'lumotlar PDF faylga saqlandi va yuborildi.")




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
