import psycopg2

def get_connection():
    """Возвращает объект подключения к PostgreSQL."""
    return psycopg2.connect(
        dbname="orders_store",
        user="admin",
        password="password",
        host="127.0.0.1",
        port="5435"
    )