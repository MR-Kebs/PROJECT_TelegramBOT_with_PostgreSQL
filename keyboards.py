from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

def menu():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("➕ Записать", callback_data="add_day"),
        InlineKeyboardButton("📅 Статистика", callback_data="stats"),
        InlineKeyboardButton("⏱️ История", callback_data="history"),
        InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        InlineKeyboardButton("🙏 Помощь", callback_data="help"),
        InlineKeyboardButton("🧹 Очистить данные", callback_data="clear_data")
    )
    return markup

def mood():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("1 - 😞", callback_data="mood:1"),
        InlineKeyboardButton("2 - 😐", callback_data="mood:2"),
        InlineKeyboardButton("3 - 🙂", callback_data="mood:3"),
        InlineKeyboardButton("4 - 😊", callback_data="mood:4"),
        InlineKeyboardButton("5 - 🤩", callback_data="mood:5")
    )
    return markup

def work_hours():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("1 час", callback_data="work_hours:1"),
        InlineKeyboardButton("2 часа", callback_data="work_hours:2"),
        InlineKeyboardButton("3 часа", callback_data="work_hours:3"),
        InlineKeyboardButton("4 часа", callback_data="work_hours:4"),
        InlineKeyboardButton("5 часов", callback_data="work_hours:5"),
        InlineKeyboardButton("Другое", callback_data="work_hours:other")
    )
    return markup

def sleep_hours():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("2 часа", callback_data="sleep_hours:2"),
        InlineKeyboardButton("4 часа", callback_data="sleep_hours:4"),
        InlineKeyboardButton("6 часов", callback_data="sleep_hours:6"),
        InlineKeyboardButton("8 часов", callback_data="sleep_hours:8"),
        InlineKeyboardButton("10 часов", callback_data="sleep_hours:10"),
        InlineKeyboardButton("Другое", callback_data="sleep_hours:other")
    )
    return markup

# ИСТОРИЯ

def history():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("За неделю (7 дней)", callback_data="history_week"),
        InlineKeyboardButton("За месяц (30 дней)", callback_data="history_month"),
        InlineKeyboardButton("Всю историю", callback_data="history_all"),
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    return markup

# СТАТИСТИКА

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

def add_comment():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Да", callback_data="comment:yes"),
        InlineKeyboardButton("Пропустить", callback_data="comment:skip")
    )
    return markup

# ОЧИСТКА ДАННЫХ

def clear():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Да", callback_data="clear_confirm"),
        InlineKeyboardButton("Нет", callback_data="back")
    )
    return markup


# Назад
def back():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    return markup

# ГРАФИКИ
def graphs():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("За неделю (7 дней)", callback_data="graph_week"),
        InlineKeyboardButton("За две недели (14 дней)", callback_data="graph_two_weeks"),
        InlineKeyboardButton("За месяц (30 дней)", callback_data="graph_month"),
        InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    return markup