import random
from faker import Faker
from .connection import get_connection

# Указываем русскую локаль, чтобы данные выглядели как настоящие
fake = Faker('ru_RU')

def generate_fake_data():
    """Генерирует тестовые данные и заполняет все таблицы."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Очищаем старые данные (чтобы при повторном нажатии база не пухла)
        cur.execute("TRUNCATE TABLE OrderItems, Orders, Documents, Products, Employees, Customers, Suppliers RESTART IDENTITY CASCADE;")
        
        # 2. Генерируем Сотрудников (5 человек)
        print("Генерация сотрудников...")
        for _ in range(5):
            cur.execute("""
                INSERT INTO Employees (FullName, Position, Login, Password, AccessLevel)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                fake.name(), 
                random.choice(["Менеджер", "Старший менеджер", "Оператор"]),
                fake.unique.user_name(), 
                "password123", # Заглушка для пароля
                random.randint(1, 3)
            ))

        # 3. Генерируем Поставщиков (10 компаний)
        print("Генерация поставщиков...")
        for _ in range(10):
            cur.execute("""
                INSERT INTO Suppliers (CompanyName, ContactPerson, PhoneNumber, Details)
                VALUES (%s, %s, %s, %s)
            """, (fake.company(), fake.name(), fake.phone_number(), fake.catch_phrase()))

        # 4. Генерируем Клиентов (20 человек/компаний)
        print("Генерация клиентов...")
        for _ in range(20):
            cur.execute("""
                INSERT INTO Customers (FullName, CompanyName, PhoneNumber, Email, ShippingAddress)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                fake.name(), 
                fake.company() if random.choice([True, False]) else None, 
                fake.phone_number(), 
                fake.email(), 
                fake.address()
            ))

        # 5. Генерируем Товары (30 штук)
        print("Генерация товаров...")
        # Получаем ID поставщиков, чтобы привязать к ним товары
        cur.execute("SELECT SupplierID FROM Suppliers;")
        supplier_ids = [row[0] for row in cur.fetchall()]
        
        for _ in range(30):
            purchase_price = round(random.uniform(100.0, 5000.0), 2)
            sale_price = round(purchase_price * random.uniform(1.2, 2.0), 2) # Наценка 20-100%
            cur.execute("""
                INSERT INTO Products (Article, ProductName, Description, PurchasePrice, SalePrice, UnitOfMeasurement, ExpirationDate, StockBalance, SupplierID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                fake.unique.bothify(text='ART-#####'), # Уникальный артикул
                fake.word().capitalize(),
                fake.sentence(),
                purchase_price,
                sale_price,
                random.choice(["шт", "кг", "упак", "литр"]),
                fake.future_date(end_date="+1y") if random.choice([True, False]) else None,
                random.randint(0, 1000),
                random.choice(supplier_ids)
            ))

        # 6. Генерируем Заказы и их Состав (50 заказов)
        print("Генерация заказов...")
        cur.execute("SELECT CustomerID FROM Customers;")
        customer_ids = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT EmployeeID FROM Employees;")
        employee_ids = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT ProductID, SalePrice FROM Products;")
        products = cur.fetchall() # Список кортежей (ID, Цена)

        for _ in range(50):
            # Создаем пустой заказ
            cur.execute("""
                INSERT INTO Orders (OrderDate, Status, CustomerID, EmployeeID)
                VALUES (%s, %s, %s, %s) RETURNING OrderID;
            """, (
                fake.date_time_between(start_date="-1y", end_date="now"),
                random.choice(["Новый", "В обработке", "Отправлен", "Доставлен", "Отменен"]),
                random.choice(customer_ids),
                random.choice(employee_ids)
            ))
            order_id = cur.fetchone()[0]

            # Наполняем заказ товарами (от 1 до 5 разных товаров)
            order_total = 0
            items_count = random.randint(1, 5)
            selected_products = random.sample(products, items_count) # Берем уникальные товары для заказа
            
            for prod_id, price in selected_products:
                qty = random.randint(1, 10)
                order_total += price * qty
                cur.execute("""
                    INSERT INTO OrderItems (OrderID, ProductID, Quantity, PriceAtOrder)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, prod_id, qty, price))
            
            # Обновляем общую сумму заказа (TotalAmount)
            cur.execute("""
                UPDATE Orders SET TotalAmount = %s WHERE OrderID = %s
            """, (order_total, order_id))

        # Сохраняем все изменения в БД
        conn.commit()
        print("Генерация успешно завершена!")

    except Exception as e:
        conn.rollback() # Откат при ошибке
        raise e
    finally:
        cur.close()
        conn.close()