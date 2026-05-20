from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
from database import get_users_to_remind

scheduler = BackgroundScheduler()

active = False

def send_reminders(bot):
    if active == False:
        return
    current_time = datetime.now().strftime("%H:%M")
    fix_time = time()
    users = get_users_to_remind(current_time)
    for user in users:
        if current_time 
            bot.send_message(user[0], "Самое время отметиться!")


def start_scheduler(bot):
    if active == False:
        return
    scheduler.add_job(send_reminders, 'interval', minutes = 1, args=[bot])
    scheduler.start()