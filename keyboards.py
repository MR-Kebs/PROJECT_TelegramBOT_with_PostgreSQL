from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

def start():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Начать", callback_data="start")
    )
    return markup