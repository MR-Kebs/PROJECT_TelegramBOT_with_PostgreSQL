import os
from dotenv import load_dotenv
import telebot
import keyboards
import database
from scheduler import start_scheduler
import scheduler
import re
from charts import generate_stats_image


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
    if scheduler.active == True:
        user_sessions[user_id] = {"step": "mood", "data": {}}
        bot.send_message(
            call.message.chat.id, 
            'Оцени свое настроение сегодня от 1 до 5, где 1 - ужасно 😞, 5 - отлично 🤩:', 
            reply_markup=keyboards.mood()
        )
    else:
        bot.send_message(call.message.chat.id,
        "Вы уже делали запись сегодня ❤",
        reply_markup=keyboards.me_delete_back())


# Роут обработки настроения, главная задача дать статус для следущего роута и отправить текст
@bot.callback_query_handler(is_mood)
def add_mood(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id]["step"] = "work_hours"
    user_sessions[user_id]["data"]["mood"] = int(call.data.split(":")[1])
    bot.edit_message_text(
        f"😊 Твое настроение сегодня: _{user_sessions[user_id]['data']['mood']}_",
        call.message.chat.id,
        call.message.message_id, 
        parse_mode="Markdown"
    )
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
    bot.edit_message_text(
        f"💼 Ты работал сегодня: _{user_sessions[user_id]['data']['work']} часов_",
        call.message.chat.id,
        call.message.message_id, 
        parse_mode="Markdown"
    )
    bot.send_message(
        call.message.chat.id, 
        'Сколько часов ты спал?', 
        reply_markup=keyboards.sleep_hours()
    )

@bot.callback_query_handler(is_work_other)
def add_work_other(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id]["step"] = "work_hours_other"
    user_sessions[user_id]["work_msg_id"] = call.message.message_id
    bot.edit_message_text(
        "Введи количество часов работы цифрами:",
        call.message.chat.id,
        call.message.message_id
    )


@bot.message_handler(func=lambda message: user_sessions.get(message.from_user.id, {}).get("step") == "work_hours_other")
def handle_work_other(message):
    user_id = message.from_user.id
    msg_id = user_sessions[user_id]["work_msg_id"]

    try:
        user_sessions[user_id]["data"]["work"] = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Введи число:")
        return

    if msg_id:
        bot.edit_message_text(
            f"💼 Ты работал сегодня: _{user_sessions[user_id]['data']['work']} часов_",
            message.chat.id,
            msg_id, 
            parse_mode="Markdown"
        )

    user_sessions[user_id]["step"] = "sleep_hours"
    bot.send_message(message.chat.id, "Сколько часов ты спал?", reply_markup=keyboards.sleep_hours())


# Роут обработки кол-во часов сна, главная задача дать статус для следущего роута и отправить текст
@bot.callback_query_handler(is_sleep)
def add_sleep(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id]["step"] = "ask_comment"
    user_sessions[user_id]["data"]["sleep"] = int(call.data.split(":")[1])
    bot.edit_message_text(
        f"😴 Ты спал сегодня: _{user_sessions[user_id]['data']['sleep']} часов_",
        call.message.chat.id,
        call.message.message_id, 
        parse_mode="Markdown"
    )
    bot.send_message(
        call.message.chat.id,
        "Хочешь добавить комментарий?",
        reply_markup=keyboards.add_comment()
    )

@bot.callback_query_handler(is_sleep_other)
def add_sleep_other(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id]["step"] = "sleep_hours_other"
    user_sessions[user_id]["sleep_msg_id"] = call.message.message_id
    bot.edit_message_text(
        "Введи количество часов сна цифрами:",
        call.message.chat.id,
        call.message.message_id
    )
    


@bot.message_handler(func=lambda message: user_sessions.get(message.from_user.id, {}).get("step") == "sleep_hours_other")
def handle_sleep_other(message):
    user_id = message.from_user.id
    msg_id = user_sessions[user_id].get("sleep_msg_id")

    try:
        user_sessions[user_id]["data"]["sleep"] = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Введи число:")
        return

    if msg_id:
        bot.edit_message_text(
            f"😴 Ты спал сегодня: _{user_sessions[user_id]['data']['sleep']} часов_",
            message.chat.id,
            msg_id,
            parse_mode="Markdown"
        )

    user_sessions[user_id]["step"] = "ask_comment"
    bot.send_message(message.chat.id, "Хочешь добавить комментарий?", reply_markup=keyboards.add_comment())


@bot.callback_query_handler(is_comment_yes)
def comment_yes(call):
    bot.answer_callback_query(call.id)
    user_sessions[call.from_user.id]["step"] = "comment"
    user_sessions[call.from_user.id]["prompt_msg_id"] = call.message.message_id
    bot.edit_message_text(
        "Напиши короткий комментарий о дне:",
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(is_comment_skip)
def comment_skip(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    session = user_sessions[user_id]["data"]
    session["comment"] = ""

    bot.edit_message_text(
        "💬 Без комментария",
        call.message.chat.id,
        call.message.message_id
    )
    
    database.add_entry(
        user_id,
        session["mood"],
        session["work"],
        session["sleep"],
        session["comment"]
    )
    
    del user_sessions[user_id]
    scheduler.active = False
    bot.send_message(call.message.chat.id, "✅ День записан!")
    bot.send_message(call.message.chat.id, "Выбери действие:", reply_markup=keyboards.menu())

@bot.message_handler(func=lambda message: user_sessions.get(message.from_user.id, {}).get("step") == "comment")
def add_comment(message):
    user_id = message.from_user.id
    session = user_sessions[user_id]["data"]
    session["comment"] = message.text
    msg_id = user_sessions[user_id].get("prompt_msg_id")

    if msg_id:
        bot.edit_message_text(
            "💬 Комментарий добавлен",
            message.chat.id,
            msg_id
        )
    
    database.add_entry(
        user_id,
        session["mood"],
        session["work"],
        session["sleep"],
        session["comment"]
    )
    
    del user_sessions[user_id]
    scheduler.active = False
    bot.send_message(message.chat.id, "✅ День записан!")
    bot.send_message(message.chat.id, "Выбери действие:", reply_markup=keyboards.menu())


###########################
# ГЛОБАЛЬНЫЕ РОУТЫ
###########################

# Роут возвращения к меню
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выбери действие:", reply_markup=keyboards.menu())
    
# Роут возвращения к меню путем удаления себя
@bot.callback_query_handler(func=lambda call: call.data == "me_delete_back")
def me_delete_back(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

# Роут возвращения к меню из графиков
@bot.callback_query_handler(func=lambda call: call.data == "graphs_back")
def graphs_back(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Выбери действие:", reply_markup=keyboards.stats())


# Роут помощи
@bot.callback_query_handler(func=lambda call: call.data == "help")
def help(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 
    "🙏 *Помощь по боту*\n\n"
    "Я помогаю отслеживать твой день: настроение, продуктивность и сон. "
    "На основе записей строю статистику и даю персональные инсайты.\n\n"
    "📋 *Что умею:*\n"
    "➕ *Записать* — добавить день: настроение (1–5), часы работы/учёбы, сон и комментарий\n"
    "📅 *Статистика* — средние значения за неделю/месяц, инсайты и графики\n"
    "⏱️ *История* — список записей за неделю, месяц или всё время\n"
    "⚙️ *Настройки* — задать или убрать время ежедневного напоминания\n"
    "🧹 *Очистить данные* — полное удаление всех твоих записей (безвозвратно)\n\n"
    "Если что-то сломалось — перезапусти бота командой /start",
    parse_mode="Markdown", reply_markup=keyboards.me_delete_back())

###########################
# РОУТЫ ДЛЯ ОЧИСТКИ ДАННЫХ
###########################

# Роут для подтверждения очистки всех данных
@bot.callback_query_handler(func=lambda call: call.data == "clear_data")
def clear(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    rows = database.get_history(user_id)

    if not rows or rows[0] is None:
        bot.send_message(call.message.chat.id, "Нечего очищать.")
        return

    bot.send_message(call.message.chat.id, "Ты уверен, что хочешь очистить все данные? Это действие необратимо.", reply_markup=keyboards.clear())

# Роут очистки всех данных
@bot.callback_query_handler(func=lambda call: call.data == "clear_confirm")
def clear_confirm(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    database.clear_entries(user_id)
    bot.edit_message_text(
        "Все данные успешно очищены!",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboards.me_delete_back()
    )
    

###########################
# РОУТЫ ДЛЯ СТАТИСТИКИ
###########################

# Роут показа статистики
@bot.callback_query_handler(func=lambda call: call.data == "stats")
def show_stats(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    try:
        count = len(database.get_history(user_id))
        if count <= 2:
            bot.send_message(call.message.chat.id, "У тебя пока недостаточно записей для статистики. Добавь хотя бы 3 записи!", reply_markup=keyboards.me_delete_back())
        else:
            bot.send_message(call.message.chat.id, "Выбери действие:", reply_markup=keyboards.stats())
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка: {e}", reply_markup=keyboards.me_delete_back())

# Роут показа статистики за неделю
@bot.callback_query_handler(func=lambda call: call.data == "week")
def show_week(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    rows = database.get_stats_week(user_id)

    if not rows or rows[0] is None:
        bot.edit_message_text(
            "Нет записей за неделю.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboards.stats()
        )
        return

    bot.edit_message_text(
        f"Статистика за неделю:\n\n😊 Среднее настроение: {float(rows[0]):.1f}\n💼 Средняя работа: {float(rows[1]):.1f}\n😴 Средний сон: {float(rows[2]):.1f}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboards.stats()
    )
  

# Роут показа статистики за месяц
@bot.callback_query_handler(func=lambda call: call.data == "month")
def show_month(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    rows = database.get_stats_month(user_id)

    if not rows or rows[0] is None:
        bot.edit_message_text(
            "Нет записей за месяц.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboards.stats()
        )
        return

    bot.edit_message_text(
        f"Статистика за месяц:\n\n😊 Среднее настроение: {float(rows[0]):.1f}\n💼 Средняя работа: {float(rows[1]):.1f}\n😴 Средний сон: {float(rows[2]):.1f}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboards.stats()
    )

# Роут показа инсайтов
@bot.callback_query_handler(func=lambda call: call.data == "insights")
def show_insights(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    rows = database.get_insights(user_id)

    if not rows or rows[0] is None:
        bot.send_message(call.message.chat.id, "Нет инсайтов.")
        return

    bot.edit_message_text(
        f"Твой инсайт:\n\n_{rows[0]}_",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboards.stats()
    )
    
    

###########################
# РОУТЫ ДЛЯ ГРАФИКОВ
###########################

# Роут показа меню графиков
@bot.callback_query_handler(func=lambda call: call.data == "graphs")
def show_graphs(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        "Выберите период для графика:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboards.graphs()
    )

# Роут для вывода графика за неделю
@bot.callback_query_handler(func=lambda call: call.data == "graph_week")
def show_graph_week(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    interval = 7
    image_buffer = generate_stats_image(user_id, interval)
    if image_buffer is None:
        bot.edit_message_text(
            "Недостаточно данных за указанный период.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboards.graphs()
        )
        return

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(
        chat_id=call.message.chat.id,
        photo=image_buffer,
        caption=f"📈 Ваша статистика за последние дни: {interval}",
        reply_markup=keyboards.graphs()
    )
    image_buffer.close()


# Роут для вывода графика за две недели
@bot.callback_query_handler(func=lambda call: call.data == "graph_two_weeks")
def show_graph_two_weeks(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    interval = 14
    image_buffer = generate_stats_image(user_id, interval)
    if image_buffer is None:
        bot.edit_message_text(
            "Недостаточно данных за указанный период.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboards.graphs()
        )
        return

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(
        chat_id=call.message.chat.id,
        photo=image_buffer,
        caption=f"📈 Ваша статистика за последние дни: {interval}",
        reply_markup=keyboards.graphs()
    )
    image_buffer.close()
    
# Роут для вывода графика за месяц
@bot.callback_query_handler(func=lambda call: call.data == "graph_month")
def show_graph_month(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    interval = 30
    image_buffer = generate_stats_image(user_id, interval)
    if image_buffer is None:
        bot.edit_message_text(
            "Недостаточно данных за указанный период.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboards.graphs()
        )
        return

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_photo(
        chat_id=call.message.chat.id,
        photo=image_buffer,
        caption=f"📈 Ваша статистика за последние дни: {interval}",
        reply_markup=keyboards.graphs()
    )
    image_buffer.close()

###########################
# РОУТЫ ДЛЯ ИСТОРИИ
###########################

# Роут показа истории
@bot.callback_query_handler(func=lambda call: call.data == "history")
def show_history(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    rows = database.get_history(user_id)

    if not rows or rows[0] is None:
        bot.send_message(call.message.chat.id, "Нет записей.", reply_markup=keyboards.me_delete_back())
        return

    bot.send_message(call.message.chat.id, "Выберите за какой период показать историю:", reply_markup=keyboards.history())

# ЗА НЕДЕЛЮ
@bot.callback_query_handler(func=lambda call: call.data == "history_week")
def show_history_week(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    rows = database.get_history(user_id, 7)

    lines = []
    for row in rows:
        id, u_id, date, mood, work, sleep, comment, created_at = row
            
        shema = (
            f"📅 {date}\n"
            f"😊 Настроение: {mood} \n"
            f"💼 Работа: {float(work)} \n"
            f"😴 Сон: {float(sleep)} \n"
            f"💬 Комментарий: {comment + '\n' if comment else 'без комментария \n'}"
            f"🕐 Создано: {str(created_at)[11:19]}"
        )
        lines.append(shema)

    bot.edit_message_text(
        f"История за неделю:\n\n{'\n\n'.join(lines)}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboards.history()
    )


# ЗА МЕСЯЦ
@bot.callback_query_handler(func=lambda call: call.data == "history_month")
def show_history_month(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    rows = database.get_history(user_id, 30)

    lines = []
    for row in rows:
        id, u_id, date, mood, work, sleep, comment, created_at = row
            
        shema = (
            f"📅 {date}\n"
            f"😊 Настроение: {mood} \n"
            f"💼 Работа: {float(work)} \n"
            f"😴 Сон: {float(sleep)} \n"
            f"💬 Комментарий: {comment + '\n' if comment else 'без комментария \n'}"
            f"🕐 Создано: {str(created_at)[11:19]}"
        )
        lines.append(shema)

    bot.edit_message_text(
        f"История за месяц:\n\n{'\n\n'.join(lines)}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboards.history()
    )

# ЗА ВСЕ ВРЕМЯ
@bot.callback_query_handler(func=lambda call: call.data == "history_all")
def show_history_all(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    rows = database.get_history(user_id)

    lines = []
    for row in rows:
        id, u_id, date, mood, work, sleep, comment, created_at = row
            
        shema = (
            f"📅 {date}\n"
            f"😊 Настроение: {mood} \n"
            f"💼 Работа: {float(work)} \n"
            f"😴 Сон: {float(sleep)} \n"
            f"💬 Комментарий: {comment + '\n' if comment else 'без комментария \n'}"
            f"🕐 Создано: {str(created_at)[11:19]}"
        )
        lines.append(shema)

    bot.edit_message_text(
        f"История за все время:\n\n{'\n\n'.join(lines)}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboards.history()
    )
###########################
# РОУТЫ ДЛЯ НАСТРОЕК
###########################

TIME_PATTERN = re.compile(r"^(0\d|1\d|2[0-3]):([0-5]\d)$")

# Назначение правильной клавиатуры
@bot.callback_query_handler(func=lambda call: call.data == "settings")
def settings(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    remind_time = database.get_remind_time(user_id)
    if remind_time is not None:
        time_str = remind_time[0].strftime("%H:%M")
        msg = bot.send_message(
            call.message.chat.id,
            f"Время напоминания установлено на: _{time_str}_",
            parse_mode="Markdown",
            reply_markup=keyboards.settings_A()
        )
    else:
        msg = bot.send_message(
            call.message.chat.id,
            "Время напоминания не установлено. Нажмите на кнопку ниже, чтобы установить.",
            reply_markup=keyboards.settings_B()
        )
    user_sessions[user_id] = {"step": None, "settings_msg_id": msg.message_id}

#######################################################
# перенправления роутов
@bot.callback_query_handler(func=lambda call: call.data == "add_reminder")
def add_reminder_port(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id] = {"step": "add_reminder", "settings_msg_id": call.message.message_id}
    bot.edit_message_text(
        "Введите время напоминания в формате HH:MM (например, 09:00):",
        call.message.chat.id,
        call.message.message_id
    )

# тоже перенаправление
@bot.callback_query_handler(func=lambda call: call.data == "edit_reminder")
def edit_reminder_port(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    user_sessions[user_id] = {"step": "edit_reminder", "settings_msg_id": call.message.message_id}
    bot.edit_message_text(
        "Введите новое время напоминания в формате HH:MM (например, 09:00):",
        call.message.chat.id,
        call.message.message_id
    )
#######################################################

#Установка напоминания
@bot.message_handler(func=lambda message: user_sessions.get(message.from_user.id, {}).get("step") == "add_reminder")
def add_reminder(message):
    user_id = message.from_user.id
    time = message.text.strip()
    msg_id = user_sessions[user_id].get("settings_msg_id")
    bot.delete_message(message.chat.id, message.message_id)

    if not TIME_PATTERN.match(time):
        bot.send_message(message.chat.id, "Неверный формат. Введите время в формате HH:MM (например, 09:00):")
        return
 
    database.set_remind_time(user_id, time)

    if msg_id:
        bot.edit_message_text(
            f"Время напоминания установлено на _{time}_.",
            message.chat.id,
            msg_id,
            parse_mode="Markdown",
            reply_markup=keyboards.settings_A()
        )
    del user_sessions[user_id]

#Изменение напоминания
@bot.message_handler(func=lambda message: user_sessions.get(message.from_user.id, {}).get("step") == "edit_reminder")
def edit_reminder(message):
    user_id = message.from_user.id
    new_time = message.text.strip()
    current_time = database.get_remind_time(user_id)
    current_str = current_time[0].strftime("%H:%M") if current_time and current_time[0] else "—"
    msg_id = user_sessions[user_id].get("settings_msg_id")
    bot.delete_message(message.chat.id, message.message_id)
 
    if not TIME_PATTERN.match(new_time):
        bot.send_message(message.chat.id, "Неверный формат. Введите время в формате HH:MM (например, 09:00):")
        return
 
    database.set_remind_time(user_id, new_time)
    
    if msg_id:
        bot.edit_message_text(
            f"Время напоминания изменено с _{current_str}_ на _{new_time}_.",
            message.chat.id,
            msg_id,
            parse_mode="Markdown",
            reply_markup=keyboards.settings_A()
        )
    del user_sessions[user_id]

#Удаление напоминания
@bot.callback_query_handler(func=lambda call: call.data == "delete_reminder")
def delete_reminder(call):
    bot.answer_callback_query(call.id)
    database.clear_remind_time(call.from_user.id)
    bot.edit_message_text(
        "Напоминание удалено.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboards.settings_B()
    )



start_scheduler(bot)
if __name__ == "__main__":
    print('Ботик запущен')
    bot.polling(none_stop=True)
