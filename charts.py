import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
from database import get_stats_graphic

def generate_stats_image(user_id: int, interval: int) -> BytesIO | None:
    rows = get_stats_graphic(user_id, interval)
    if not rows:
        return None

    dates = [row[0] for row in rows]
    moods = [row[1] for row in rows]
    work_hours = [row[2] for row in rows]
    sleep_hours = [row[3] for row in rows]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    
    ax.plot(dates, moods, marker='o', label='Настроение', color='#FF6B6B', linewidth=2)
    ax.plot(dates, work_hours, marker='s', label='Работа (ч)', color='#4ECDC4', linewidth=2)
    ax.plot(dates, sleep_hours, marker='^', label='Сон (ч)', color='#45B7D1', linewidth=2)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.set_xlabel('Дата')
    ax.set_ylabel('Значение')
    ax.set_title(f'Статистика за последние {interval} дней')
    ax.legend(loc='upper left', framealpha=0.8)
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    plt.close(fig)
    
    return buf