import os
import psycopg2
from dotenv import load_dotenv

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




def get_history(user_id, limit=7):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM entries WHERE user_id = %s ORDER BY entry_date DESC LIMIT %s
        """, (user_id, limit))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print(f"Ошибка при чтении записи: {e}")
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
                    ELSE 'Оптимальный сон и работа в меру - супер. Не удивительно, что твой уровень счастья отличный'
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


test_connection()