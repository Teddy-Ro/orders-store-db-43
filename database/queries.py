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
    """Возвращает всех клиентов (теперь с email и адресом)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT CustomerID, FullName, CompanyName, PhoneNumber, Email, ShippingAddress 
            FROM Customers ORDER BY CustomerID;
        """)
        return cur.fetchall()
    finally:
        cur.close()
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

def add_customer(full_name, company, phone, email, address):
    """Добавляет нового клиента в базу данных."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Customers (FullName, CompanyName, PhoneNumber, Email, ShippingAddress)
            VALUES (%s, %s, %s, %s, %s)
        """, (full_name, company, phone, email, address))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
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

def update_customer(customer_id, full_name, company, phone, email, address):
    """Обновляет данные существующего клиента."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE Customers 
            SET FullName = %s, CompanyName = %s, PhoneNumber = %s, Email = %s, ShippingAddress = %s
            WHERE CustomerID = %s
        """, (full_name, company, phone, email, address, customer_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
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
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("SELECT ProductID, Article, ProductName, PurchasePrice, SalePrice, StockBalance, SupplierID FROM Products ORDER BY ProductID;")
        return cur.fetchall()
    finally: cur.close(); conn.close()

def add_product(art, name, p_price, s_price, stock, sup_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Products (Article, ProductName, PurchasePrice, SalePrice, StockBalance, SupplierID) VALUES (%s, %s, %s, %s, %s, %s)", (art, name, p_price, s_price, stock, sup_id))
        conn.commit()
    except Exception as e: conn.rollback(); raise e
    finally: cur.close(); conn.close()

def update_product(prod_id, art, name, p_price, s_price, stock, sup_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("UPDATE Products SET Article=%s, ProductName=%s, PurchasePrice=%s, SalePrice=%s, StockBalance=%s, SupplierID=%s WHERE ProductID=%s", (art, name, p_price, s_price, stock, sup_id, prod_id))
        conn.commit()
    except Exception as e: conn.rollback(); raise e
    finally: cur.close(); conn.close()

def delete_product(prod_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Products WHERE ProductID = %s", (prod_id,))
        conn.commit()
    except Exception as e: conn.rollback(); raise e
    finally: cur.close(); conn.close()