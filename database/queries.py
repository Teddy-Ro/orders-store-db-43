import os
from .connection import get_connection

def init_database():
    """Читает SQL-файл и создает таблицы в базе данных."""
    # Получаем абсолютный путь к файлу SQL, чтобы скрипт работал из любой папки
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_file_path = os.path.join(base_dir, 'sql', 'create_tables.sql')

    with open(sql_file_path, 'r', encoding='utf-8') as file:
        sql_script = file.read()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql_script)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_all_customers():
    """Возвращает всех клиентов из базы."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT CustomerID, FullName, CompanyName, PhoneNumber FROM Customers ORDER BY CustomerID;")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()