import sqlite3

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def initialize_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Create users table (if it doesn't exist)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Check if the 'email' column exists in the users table
    if not column_exists(cursor, 'users', 'email'):
        print("Adding missing 'email' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    else:
        print("'email' column already exists in users table.")

    # Create files table (if it doesn't exist)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            owner TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()
