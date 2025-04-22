import sqlite3

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA Table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def initialize_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Create users table (if it doesn't exist)
    cursor.execute("""
                    Create table if not exists users (
                        id integer primary key autoincrement,
                        username text unique,
                        password text)
                    """)

    # Check if the 'email' column exists in the users table
    if not column_exists(cursor, 'users', 'email'):
        print("Adding missing 'email' column to users table...")
        cursor.execute("Alter table users add column email text")
    else:
        print("'email' column already exists in users table.")

    # Create files table (if it doesn't exist)
    cursor.execute( """
                    Create table if not exists files (
                        id integer primary key autoincrement,
                        filename text,
                        owner text)
                    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()
