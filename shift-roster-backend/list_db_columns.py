import sqlite3

# Path to your SQLite database
DB_PATH = 'shift-roster-backend/src/database/app.db'

def get_table_columns(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [row[1] for row in cursor.fetchall()]
        schema[table] = columns
    conn.close()
    return schema

if __name__ == '__main__':
    schema = get_table_columns(DB_PATH)
    for table, columns in schema.items():
        print(f'Table: {table}')
        for col in columns:
            print(f'  - {col}')
        print()
