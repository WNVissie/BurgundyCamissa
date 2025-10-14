"""Check roles in the database"""
import psycopg2
import os

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("Set DATABASE_URL environment variable first")
    exit(1)

conn = psycopg2.connect(database_url)
cur = conn.cursor()

print("\n✅ Roles in Database:")
print("-" * 80)
cur.execute("SELECT id, name, permissions, created_at FROM roles ORDER BY id")
roles = cur.fetchall()

for role in roles:
    print(f"\nID: {role[0]}")
    print(f"Name: {role[1]}")
    print(f"Permissions: {role[2]}")
    print(f"Created: {role[3]}")
    print("-" * 80)

print(f"\nTotal Roles: {len(roles)}")

cur.close()
conn.close()
