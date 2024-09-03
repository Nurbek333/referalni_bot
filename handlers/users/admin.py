from filters.check_sub_channel import IsCheckSubChannels
from loader import bot,db,dp,ADMINS
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message,InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.filters import Command
from filters.admin import IsBotAdminFilter
from states.reklama import Adverts
from aiogram.fsm.context import FSMContext #new
from keyboard_buttons import admin_keyboard
import time 
import sqlite3
from datetime import datetime
from aiogram import F


@dp.message(Command("admin"),IsBotAdminFilter(ADMINS))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)


# @dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
# async def users_count(message:Message):
#     counts = db.count_users()
#     text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
#     await message.answer(text=text)
    

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from aiogram.types import FSInputFile

# PDF yaratish funksiyasi
def generate_referral_pdf(users_with_referrals):
    pdf_file = "referral_stats.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    y = height - 40  # PDFni yuqorisidan boshlaymiz

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y, "Foydalanuvchilar va ularning referral soni:")
    
    y -= 30
    c.setFont("Helvetica", 12)

    if not users_with_referrals:
        c.drawString(100, y, "Hozircha hech kim referral qilmagan.")
    else:
        for idx, (user_id, username, referrals_count) in enumerate(users_with_referrals, start=1):
            c.drawString(100, y, f"{idx}. {username} - Referral soni: {referrals_count}")
            y -= 20  # Har bir qator orasida bo'sh joy qoldiramiz

    c.save()
    return pdf_file


@dp.message(F.text=="Referallar soni")
async def show_referral_stats(message: Message):
    user_id = message.from_user.id
    
    # Foydalanuvchini adminlar ro'yxatidan tekshiramiz
    if user_id not in ADMINS:
        await message.answer("Siz bu buyruqdan foydalana olmaysiz, faqat adminlar foydalanishi mumkin.")
        return

    # Agar foydalanuvchi admin bo'lsa, referral statistikasini ko'rsatamiz
    users_with_referrals = db.get_users_with_referral_counts()

    # PDF yaratish
    pdf_file = generate_referral_pdf(users_with_referrals)
    
    # PDF file’ni jo'natish
    pdf_document = FSInputFile(pdf_file)
    await message.answer_document(pdf_document)
    

@dp.message(F.text=="Reklama yuborish",IsBotAdminFilter(ADMINS))
async def advert_dp(message:Message,state:FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message:Message,state:FSMContext):
    
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = db.get_all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],from_chat_id=from_chat_id,message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.01)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()

async def admin_panel(message: Message):
    if message.from_user.id in ADMINS:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Foydalanuvchilar ro'yxati", callback_data='users'))
        await message.answer("Admin panelga xush kelibsiz!", reply_markup=keyboard)
    else:
        await message.answer("Siz admin emassiz!")


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db
        self.create_table_bot_info()

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_bot_info(self):
        sql = """
        CREATE TABLE IF NOT EXISTS BotInfo(
        start_time TEXT
        );
        """
        self.execute(sql, commit=True)
        # Agar `BotInfo` jadvali bo'sh bo'lsa, botning ishga tushgan vaqtini qo'shing
        if not self.execute("SELECT * FROM BotInfo;", fetchone=True):
            self.execute("INSERT INTO BotInfo (start_time) VALUES (?);", parameters=(datetime.now().isoformat(),), commit=True)

    def get_bot_start_time(self):
        return self.execute("SELECT start_time FROM BotInfo;", fetchone=True)[0]

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)
    
    def get_all_users_id(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        return users
    
    def get_users_with_referral_counts(self):
        """
        Har bir foydalanuvchining username va referral sonini kamayish tartibida qaytaradi.
        """
        sql = """
        SELECT u.user_id, u.username, COUNT(r.referred_id) AS referrals_count
        FROM users u
        LEFT JOIN Referrals r ON u.user_id = r.referrer_id
        GROUP BY u.user_id, u.username
        ORDER BY referrals_count DESC;  -- Referral soni bo'yicha kamayish tartibida
        """
        return self.execute(sql, fetchall=True)

db = Database()

async def get_bot_statistics():
    total_users = db.count_users()[0]
    bot_start_time = db.get_bot_start_time()
    start_time = datetime.fromisoformat(bot_start_time)
    uptime = datetime.now() - start_time
    days_uptime = uptime.days
    
    # Uptime formatlash
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_uptime = f"{days_uptime} kun, {hours} soat, {minutes} daqiqa, {seconds} soniya"
    
    error_count = 0  # Bu qiymatni haqiqiy xatoliklar bilan almashtiring

    return {
        "total_users": total_users,
        "error_count": error_count,
        "uptime": formatted_uptime,
        "days_uptime": days_uptime
    }

@dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
async def users_count(message:Message):
    stats = await get_bot_statistics()
    
    response = (
        f"👥 *Jami foydalanuvchilar:* {stats['total_users']}\n\n"
        f"⚠️ *Bot xatoliklari:* {stats['error_count']}\n\n"
        f"⏳ *Bot ishga tushgan vaqt:* {stats['uptime']}\n\n"
        f"📅 *Kunlar soni:* {stats['days_uptime']}"
    )
    
    # Rasmning URL manzili
    photo_url = "https://static3.tgstat.ru/channels/_0/7a/7a13404ed6199848a0dd561a94567e60.jpg"
    
    # Rasmni yuborish
    await message.answer_photo(photo=photo_url, caption=response, parse_mode='Markdown')