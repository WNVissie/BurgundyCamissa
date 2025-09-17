# 🗃️ Database Migration Guide

## 📋 Overview

This guide explains how to safely copy your existing SQLite database to the production server and ensure all data is preserved during deployment.

## 🔍 Pre-Migration: Identify Your Database

### Locate Current Database
Your database is located at:
```
shift-roster-backend/src/database/app.db
```

### Backup Current Database (Important!)
Before migration, create a backup:
```cmd
REM From your local machine
cd shift-roster-backend\src\database
copy app.db app.db.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%
```

## 📊 Database Content Verification

### Check Database Tables and Data
Run this script to verify your database contents before migration:

```python
# check_database_contents.py
import sqlite3
import os

def verify_database(db_path):
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("🗃️ Database Tables Found:")
        total_records = 0
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"  📋 {table_name}: {count} records")
        
        print(f"\n📊 Total Records: {total_records}")
        
        # Check for critical tables
        critical_tables = ['user', 'employee', 'roster', 'timesheet', 'leave_request', 'community_post']
        missing_tables = []
        
        table_names = [t[0] for t in tables]
        for critical in critical_tables:
            if critical not in table_names:
                missing_tables.append(critical)
        
        if missing_tables:
            print(f"⚠️ Missing critical tables: {missing_tables}")
        else:
            print("✅ All critical tables present")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    db_path = "app.db"
    verify_database(db_path)
```

### Run Database Verification
```cmd
cd shift-roster-backend\src\database
python ..\..\..\check_database_contents.py
```

## 📤 Preparing Database for Transfer

### 1. Create Migration Package
Create a folder with all necessary files:
```cmd
mkdir database_migration
cd database_migration

REM Copy database
copy ..\shift-roster-backend\src\database\app.db .

REM Copy database verification script
copy check_database_contents.py .

REM Create migration info file
echo Migration Date: %date% %time% > migration_info.txt
echo Source: Local Development >> migration_info.txt
echo Target: Production Server >> migration_info.txt
```

### 2. Compress for Transfer
```cmd
REM Create zip file for easy transfer
powershell Compress-Archive -Path database_migration\* -DestinationPath database_migration.zip
```

## 🚚 Transfer Database to Server

### Option A: Secure Copy (SCP)
```bash
# From your local machine to server
scp database_migration.zip username@server-ip:/tmp/
```

### Option B: SFTP Transfer
```bash
sftp username@server-ip
put database_migration.zip /tmp/
quit
```

### Option C: Cloud Storage
1. Upload `database_migration.zip` to Google Drive, Dropbox, etc.
2. Download on server using wget or curl

## 🖥️ Server-Side Database Setup

### 1. Extract Migration Package
```bash
# On the server
cd /tmp
unzip database_migration.zip
cd database_migration
```

### 2. Verify Database Integrity
```bash
# Check database file
ls -la app.db
file app.db

# Verify contents
python3 check_database_contents.py
```

### 3. Install Database in Correct Location
```bash
# Create database directory if not exists
sudo mkdir -p /opt/shift-roster/data/database

# Copy database with proper permissions
sudo cp app.db /opt/shift-roster/data/database/
sudo chown username:username /opt/shift-roster/data/database/app.db
sudo chmod 664 /opt/shift-roster/data/database/app.db
```

## 🔧 Post-Migration Configuration

### 1. Update Environment Variables
Ensure the Docker environment points to the correct database:
```env
DATABASE_URL=sqlite:////opt/shift-roster/data/database/app.db
```

### 2. Test Database Connection
```bash
cd /opt/shift-roster/app/shift-roster-backend

# Test connection
python3 -c "
import sqlite3
import os

db_path = '/opt/shift-roster/data/database/app.db'
print(f'Testing database: {db_path}')
print(f'File exists: {os.path.exists(db_path)}')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute('SELECT COUNT(*) FROM user')
    user_count = cursor.fetchone()[0]
    print(f'Users in database: {user_count}')
    
    cursor.execute('SELECT COUNT(*) FROM employee')
    employee_count = cursor.fetchone()[0]
    print(f'Employees in database: {employee_count}')
    
    conn.close()
    print('✅ Database connection successful!')
    
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

## 🔄 Database Migrations (If Needed)

### Check for Missing Tables
If the application has been updated since your database was created:

```bash
# From application directory
cd /opt/shift-roster/app/shift-roster-backend

# Run any pending migrations
python3 migrate_user_auth_fields.py
python3 create_notifications_table.py

# Check if all tables exist
python3 -c "
from src.models.models import db
from src.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/shift-roster/data/database/app.db'

with app.app_context():
    db.init_app(app)
    # This will create any missing tables
    db.create_all()
    print('✅ Database schema updated')
"
```

## 📊 Verify Migration Success

### 1. Start Docker Containers
```bash
cd /opt/shift-roster/app
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Test Application Access
```bash
# Check if backend can access database
curl http://localhost:5001/health

# Check if users can login (test with known credentials)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your-admin-username","password":"your-admin-password"}'
```

### 3. Verify Data in Application
- Access the web interface
- Login as admin
- Check that all employees are visible
- Verify roster data is present
- Check community posts exist
- Test notification system

## 🔧 Troubleshooting Common Issues

### Database Permission Errors
```bash
# Fix permissions
sudo chown username:username /opt/shift-roster/data/database/app.db
sudo chmod 664 /opt/shift-roster/data/database/app.db
```

### Database Locked Errors
```bash
# Check if any processes are using the database
sudo lsof /opt/shift-roster/data/database/app.db

# Stop containers and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Missing Tables
```bash
# Run database initialization
cd /opt/shift-roster/app/shift-roster-backend
python3 src/init_db.py
```

### Data Corruption
```bash
# Test database integrity
sqlite3 /opt/shift-roster/data/database/app.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp /path/to/backup/app.db /opt/shift-roster/data/database/app.db
```

## ✅ Migration Checklist

### Pre-Migration:
- [ ] Database backup created
- [ ] Database contents verified
- [ ] Migration package prepared
- [ ] Transfer method chosen

### During Migration:
- [ ] Database transferred to server
- [ ] File permissions set correctly
- [ ] Database integrity verified
- [ ] Environment variables updated

### Post-Migration:
- [ ] Docker containers started successfully
- [ ] Database connection test passed
- [ ] Application login test successful
- [ ] All data visible in interface
- [ ] Notification system working
- [ ] Backup of migrated database created

## 🔐 Security Notes

### Database Security
- Database file should not be web-accessible
- Regular backups should be encrypted
- File permissions should be restrictive (664 or 640)
- Database should be backed up before any updates

### Access Control
- Only application containers should access database
- No direct database access from web interface
- Regular security updates for SQLite

---

**Migration Complete!** 🎉

Your database has been successfully migrated to the production server. All employee data, rosters, timesheets, and community posts should now be available in the production environment.