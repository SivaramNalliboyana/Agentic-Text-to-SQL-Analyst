import sqlite3

def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers
                   (
                       id INTEGER PRIMARY KEY,
                       name TEXT,
                       city TEXT
                   )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
           id INTEGER PRIMARY KEY,
           name TEXT,
           price REAL,
           category TEXT
           )
    ''')

    cursor.execute(
        "INSERT OR IGNORE INTO customers (id, name, city) VALUES (1, 'Alice', 'New York'), (2, 'Bob', 'London')")
    cursor.execute(
        "INSERT OR IGNORE INTO products (id, name, price, category) VALUES (10, 'Laptop', 1200, 'Electronics'), (11, 'Apple', 1, 'Food')")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
