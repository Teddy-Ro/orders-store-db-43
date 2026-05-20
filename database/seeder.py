import random
import math
from datetime import datetime, timedelta
from faker import Faker
from .connection import get_connection

fake = Faker('ru_RU')

def generate_fake_data(num_customers=30, num_suppliers=10, num_products=40, days_of_history=120):
    """Генерирует тестовые данные строго по физической ER-схеме PostgreSQL."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Очистка таблиц каскадом 
        cur.execute("TRUNCATE TABLE orderitems, orders, documents, products, employees, customers, suppliers RESTART IDENTITY CASCADE;")
        
        # 2. Сотрудники (Админ, Продавцы, Курьеры)
        cur.execute("INSERT INTO employees (fullname, position, login, password, accesslevel) VALUES ('Иванов А.Д.', 'Управляющий', 'admin', 'admin', 1);")
        
        seller_ids = []
        for _ in range(3):
            cur.execute("INSERT INTO employees (fullname, position, login, password, accesslevel) VALUES (%s, 'Продавец', %s, '123', 2) RETURNING employeeid;",
                        (fake.name(), fake.unique.user_name()))
            seller_ids.append(cur.fetchone()[0])
            
        courier_ids = []
        for _ in range(3):
            cur.execute("INSERT INTO employees (fullname, position, login, password, accesslevel) VALUES (%s, 'Курьер', %s, '123', 3) RETURNING employeeid;",
                        (fake.name(), fake.unique.user_name()))
            courier_ids.append(cur.fetchone()[0])

        # 3. Поставщики
        supplier_ids = []
        for _ in range(max(2, num_suppliers)):
            cur.execute("INSERT INTO suppliers (companyname, contactperson, phonenumber, details) VALUES (%s, %s, %s, %s) RETURNING supplierid;",
                        (fake.company(), fake.name(), fake.phone_number(), fake.catch_phrase()))
            supplier_ids.append(cur.fetchone()[0])

        # 4. ИСПРАВЛЕНО: Клиенты создаются СТРОГО по схеме (без shippingaddress!)
        customer_ids = []
        for _ in range(max(5, num_customers)):
            cur.execute("INSERT INTO customers (fullname, companyname, phonenumber, email) VALUES (%s, %s, %s, %s) RETURNING customerid;",
                        (fake.name(), fake.company() if random.choice([True, False]) else None, fake.phone_number(), fake.email()))
            customer_ids.append(cur.fetchone()[0])

        # 5. Товары (Используем колонку unitofmeasurement из create_tables.sql)
        product_pool = []
        for i in range(max(5, num_products)):
            p_price = round(random.uniform(100.0, 3500.0), 2)
            s_price = round(p_price * random.uniform(1.2, 1.7), 2)
            
            cur.execute("""
                INSERT INTO products (article, productname, description, purchaseprice, saleprice, unitofmeasurement, stockbalance, supplierid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING productid;
            """, (
                f"ART-{random.randint(10000, 99999)}",
                fake.word().capitalize() + " " + random.choice(["Органик", "Импорт", "Люкс", "Классик"]),
                fake.sentence(), p_price, s_price, random.choice(["шт", "кг", "упак", "литр"]),
                random.randint(30, 300), random.choice(supplier_ids)
            ))
            prod_id = cur.fetchone()[0]
            
            # Закон Парето для реализма аналитики
            weight = 120 if i < 4 else random.randint(2, 12)
            product_pool.append((prod_id, s_price, weight))

        # 6. Заказы (Адрес доставки пишется СЮДА)
        start_date = datetime.now() - timedelta(days=days_of_history)
        prod_ids_list = [p[0] for p in product_pool]
        prod_prices_dict = {p[0]: p[1] for p in product_pool}
        prod_weights = [p[2] for p in product_pool]

        for day_offset in range(days_of_history):
            current_date = start_date + timedelta(days=day_offset)
            base_orders = random.randint(1, 2)
            trend_bonus = math.floor(day_offset / 30) 
            
            for _ in range(base_orders + trend_bonus):
                days_ago = (datetime.now() - current_date).days
                if days_ago > 3:
                    status = "Отменен" if random.random() < 0.12 else "Доставлен"
                else:
                    status = random.choice(["Новый", "Оплачен", "В доставке", "Доставлен"])

                courier_id = random.choice(courier_ids) if status in ["В доставке", "Доставлен"] else None

                cur.execute("""
                    INSERT INTO orders (orderdate, status, totalamount, customerid, employeeid, shippingaddress, courierid)
                    VALUES (%s, %s, 0.00, %s, %s, %s, %s) RETURNING orderid;
                """, (
                    current_date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59)),
                    status, random.choice(customer_ids), random.choice(seller_ids), fake.address(), courier_id
                ))
                order_id = cur.fetchone()[0]

                order_total = 0
                items_count = random.randint(1, 4)
                chosen_products = list(set(random.choices(prod_ids_list, weights=prod_weights, k=items_count)))

                for p_id in chosen_products:
                    qty = random.randint(1, 3)
                    price = prod_prices_dict[p_id]
                    order_total += price * qty
                    
                    cur.execute("""
                        INSERT INTO orderitems (orderid, productid, quantity, priceatorder)
                        VALUES (%s, %s, %s, %s);
                    """, (order_id, p_id, qty, price))

                cur.execute("UPDATE orders SET totalamount = %s WHERE orderid = %s;", (order_total, order_id))

        conn.commit()
        print("Параметризованный сидинг успешно выполнен.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def clear_database_completely():
    """Полностью удаляет все данные из БД, оставляя только одну дефолтную учетную запись админа."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Очищаем все таблицы каскадом с перезапуском автоинкрементных счетчиков (IDENTITY)
        cur.execute("TRUNCATE TABLE orderitems, orders, documents, products, employees, customers, suppliers RESTART IDENTITY CASCADE;")
        
        # Сразу создаем базового администратора, чтобы сессия авторизации не ломалась
        cur.execute("""
            INSERT INTO employees (fullname, position, login, password, accesslevel) 
            VALUES ('Иванов А.Д.', 'Управляющий', 'admin', 'admin', 1);
        """)
        conn.commit()
        print("База данных успешно полностью очищена!")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()