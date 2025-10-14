"""
Run SQL commands on Render PostgreSQL database
"""
import psycopg2

# Your database connection string
DATABASE_URL = "postgresql://burgundycamissa_user:49S4txcD3CbU5kxMADxzK3qeVF1Zx7sg@dpg-d3n5haur433s73auk3tg-a.ohio-postgres.render.com/burgundycamissa"

print("🔌 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
print("✅ Connected!\n")

# Update Manager permissions
print("📝 Updating Manager role permissions...")
cur.execute("""
    UPDATE roles 
    SET permissions = '{"manage_shifts": true, "view_analytics": true, "approve_timesheets": true, "manage_leave": true, "view_all_employees": true, "view_own_data": true}'
    WHERE name = 'Manager'
""")
print("✅ Manager updated\n")

# Update Employee permissions
print("📝 Updating Employee role permissions...")
cur.execute("""
    UPDATE roles
    SET permissions = '{"view_own_data": true, "submit_leave": true, "view_own_roster": true, "accept_shifts": true}'
    WHERE name = 'Employee'
""")
print("✅ Employee updated\n")

# Commit changes
conn.commit()
print("💾 Changes committed!\n")

# Verify
print("=" * 80)
print("📋 Current Roles and Permissions:")
print("=" * 80)

cur.execute("SELECT id, name, permissions FROM roles ORDER BY id")
roles = cur.fetchall()

for role in roles:
    print(f"\n🔹 {role[1]} (ID: {role[0]})")
    print(f"   Permissions: {role[2]}")

print("\n" + "=" * 80)
print(f"✅ Successfully updated role permissions!")
print("=" * 80)

cur.close()
conn.close()
