from aiogram.types import Message
from loader import dp
from aiogram.filters import Command


#help commands
@dp.message(Command("help"))
async def help_commands(message:Message):
    help_text = """
<b>🆘 Yordam:</b>    

Botimiz qanday ishlashini tushuntiruvchi ko'rsatmalar:    

1. <b>🎯 Referal tizimi:</b>    
  - Do'stlaringizni taklif qiling va ball to'plang.    
  - Referal havolangizni olish uchun /referal buyrug'ini bosing.     

2. <b>📊 Ballaringizni kuzatish:</b>    
  - O'zingiz to'plagan ballaringizni ko'rish uchun /my_points buyrug'ini yozing.     

3. <b>💬 Yordam kerakmi?</b>
  - Qo'shimcha yordam olish uchun <a href="https://t.me/admin_username">Admin bilan bog'laning</a>.         

<b>Qo'llab-quvvatlash:</b> Botda duch kelgan muammolaringiz yoki savollaringiz bo'lsa, yuqoridagi admin bilan bog'lanishingiz mumkin.     

<b>🔗 Foydali buyruqlar:</b>    
  - /start: Botni qayta ishga tushirish.  
  - /referal: Referal havolangizni olish.  
  - /about: Bot haqida ma'lumot olish.  
  - /my_points: Ballaringizni ko'rish.        

<b>🔥 Omad tilaymiz!</b>    
    """
    await message.answer(help_text, parse_mode="html")
