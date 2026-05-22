from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
from database import get_users_to_remind

scheduler = BackgroundScheduler()

active = True

def send_reminders(bot):
    current_time = datetime.now().strftime("%H:%M")
    ct = datetime.now().time()
    start_vibe = time(4, 00)
    start_atmosphere = time(16, 00)
    users = get_users_to_remind(current_time)
    for user in users:
        if start_vibe <= ct < start_atmosphere:
            bot.send_message(user[0], "Самое время отметить свой вайбик!")
        else:
            bot.send_message(user[0], "Самое время отметить свою атмосферу!")
    active = True


def start_scheduler(bot):
    scheduler.add_job(send_reminders, 'interval', minutes = 1, args=[bot])
    scheduler.start()