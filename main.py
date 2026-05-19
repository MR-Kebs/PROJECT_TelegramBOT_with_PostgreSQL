import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import keyboards


load_dotenv()
api_key = os.getenv("BOT_TOKEN")
print(f"Ключ загружен: {api_key[:4]}...")

bot = telebot.TeleBot(api_key)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать в меню!\nНажмите "+" для добавления дня.')
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboards.menu())


@bot.callback_query_handler(func=lambda call: call.data == "add_day")
def add_day(call):

    data = {
        "user_id": call.from_user.id,
        'mood': None,
        'work_hours': None,
        'sleep_hours': None,
        'commit': None
    }
    bot.send_message(call.message.chat.id, 'Выберите ваше настроение от 1😞 до 5🤩:', reply_markup=keyboards.mood())



@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    user_id = call.from_user.id
    
    if user_states.get(user_id) == "waiting_mood":
        pass



if __name__ == "__main__":
    print('Ботик запущен')
    bot.polling(non_stop=True)
