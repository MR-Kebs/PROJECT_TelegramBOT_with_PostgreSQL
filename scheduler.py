from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from database import get_remind_time

scheduler = BackgroundScheduler()

def send_reminders(bot):
    current_time = datetime.now().strftime("%H:%M")
    users = get_remind_time(current_time)
    for user in users:
        bot.send_message(user, "Самое время отметиться!")


def start_scheduler(bot):
    scheduler.add_job(send_reminders, 'interval', minutes = 1, args=[bot])
    scheduler.start()