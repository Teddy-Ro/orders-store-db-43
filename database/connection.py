import psycopg2

def get_connection():
    """Возвращает объект подключения к PostgreSQL."""
    return psycopg2.connect(
        dbname="orders_store",
        user="admin",
        password="password",
        host="localhost",
        port="5432"
    )