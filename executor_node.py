import sqlite3

def execute_sql(sql_query):
    try:
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        # Run sql which llama wrote
        cursor.execute(sql_query)

        # Fetch results
        rows = cursor.fetchall()
        conn.close()

        return {"status": "success", "data": rows}

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    test_sql = "SELECT name, price FROM products WHERE category = 'Electronics';"
    result = execute_sql(test_sql)

    print(f"--- EXECUTOR NODE TEST ---")
    if result["status"] == "success":
        print(f"Data Found: {result['data']}")
    else:
        print(f"SQL Error: {result['message']}")
