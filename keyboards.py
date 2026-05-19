from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

def menu():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("➕ Записать", callback_data="add_day"),
        InlineKeyboardButton("Статистика", callback_data="stats"),
        InlineKeyboardButton("История", callback_data="history"),
        InlineKeyboardButton("Настройки", callback_data="settings"),
        InlineKeyboardButton("Помощь", callback_data="help"),
        InlineKeyboardButton("Очистить данные", callback_data="clear_data")
    )
    return markup

def mood():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("1 - 😞", callback_data="1"),
        InlineKeyboardButton("2 - 😐", callback_data="2"),
        InlineKeyboardButton("3 - 🙂", callback_data="3"),
        InlineKeyboardButton("4 - 😊", callback_data="4"),
        InlineKeyboardButton("5 - 🤩", callback_data="5")
    )
    return markup

def stats():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📅 За неделю", callback_data="week"),
        InlineKeyboardButton("📅 За месяц", callback_data="month"),
        InlineKeyboardButton("🔍 Мои инсайты", callback_data="insights"),
        InlineKeyboardButton("📉 График", callback_data="graphs"),
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    return markup
