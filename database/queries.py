import os
import random
import string
from .connection import get_connection

# =====================================================================
# ИНИЦИАЛИЗАЦИЯ И СЛУЖЕБНЫЕ ФУНКЦИИ
# =====================================================================

def init_database():
    """Читает SQL-файл и создает таблицы в базе данных."""
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

# =====================================================================
# КЛИЕНТЫ (CUSTOMERS)
# =====================================================================

def get_all_customers():
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("SELECT CustomerID, FullName, CompanyName, PhoneNumber, Email FROM Customers ORDER BY CustomerID;")
        return cur.fetchall()
    finally: 
        cur.close(); 
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

def get_customers_for_search():
    """Получает клиентов для умного поиска (ID, Имя, Телефон, Email)"""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("SELECT CustomerID, FullName, PhoneNumber, Email FROM Customers;")
        return cur.fetchall()
    finally: cur.close(); conn.close()

# =====================================================================
# ПОСТАВЩИКИ (SUPPLIERS)
# =====================================================================

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

def get_suppliers_for_dropdown():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT supplierid, companyname FROM suppliers ORDER BY companyname;")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# =====================================================================
# СОТРУДНИКИ (EMPLOYEES)
# =====================================================================

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
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

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

# =====================================================================
# ТОВАРЫ (PRODUCTS)
# =====================================================================

def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    try:
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

def get_products_for_search():
    """Получает товары для умного поиска и контроля остатков"""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("SELECT ProductID, Article, ProductName, SalePrice, StockBalance, Unit FROM Products WHERE StockBalance > 0;")
        return cur.fetchall()
    finally: cur.close(); conn.close()

# =====================================================================
# ЗАКАЗЫ (ORDERS)
# =====================================================================

def create_order_transaction(customer_id, seller_id, address, cart_items):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Проверяем остатки с жесткой блокировкой строк (FOR UPDATE)
        for item in cart_items:
            cur.execute("SELECT StockBalance, ProductName FROM Products WHERE ProductID = %s FOR UPDATE;", (item['product_id'],))
            res = cur.fetchone()
            if not res:
                raise ValueError(f"Товар с ID {item['product_id']} не найден.")
            
            current_stock, prod_name = res
            
            # Если пока мы собирали корзину товар кто-то купил:
            if current_stock < item['qty']:
                raise ValueError(f"Товара '{prod_name}' недостаточно на складе!\nВ наличии: {current_stock}, требуется: {item['qty']}")
                
            # Списываем остаток
            cur.execute("UPDATE Products SET StockBalance = StockBalance - %s WHERE ProductID = %s;", 
                        (item['qty'], item['product_id']))

        # 2. Создаем сам заказ
        cur.execute("""
            INSERT INTO Orders (CustomerID, EmployeeID, OrderDate, Status, ShippingAddress) 
            VALUES (%s, %s, CURRENT_TIMESTAMP, 'Новый', %s) RETURNING OrderID;
        """, (customer_id, seller_id, address))
        order_id = cur.fetchone()[0]

        # 3. Сохраняем состав
        for item in cart_items:
            cur.execute("""
                INSERT INTO OrderItems (OrderID, ProductID, Quantity, PriceAtOrder) 
                VALUES (%s, %s, %s, %s);
            """, (order_id, item['product_id'], item['qty'], item['price']))
        
        conn.commit()
        return order_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_all_orders():
    conn = get_connection(); cur = conn.cursor()
    try:
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
        cur.execute("SELECT Status FROM Orders WHERE OrderID = %s", (order_id,))
        current_status = cur.fetchone()[0]

        if new_status == 'Отменен' and current_status != 'Отменен':
            cur.execute("SELECT ProductID, Quantity FROM OrderItems WHERE OrderID = %s", (order_id,))
            for p_id, qty in cur.fetchall():
                cur.execute("UPDATE Products SET StockBalance = StockBalance + %s WHERE ProductID = %s", (qty, p_id))

        cur.execute("UPDATE Orders SET Status = %s WHERE OrderID = %s", (new_status, order_id))
        conn.commit()
    except Exception as e: 
        conn.rollback(); raise e
    finally: cur.close(); conn.close()

# =====================================================================
# БЛОК КУРЬЕРА (COURIERS)
# =====================================================================

def get_available_orders():
    """Возвращает все оплаченные заказы, у которых еще нет курьера"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT o.orderid, o.orderdate, c.fullname, o.shippingaddress
            FROM orders o
            JOIN customers c ON o.customerid = c.customerid
            WHERE o.status = 'Оплачен' AND o.courierid IS NULL
            ORDER BY o.orderid;
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_active_courier_order(courier_id):
    """Возвращает текущий активный заказ курьера (статус 'В доставке')"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT o.orderid, o.orderdate, c.fullname, c.phonenumber, o.shippingaddress
            FROM orders o
            JOIN customers c ON o.customerid = c.customerid
            WHERE o.status = 'В доставке' AND o.courierid = %s
            LIMIT 1;
        """, (courier_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def get_order_items_details(order_id):
    """Возвращает состав товаров для конкретного заказа: Артикул, ID, Название, Количество"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.article, p.productid, p.productname, oi.quantity
            FROM orderitems oi
            JOIN products p ON oi.productid = p.productid
            WHERE oi.orderid = %s
            ORDER BY p.productid;
        """, (order_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def accept_order(order_id, courier_id):
    """Привязать заказ к курьеру и перевести в статус 'В доставке'"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE orders 
            SET status = 'В доставке', courierid = %s 
            WHERE orderid = %s AND status = 'Оплачен' AND courierid IS NULL;
        """, (courier_id, order_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def complete_order(order_id):
    """Перевести заказ в статус 'Доставлен'"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE orders 
            SET status = 'Доставлен' 
            WHERE orderid = %s AND status = 'В доставке';
        """, (order_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# =====================================================================
# АНАЛИТИКА И ОТЧЕТЫ (ANALYTICS)
# =====================================================================

def get_analytics_kpis(start_date, end_date):
    """Считает расширенный список KPI: Выручку, Прибыль, Процент выполнения, Средний чек и Число заказов."""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COALESCE(SUM(totalamount), 0) FROM orders 
            WHERE status IN ('Оплачен', 'В доставке', 'Доставлен') 
              AND orderdate::date BETWEEN %s AND %s;
        """, (start_date, end_date))
        revenue = float(cur.fetchone()[0])

        cur.execute("""
            SELECT COALESCE(SUM((oi.priceatorder - p.purchaseprice) * oi.quantity), 0)
            FROM orderitems oi
            JOIN products p ON oi.productid = p.productid
            JOIN orders o ON oi.orderid = o.orderid
            WHERE o.status IN ('Оплачен', 'В доставке', 'Доставлен')
              AND o.orderdate::date BETWEEN %s AND %s;
        """, (start_date, end_date))
        profit = float(cur.fetchone()[0])

        cur.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'Доставлен' THEN 1 END)::float / 
                NULLIF(COUNT(CASE WHEN status IN ('Доставлен', 'Отменен') THEN 1 END), 0) * 100
            FROM orders WHERE orderdate::date BETWEEN %s AND %s;
        """, (start_date, end_date))
        res = cur.fetchone()[0]
        rate = round(res, 1) if res is not None else 0.0

        cur.execute("""
            SELECT COALESCE(AVG(totalamount), 0) FROM orders 
            WHERE status IN ('Оплачен', 'В доставке', 'Доставлен') 
              AND orderdate::date BETWEEN %s AND %s;
        """, (start_date, end_date))
        avg_check = float(cur.fetchone()[0])

        cur.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE orderdate::date BETWEEN %s AND %s;
        """, (start_date, end_date))
        total_orders = int(cur.fetchone()[0])

        return revenue, profit, rate, avg_check, total_orders
    finally: 
        cur.close(); conn.close()

def get_top_products(start_date, end_date):
    """Возвращает Топ-5 продаваемых товаров за период."""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.article, p.productname, SUM(oi.quantity), SUM(oi.quantity * oi.priceatorder) as total
            FROM orderitems oi
            JOIN products p ON oi.productid = p.productid
            JOIN orders o ON oi.orderid = o.orderid
            WHERE o.status IN ('Оплачен', 'В доставке', 'Доставлен')
              AND o.orderdate::date BETWEEN %s AND %s
            GROUP BY p.productid, p.article, p.productname
            ORDER BY total DESC LIMIT 5;
        """, (start_date, end_date))
        return cur.fetchall()
    finally: cur.close(); conn.close()

def get_sales_trend(start_date, end_date):
    """Возвращает посуточную выручку и чистую прибыль для комплексных графиков."""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT o.orderdate::date as day, 
                   COALESCE(SUM(o.totalamount), 0) as daily_revenue,
                   COALESCE(SUM((oi.priceatorder - p.purchaseprice) * oi.quantity), 0) as daily_profit
            FROM orders o
            LEFT JOIN orderitems oi ON o.orderid = oi.orderid
            LEFT JOIN products p ON oi.productid = p.productid
            WHERE o.status IN ('Оплачен', 'В доставке', 'Доставлен')
              AND o.orderdate::date BETWEEN %s AND %s
            GROUP BY day ORDER BY day;
        """, (start_date, end_date))
        return cur.fetchall()
    finally: cur.close(); conn.close()

def get_order_status_distribution(start_date, end_date):
    """Возвращает количество заказов по каждому статусу за указанный период."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM orders 
            WHERE orderdate::date BETWEEN %s AND %s
            GROUP BY status;
        """, (start_date, end_date))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_top_sellers_rating(start_date, end_date):
    """Возвращает топ продавцов (сотрудников) по объему выручки за период."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT e.fullname, COALESCE(SUM(o.totalamount), 0) as total_sales
            FROM orders o
            JOIN employees e ON o.employeeid = e.employeeid
            WHERE o.status IN ('Оплачен', 'В доставке', 'Доставлен')
              AND o.orderdate::date BETWEEN %s AND %s
            GROUP BY e.employeeid, e.fullname
            ORDER BY total_sales ASC LIMIT 5; 
        """, (start_date, end_date))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()