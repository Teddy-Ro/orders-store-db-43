from database.connection import get_connection

def init():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Читаем и выполняем твой файл с SQL-запросами
        with open('sql/create_tables.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
            cur.execute(sql_script)
            
        conn.commit()
        conn.close()
        print("Успех! Каркас таблиц успешно создан в базе данных.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    init()