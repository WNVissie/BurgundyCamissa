"""Update role permissions in the database"""
import psycopg2
import os
import json

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ Set DATABASE_URL environment variable first")
    exit(1)

# Define permissions for each role
role_permissions = {
    'Admin': {
        'manage_employees': True,
        'manage_shifts': True,
        'view_analytics': True,
        'manage_roles': True,
        'approve_timesheets': True,
        'manage_leave': True,
        'view_all_employees': True,
        'manage_areas': True,
        'manage_skills': True
    },
    'Manager': {
        'manage_shifts': True,
        'view_analytics': True,
        'approve_timesheets': True,
        'manage_leave': True,  # Can approve leave
        'view_all_employees': True,
        'view_own_data': True
    },
    'Employee': {
        'view_own_data': True,
        'submit_leave': True,
        'view_own_roster': True,
        'accept_shifts': True
    }
}

conn = psycopg2.connect(database_url)
cur = conn.cursor()

print("\n🔧 Updating Role Permissions...")
print("=" * 80)

for role_name, permissions in role_permissions.items():
    permissions_json = json.dumps(permissions)
    
    cur.execute(
        "UPDATE roles SET permissions = %s WHERE name = %s RETURNING id, name",
        (permissions_json, role_name)
    )
    
    result = cur.fetchone()
    if result:
        print(f"\n✅ Updated: {result[1]}")
        print(f"   Permissions: {json.dumps(permissions, indent=2)}")
    else:
        print(f"\n⚠️  Role '{role_name}' not found - skipping")

conn.commit()

# Verify the updates
print("\n" + "=" * 80)
print("\n📋 Final Verification:")
print("=" * 80)

cur.execute("SELECT id, name, permissions FROM roles ORDER BY id")
roles = cur.fetchall()

for role in roles:
    print(f"\n{role[1]}:")
    perms = json.loads(role[2]) if role[2] else {}
    if perms:
        for perm, value in perms.items():
            print(f"  ✓ {perm}: {value}")
    else:
        print("  (No permissions)")

print("\n" + "=" * 80)
print(f"\n✅ Successfully updated {len(role_permissions)} roles!")

cur.close()
conn.close()
