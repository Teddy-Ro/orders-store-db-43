import os
import random
import string
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
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("SELECT CustomerID, FullName, CompanyName, PhoneNumber, Email FROM Customers ORDER BY CustomerID;")
        return cur.fetchall()
    finally: 
        cur.close(); 
        conn.close()

def check_login(login, password):
    """Проверяет логин и пароль сотрудника. Возвращает данные или None."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT EmployeeID, FullName, AccessLevel, Position 
            FROM Employees 
            WHERE Login = %s AND Password = %s;
        """, (login, password))
        return cur.fetchone() # Вернет кортеж с данными или None
    finally:
        cur.close()
        conn.close()

def add_customer(full_name, company, phone, email):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Customers (FullName, CompanyName, PhoneNumber, Email) VALUES (%s, %s, %s, %s)", 
                    (full_name, company, phone, email))
        conn.commit()
    except Exception as e: 
        conn.rollback(); raise e
    finally: 
        cur.close(); 
        conn.close()

def delete_customer(customer_id):
    """Удаляет клиента по ID."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Customers WHERE CustomerID = %s", (customer_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def update_customer(customer_id, full_name, company, phone, email):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("UPDATE Customers SET FullName=%s, CompanyName=%s, PhoneNumber=%s, Email=%s WHERE CustomerID=%s", 
                    (full_name, company, phone, email, customer_id))
        conn.commit()
    except Exception as e: 
        conn.rollback(); raise e
    finally: 
        cur.close(); 
        conn.close()

def get_all_suppliers():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT SupplierID, CompanyName, ContactPerson, PhoneNumber, Details FROM Suppliers ORDER BY SupplierID;")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def add_supplier(company, contact, phone, details):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Suppliers (CompanyName, ContactPerson, PhoneNumber, Details) 
            VALUES (%s, %s, %s, %s)
        """, (company, contact, phone, details))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def update_supplier(supplier_id, company, contact, phone, details):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE Suppliers 
            SET CompanyName = %s, ContactPerson = %s, PhoneNumber = %s, Details = %s 
            WHERE SupplierID = %s
        """, (company, contact, phone, details, supplier_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def delete_supplier(supplier_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Suppliers WHERE SupplierID = %s", (supplier_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# ================= СОТРУДНИКИ =================
def get_all_employees():
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("SELECT EmployeeID, FullName, Position, Login, Password, AccessLevel FROM Employees ORDER BY EmployeeID;")
        return cur.fetchall()
    finally: cur.close(); conn.close()

def add_employee(name, pos, log, pwd, lvl):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Employees (FullName, Position, Login, Password, AccessLevel) VALUES (%s, %s, %s, %s, %s)", (name, pos, log, pwd, lvl))
        conn.commit()
    except Exception as e: conn.rollback(); raise e
    finally: cur.close(); conn.close()

def update_employee(emp_id, name, pos, log, pwd, lvl):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("UPDATE Employees SET FullName=%s, Position=%s, Login=%s, Password=%s, AccessLevel=%s WHERE EmployeeID=%s", (name, pos, log, pwd, lvl, emp_id))
        conn.commit()
    except Exception as e: conn.rollback(); raise e
    finally: cur.close(); conn.close()

def delete_employee(emp_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Employees WHERE EmployeeID = %s", (emp_id,))
        conn.commit()
    except Exception as e: conn.rollback(); raise e
    finally: cur.close(); conn.close()

# ================= ТОВАРЫ =================
def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Запрос строго по твоей схеме: убрали category
        cur.execute("""
            SELECT productid, article, productname, purchaseprice, saleprice, stockbalance, 
                   unit, description, supplierid 
            FROM products ORDER BY productid;
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def add_product(art, name, p_price, s_price, stock, unit, supplier_id, description):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if not art or art.strip() == "":
            art = generate_unique_article()
            
        cur.execute("""
            INSERT INTO products (article, productname, purchaseprice, saleprice, stockbalance, unit, supplierid, description) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (art, name, p_price, s_price, stock, unit, supplier_id, description))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def update_product(prod_id, art, name, p_price, s_price, stock, unit, supplier_id, description):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if not art or art.strip() == "":
            art = generate_unique_article()
            
        cur.execute("""
            UPDATE products 
            SET article=%s, productname=%s, purchaseprice=%s, saleprice=%s, stockbalance=%s, 
                unit=%s, supplierid=%s, description=%s 
            WHERE productid=%s;
        """, (art, name, p_price, s_price, stock, unit, supplier_id, description, prod_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def delete_product(prod_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Products WHERE ProductID = %s", (prod_id,))
        conn.commit()
    except Exception as e: conn.rollback(); raise e
    finally: cur.close(); conn.close()

def get_customers_for_search():
    """Получает клиентов для умного поиска (ID, Имя, Телефон, Email)"""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("SELECT CustomerID, FullName, PhoneNumber, Email FROM Customers;")
        return cur.fetchall()
    finally: cur.close(); conn.close()

def get_products_for_search():
    """Получает товары для умного поиска и контроля остатков"""
    conn = get_connection(); cur = conn.cursor()
    try:
        # Вытаскиваем ID, Артикул, Название, Цену продажи, Остаток и Единицу измерения
        cur.execute("SELECT ProductID, Article, ProductName, SalePrice, StockBalance, Unit FROM Products WHERE StockBalance > 0;")
        return cur.fetchall()
    finally: cur.close(); conn.close()

def create_order_transaction(customer_id, seller_id, address, cart_items):
    conn = get_connection(); cur = conn.cursor()
    try:
        # ЗАМЕНИЛИ CURRENT_DATE на CURRENT_TIMESTAMP
        cur.execute("""
            INSERT INTO Orders (CustomerID, EmployeeID, OrderDate, Status, ShippingAddress) 
            VALUES (%s, %s, CURRENT_TIMESTAMP, 'Новый', %s) RETURNING OrderID;
        """, (customer_id, seller_id, address))
        order_id = cur.fetchone()[0]

        for item in cart_items:
            cur.execute("""
                INSERT INTO OrderItems (OrderID, ProductID, Quantity, PriceAtOrder) 
                VALUES (%s, %s, %s, %s);
            """, (order_id, item['product_id'], item['qty'], item['price']))
            
            cur.execute("UPDATE Products SET StockBalance = StockBalance - %s WHERE ProductID = %s;", 
                        (item['qty'], item['product_id']))

        conn.commit()
        return order_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close(); conn.close()

# ================= ЖУРНАЛ ЗАКАЗОВ =================
def get_all_orders():
    conn = get_connection(); cur = conn.cursor()
    try:
        # ТУТ ИСПРАВИЛИ oi.Price на oi.PriceAtOrder
        cur.execute("""
            SELECT o.OrderID, o.OrderDate, o.Status,
                   c.FullName AS Customer,
                   e.FullName AS Seller,
                   COALESCE(ce.FullName, 'Не назначен') AS Courier,
                   COALESCE(SUM(oi.Quantity * oi.PriceAtOrder), 0) AS TotalSum
            FROM Orders o
            LEFT JOIN Customers c ON o.CustomerID = c.CustomerID
            LEFT JOIN Employees e ON o.EmployeeID = e.EmployeeID
            LEFT JOIN Employees ce ON o.CourierID = ce.EmployeeID
            LEFT JOIN OrderItems oi ON o.OrderID = oi.OrderID
            GROUP BY o.OrderID, c.FullName, e.FullName, ce.FullName
            ORDER BY o.OrderID DESC;
        """)
        return cur.fetchall()
    finally: cur.close(); conn.close()

def get_order_details(order_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.Article, p.ProductName, oi.PriceAtOrder, oi.Quantity, (oi.PriceAtOrder * oi.Quantity) AS Summa
            FROM OrderItems oi
            JOIN Products p ON oi.ProductID = p.ProductID
            WHERE oi.OrderID = %s;
        """, (order_id,))
        return cur.fetchall()
    finally: cur.close(); conn.close()

def update_order_status(order_id, new_status):
    """Обновляет статус заказа. Если заказ отменен - возвращает товары на склад."""
    conn = get_connection(); cur = conn.cursor()
    try:
        # Проверяем текущий статус, чтобы не вернуть товары дважды
        cur.execute("SELECT Status FROM Orders WHERE OrderID = %s", (order_id,))
        current_status = cur.fetchone()[0]

        if new_status == 'Отменен' and current_status != 'Отменен':
            # Фишка для курсовой: Транзакция возврата остатков
            cur.execute("SELECT ProductID, Quantity FROM OrderItems WHERE OrderID = %s", (order_id,))
            for p_id, qty in cur.fetchall():
                cur.execute("UPDATE Products SET StockBalance = StockBalance + %s WHERE ProductID = %s", (qty, p_id))

        cur.execute("UPDATE Orders SET Status = %s WHERE OrderID = %s", (new_status, order_id))
        conn.commit()
    except Exception as e: 
        conn.rollback(); raise e
    finally: cur.close(); conn.close()

def get_suppliers_for_dropdown():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT supplierid, companyname FROM suppliers ORDER BY companyname;")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def generate_unique_article():
    conn = get_connection()
    cur = conn.cursor()
    try:
        while True:
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            article = f"PRD-{suffix}"
            cur.execute("SELECT 1 FROM products WHERE article = %s;", (article,))
            if not cur.fetchone():
                return article
    finally:
        cur.close()
        conn.close()