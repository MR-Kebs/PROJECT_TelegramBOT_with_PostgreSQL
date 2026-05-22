import os
import psycopg2
from dotenv import load_dotenv
from datetime import date

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def test_connection():
    try:
        conn = get_connection()
        print("БД работает")
        conn.close()
    except Exception as e:
        print(f"иди чини бд {e}")



def add_entry(user_id, mood, work_hours, sleep_hours, comment):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO entries (user_id, mood, work_hours, sleep_hours, comment)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, mood, work_hours, sleep_hours, comment))

        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении записи: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def has_entry_today(user_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM entries WHERE user_id = %s AND entry_date = %s LIMIT 1",
                (user_id, date.today())
            )
            return cur.fetchone() is not None


def get_history(user_id, limit=None):
    if limit is not None and isinstance(limit, int) and limit > 0:
        limit_clause = f"LIMIT {limit}"
    else:
        limit_clause = ""
    
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"""
            SELECT * FROM entries 
            WHERE user_id = %s 
            ORDER BY entry_date DESC 
            {limit_clause}
        """, (user_id,))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print(f"Ошибка при чтении записи: {e}")
        return []
    finally:
        cursor.close()
        conn.close()



def get_stats_week(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT AVG(mood) AS moods, 
                   AVG(work_hours) AS work, 
                   AVG(sleep_hours) AS sleep 
            FROM entries 
            WHERE user_id = %s AND entry_date >= CURRENT_DATE - INTERVAL '7 days'
        """, (user_id,))
        rows = cursor.fetchone()
        return rows

    except Exception as e:
        print(f"Ошибка при чтении записи: {e}")
    finally:
        cursor.close()
        conn.close()



def get_stats_month(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT AVG(mood) AS moods, 
                   AVG(work_hours) AS work, 
                   AVG(sleep_hours) AS sleep 
            FROM entries 
            WHERE user_id = %s AND entry_date >= CURRENT_DATE - INTERVAL '30 days'
        """, (user_id,))
        rows = cursor.fetchone()
        return rows

    except Exception as e:
        print(f"Ошибка при чтении записи: {e}")
    finally:
        cursor.close()
        conn.close()



def get_insights(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            WITH data AS (
                SELECT 
                    AVG(mood) AS mood,
                    AVG(work_hours) AS work,
                    AVG(sleep_hours) AS sleep
                FROM entries WHERE user_id = %s
            )
            
            SELECT
                CASE
                    WHEN mood < 2 AND work > 5 AND sleep < 7 THEN 'Твоё настроение сильно упало, из-за большого количества работы и короткого сна. Тебе стоит почаще высыпаться и не перегружать себя'
                    WHEN mood < 2 AND work <= 5 AND sleep < 7 THEN 'Твоё настроение сильно упало, из-за короткого сна, попробуй почаще высыпаться'
                    WHEN mood < 2 AND work > 5 AND sleep > 7 THEN 'Твоё настроение сильно упало, из-за огромного количества работы, снизь дневную нагрузку'
                    WHEN mood < 2 AND work <= 5 AND sleep > 7 THEN 'Твоё настроение сильно упало, хотя ты высыпаешься и работаешь в меру. Думаю тебе стоит посоветоваться с кем-либо'
                    
                    WHEN mood BETWEEN 2 AND 3 AND work > 5 AND sleep < 7 THEN 'Среднее значение настроения обусловлена тем, что ты много работаешь и мало спишь, Тебе стоит почаще высыпаться и не перегружать себя'
                    WHEN mood BETWEEN 2 AND 3 AND work <= 5 AND sleep < 7 THEN 'Среднее значение настроения обусловлена тем, что ты мало спишь, попробуй почаще высыпаться'
                    WHEN mood BETWEEN 2 AND 3 AND work > 5 AND sleep > 7 THEN 'Среднее значение настроения обусловлена тем, что ты много работаешь, снизь дневную нагрузку'
                    WHEN mood BETWEEN 2 AND 3 AND work <= 5 AND sleep > 7 THEN 'Несмотря на то, что ты отлично спишь и работаешь в меру, твоё настроение не сильно увеличилось, может тебе стоит попробовать что-то новое, изучить что-нибудь' 
                    
                    
                    WHEN mood BETWEEN 4 AND 5 AND work > 5 AND sleep < 7 THEN 'Вижу ты прекрасно себя чувствуешь, даже не смотря на огромное количество работы и короткий сон'
                    WHEN mood BETWEEN 4 AND 5 AND work <= 5 AND sleep < 7 THEN 'Твоё настроение в идеале, короткий сон никак не повлиял на свою мотивацию'
                    WHEN mood BETWEEN 4 AND 5 AND work > 5 AND sleep > 7 THEN 'Вижу ты очень трудолюбивый раз работа приносит столько удовольствия тебе. Показатели по настроению суперские'
                    ELSE 'Оптимальный сон и работа в меру - лучшая атмосфера. Не удивительно, что твой уровень вайба отличный'
                END AS insight
            FROM data
        """, (user_id,))
        rows = cursor.fetchone()
        return rows

    except Exception as e:
        print(f"Ошибка при чтении записи: {e}")
    finally:
        cursor.close()
        conn.close()



def clear_entries(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM entries WHERE user_id = %s
        """, (user_id,))

        conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении записи: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        
        
        
def set_remind_time(user_id, time):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (user_id, remind_at)
            VALUES (%s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET remind_at = EXCLUDED.remind_at
        """, (user_id, time))

        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении записи: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_remind_time(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT remind_at FROM users
            WHERE user_id = %s
        """, (user_id,))
        rows = cursor.fetchone()
        return rows

    except Exception as e:
        print(f"Ошибка при чтении записи: {e}")
    finally:
        cursor.close()
        conn.close()
    
        
def clear_remind_time(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM users WHERE user_id = %s
        """, (user_id,))

        conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении записи: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        



def get_users_to_remind(current_time):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT user_id FROM users
            WHERE remind_at = %s
        """, (current_time,))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print(f"Ошибка при получении пользователей: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_stats_graphic(user_id, interval):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                   entry_date,
                   mood, 
                   work_hours, 
                   sleep_hours
            FROM entries 
            WHERE user_id = %s AND entry_date >= CURRENT_DATE - INTERVAL '%s days'
        """, (user_id, interval))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print(f"Ошибка при чтении записи: {e}")
    finally:
        cursor.close()
        conn.close()


test_connection()   