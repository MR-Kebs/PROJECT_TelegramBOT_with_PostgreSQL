import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


load_dotenv()
api_key = os.getenv("BOT_TOKEN")
print(f"Ключ загружен: {api_key[:4]}...")


    