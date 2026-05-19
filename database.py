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

test_connection()