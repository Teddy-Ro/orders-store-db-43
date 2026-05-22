-- Очистка базы перед созданием (удобно для разработки)
DROP TABLE IF EXISTS OrderItems CASCADE;
DROP TABLE IF EXISTS Documents CASCADE;
DROP TABLE IF EXISTS Orders CASCADE;
DROP TABLE IF EXISTS Products CASCADE;
DROP TABLE IF EXISTS Suppliers CASCADE;
DROP TABLE IF EXISTS Customers CASCADE;
DROP TABLE IF EXISTS Employees CASCADE;

-- 1. Независимые таблицы (Справочники)
CREATE TABLE Suppliers (
    SupplierID SERIAL PRIMARY KEY,
    CompanyName VARCHAR(255) NOT NULL,
    ContactPerson VARCHAR(255),
    PhoneNumber VARCHAR(50),
    Details TEXT
);

CREATE TABLE Customers (
    CustomerID SERIAL PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    CompanyName VARCHAR(255),
    PhoneNumber VARCHAR(50),
    Email VARCHAR(255)
    -- Поле ShippingAddress убрано отсюда согласно схеме
);

CREATE TABLE Employees (
    EmployeeID SERIAL PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    Position VARCHAR(100),
    Login VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    AccessLevel INT DEFAULT 1
);

-- 2. Таблицы 1-го уровня зависимости
CREATE TABLE Products (
    ProductID SERIAL PRIMARY KEY,
    Article VARCHAR(100) UNIQUE NOT NULL,
    ProductName VARCHAR(255) NOT NULL,
    Description TEXT,
    PurchasePrice DECIMAL(12, 2) NOT NULL,
    SalePrice DECIMAL(12, 2) NOT NULL,
    UnitOfMeasurement VARCHAR(50),
    ExpirationDate DATE,
    StockBalance INT DEFAULT 0,
    SupplierID INT REFERENCES Suppliers(SupplierID) ON DELETE SET NULL,
    Unit VARCHAR(20) -- Добавлено согласно схеме
);

-- Таблицы 2-го уровня зависимости (Заказы)
CREATE TABLE Orders (
    OrderID SERIAL PRIMARY KEY,
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(50) DEFAULT 'Новый',
    TotalAmount DECIMAL(12, 2) DEFAULT 0.00,
    CustomerID INT REFERENCES Customers(CustomerID) ON DELETE CASCADE,
    EmployeeID INT REFERENCES Employees(EmployeeID) ON DELETE SET NULL,
    ShippingAddress VARCHAR(255), -- Перенесено из Customers согласно схеме
    CourierID INT REFERENCES Employees(EmployeeID) ON DELETE SET NULL -- Добавлено согласно схеме
);

-- 3. Таблицы 3-го уровня зависимости (Документы и Состав заказа)
CREATE TABLE Documents (
    DocumentID SERIAL PRIMARY KEY,
    DocumentType VARCHAR(100) NOT NULL,
    DocumentNumber VARCHAR(100) UNIQUE NOT NULL,
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    OrderID INT REFERENCES Orders(OrderID) ON DELETE SET NULL, -- Теперь ссылается на Orders (перенесено на 3-й уровень)
    SupplierID INT REFERENCES Suppliers(SupplierID) ON DELETE CASCADE
);

CREATE TABLE OrderItems (
    OrderID INT REFERENCES Orders(OrderID) ON DELETE CASCADE,
    ProductID INT REFERENCES Products(ProductID) ON DELETE RESTRICT,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    PriceAtOrder DECIMAL(12, 2) NOT NULL,
    PRIMARY KEY (OrderID, ProductID) -- Составной первичный ключ
);