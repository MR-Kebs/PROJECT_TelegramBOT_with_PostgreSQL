import os
from dotenv import load_dotenv
import telebot
import keyboards
import database


load_dotenv()
api_key = os.getenv("BOT_TOKEN")
print(f"Ключ загружен: {api_key[:4]}...")

bot = telebot.TeleBot(api_key)

user_sessions = {} 
"""
На память не забыть
user_sessions = {
    user_id: {  
        'step': 'menu',
        'data': {
            'mood': None,
            'work': None,
            'sleep': None,
            'comment': None
        }
    }
}
"""


# Роут отправляет в менюшку
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать в меню!\nНажмите "+" для добавления дня.')
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboards.menu())



###########################
# РОУТЫ ДЛЯ ДОБАВЛЕНИЯ ДНЯ
###########################
"""
Тут пипец все непонятно, только я смогу разобраться, я потом тебе комменты сделаю сладенький. 
я до часу ночи сидел.
На самом деле ничего сложного тут нет, просто все подряд написано, а с роутами по другому и не получается.
"""

def is_mood(call):
    return call.data.startswith("mood:") and user_sessions.get(call.from_user.id, {}).get("step") == "mood"

def is_work(call):
    return call.data.startswith("work_hours:") and call.data != "work_hours:other" and user_sessions.get(call.from_user.id, {}).get("step") == "work_hours"

def is_sleep(call):
    return call.data.startswith("sleep_hours:") and call.data != "sleep_hours:other" and user_sessions.get(call.from_user.id, {}).get("step") == "sleep_hours"

def is_work_other(call):
    return call.data == "work_hours:other" and user_sessions.get(call.from_user.id, {}).get("step") == "work_hours"
 
def is_sleep_other(call):
    return call.data == "sleep_hours:other" and user_sessions.get(call.from_user.id, {}).get("step") == "sleep_hours"

def is_comment_yes(call):
    return call.data == "comment:yes" and user_sessions.get(call.from_user.id, {}).get("step") == "ask_comment"

def is_comment_skip(call):
    return call.data == "comment:skip" and user_sessions.get(call.from_user.id, {}).get("step") == "ask_comment"
    
# Роут для создания сессии в словаре, главная задача дать статус для следущего роута и отправить текст
@bot.callback_query_handler(func=lambda call: call.data == "add_day")
def add_day(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id] = {"step": "mood", "data": {}}
    bot.send_message(
        call.message.chat.id, 
        'Оцени свое настроение сегодня от 1 до 5, где 1 - ужасно 😞, 5 - отлично 🤩:', 
        reply_markup=keyboards.mood()
    )


# Роут обработки настроения, главная задача дать статус для следущего роута и отправить текст
@bot.callback_query_handler(is_mood)
def add_mood(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id]["step"] = "work_hours"
    user_sessions[user_id]["data"]["mood"] = int(call.data.split(":")[1])
    bot.send_message(
        call.message.chat.id, 
        'Сколько часов ты потратил на полезную работу/учебу?', 
        reply_markup=keyboards.work_hours()
    )


# Роут обработки кол-во часов работы, главная задача дать статус для следущего роута и отправить текст
@bot.callback_query_handler(is_work)
def add_work(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id]["step"] = "sleep_hours"
    user_sessions[user_id]["data"]["work"] = int(call.data.split(":")[1])
    bot.send_message(
        call.message.chat.id, 
        'Сколько часов ты спал?', 
        reply_markup=keyboards.sleep_hours()
    )

@bot.callback_query_handler(is_work_other)
def add_work_other(call):
    bot.answer_callback_query(call.id)
    user_sessions[call.from_user.id]["step"] = "work_hours_other"
    bot.send_message(call.message.chat.id, "Введи количество часов работы цифрами:")


@bot.message_handler(func=lambda msg: user_sessions.get(msg.from_user.id, {}).get("step") == "work_hours_other")
def handle_work_other(message):
    user_id = message.from_user.id

    try:
        user_sessions[user_id]["data"]["work"] = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Введи число:")
        return

    user_sessions[user_id]["step"] = "sleep_hours"
    bot.send_message(message.chat.id, "Сколько часов ты спал?", reply_markup=keyboards.sleep_hours())


# Роут обработки кол-во часов сна, главная задача дать статус для следущего роута и отправить текст
@bot.callback_query_handler(is_sleep)
def add_sleep(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id]["step"] = "ask_comment"
    user_sessions[user_id]["data"]["sleep"] = int(call.data.split(":")[1])
    bot.send_message(
        call.message.chat.id,
        "Хочешь добавить комментарий?",
        reply_markup=keyboards.add_comment()
    )

@bot.callback_query_handler(is_sleep_other)
def add_sleep_other(call):
    bot.answer_callback_query(call.id)
    user_sessions[call.from_user.id]["step"] = "sleep_hours_other"
    bot.send_message(call.message.chat.id, "Введи количество часов сна цифрами:")


@bot.message_handler(func=lambda msg: user_sessions.get(msg.from_user.id, {}).get("step") == "sleep_hours_other")
def handle_sleep_other(message):
    user_id = message.from_user.id

    try:
        user_sessions[user_id]["data"]["sleep"] = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Введи число:")
        return

    user_sessions[user_id]["step"] = "ask_comment"
    bot.send_message(message.chat.id, "Хочешь добавить комментарий?", reply_markup=keyboards.add_comment())


@bot.callback_query_handler(is_comment_yes)
def comment_yes(call):
    bot.answer_callback_query(call.id)
    user_sessions[call.from_user.id]["step"] = "comment"
    bot.send_message(call.message.chat.id, "Напиши короткий комментарий о дне:")

@bot.callback_query_handler(is_comment_skip)
def comment_skip(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    session = user_sessions[user_id]["data"]
    session["comment"] = ""
    
    database.add_entry(
        user_id,
        session["mood"],
        session["work"],
        session["sleep"],
        session["comment"]
    )
    
    del user_sessions[user_id]
    bot.send_message(call.message.chat.id, "✅ День записан!")
    bot.send_message(call.message.chat.id, "Выбери действие:", reply_markup=keyboards.menu())

@bot.message_handler(func=lambda message: user_sessions.get(message.from_user.id, {}).get("step") == "comment")
def add_comment(message):
    user_id = message.from_user.id
    session = user_sessions[user_id]["data"]
    session["comment"] = message.text
    
    database.add_entry(
        user_id,
        session["mood"],
        session["work"],
        session["sleep"],
        session["comment"]
    )
    
    del user_sessions[user_id]
    bot.send_message(message.chat.id, "✅ День записан!")
    bot.send_message(message.chat.id, "Выбери действие:", reply_markup=keyboards.menu())


###########################
# РОУТЫ ДЛЯ МЕНЮ
###########################


if __name__ == "__main__":
    print('Ботик запущен')
    bot.polling(non_stop=True)
