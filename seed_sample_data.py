"""
Create demo tables + sample rows in the database from .env (DB_NAME).
Safe to re-run: drops and recreates only these tables.
"""
from __future__ import annotations

import mysql.connector

from db import get_connection

TABLES_IN_DROP_ORDER = (
    "reviews",
    "order_items",
    "orders",
    "products",
    "employees",
    "customers",
    "categories",
)


def main() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    for t in TABLES_IN_DROP_ORDER:
        cur.execute(f"DROP TABLE IF EXISTS `{t}`")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")

    cur.execute(
        """
        CREATE TABLE categories (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE customers (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(200) NOT NULL,
            email VARCHAR(200),
            created_at DATE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE products (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(200) NOT NULL,
            category_id INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE orders (
            id INT PRIMARY KEY AUTO_INCREMENT,
            customer_id INT NOT NULL,
            order_date DATE NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE order_items (
            id INT PRIMARY KEY AUTO_INCREMENT,
            order_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE employees (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(200) NOT NULL,
            hire_date DATE NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cur.execute(
        """
        CREATE TABLE reviews (
            id INT PRIMARY KEY AUTO_INCREMENT,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            rating DECIMAL(2, 1) NOT NULL,
            review_date DATE,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    cur.executemany(
        "INSERT INTO categories (name) VALUES (%s)",
        [
            ("Electronics",),
            ("Home",),
            ("Sports",),
        ],
    )
    cur.executemany(
        "INSERT INTO customers (name, email, created_at) VALUES (%s, %s, %s)",
        [
            ("Alice Ng", "alice@example.com", "2023-05-01"),
            ("Ben Ortiz", "ben@example.com", "2023-08-12"),
            ("Chloe Park", "chloe@example.com", "2024-01-03"),
            ("Diego Ruiz", "diego@example.com", "2024-02-18"),
            ("Eva Khan", "eva@example.com", "2024-06-20"),
            ("Frank Wu", "frank@example.com", "2022-11-05"),
        ],
    )
    cur.executemany(
        "INSERT INTO products (name, category_id, price) VALUES (%s, %s, %s)",
        [
            ("Wireless Mouse", 1, 29.99),
            ("USB-C Hub", 1, 49.50),
            ("Desk Lamp", 2, 35.00),
            ("Yoga Mat", 3, 24.00),
            ("Running Shoes", 3, 89.99),
            ("Bluetooth Speaker", 1, 59.00),
        ],
    )
    cur.executemany(
        "INSERT INTO employees (name, hire_date) VALUES (%s, %s)",
        [
            ("Sam Rivera", "2022-03-10"),
            ("Jordan Lee", "2023-11-01"),
            ("Taylor Brooks", "2024-04-15"),
            ("Morgan Ellis", "2024-09-02"),
        ],
    )

    order_rows = [
        (1, "2024-01-15"),
        (1, "2024-02-20"),
        (2, "2024-02-22"),
        (3, "2024-03-05"),
        (3, "2024-03-18"),
        (4, "2024-05-10"),
        (5, "2024-06-01"),
        (5, "2024-06-25"),
        (1, "2024-07-08"),
        (2, "2024-08-14"),
        (6, "2024-09-30"),
        (4, "2024-10-12"),
        (3, "2024-11-03"),
        (5, "2024-12-18"),
    ]
    cur.executemany(
        "INSERT INTO orders (customer_id, order_date) VALUES (%s, %s)",
        order_rows,
    )

    items = [
        (1, 1, 2, 29.99),
        (1, 4, 1, 24.00),
        (2, 2, 1, 49.50),
        (2, 6, 1, 59.00),
        (3, 3, 1, 35.00),
        (4, 5, 1, 89.99),
        (5, 1, 1, 29.99),
        (5, 2, 2, 49.50),
        (6, 6, 2, 59.00),
        (7, 4, 3, 24.00),
        (8, 5, 1, 89.99),
        (9, 3, 1, 35.00),
        (10, 1, 4, 29.99),
        (11, 2, 1, 49.50),
        (12, 5, 1, 89.99),
        (13, 6, 1, 59.00),
        (14, 4, 2, 24.00),
    ]
    cur.executemany(
        """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (%s, %s, %s, %s)
        """,
        items,
    )

    cur.executemany(
        """
        INSERT INTO reviews (product_id, customer_id, rating, review_date)
        VALUES (%s, %s, %s, %s)
        """,
        [
            (1, 1, 4.5, "2024-03-01"),
            (1, 2, 3.0, "2024-04-10"),
            (5, 3, 4.8, "2024-05-20"),
            (5, 4, 4.9, "2024-06-01"),
            (6, 5, 4.2, "2024-07-15"),
            (2, 6, 2.5, "2024-08-01"),
        ],
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Sample schema + data loaded OK.")


if __name__ == "__main__":
    main()
