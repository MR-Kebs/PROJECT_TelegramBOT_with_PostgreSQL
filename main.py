import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


load_dotenv()
api_key = os.getenv("BOT_TOKEN")
print(f"Ключ загружен: {api_key[:4]}...")

bot = telebot.TeleBot(api_key)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Салам пополам!')



if __name__ == "__main__":
    print('Ботик запущен')
    bot.polling(non_stop=True)
