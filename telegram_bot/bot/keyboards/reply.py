from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📋 Задачи"), KeyboardButton("💬 Комментарии"))
    keyboard.add(KeyboardButton("➕ Создать задачу"), KeyboardButton("➕ Создать комментарий"))
    keyboard.add(KeyboardButton("🌐 Изменить язык"))
    return keyboard