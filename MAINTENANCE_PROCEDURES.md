# 🔄 Server Maintenance & Backup Procedures

## 📅 Daily Maintenance Tasks

### Automated Daily Backup
Create this script to run daily via cron:

```bash
#!/bin/bash
# File: /opt/shift-roster/scripts/daily_backup.sh

# Configuration
BACKUP_DIR="/opt/shift-roster/backups"
DATABASE_PATH="/opt/shift-roster/data/database"
UPLOADS_PATH="/opt/shift-roster/data/uploads"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR/database $BACKUP_DIR/uploads

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔄 Starting daily backup - $TIMESTAMP"

# Backup database
echo "📊 Backing up database..."
cp $DATABASE_PATH/app.db $BACKUP_DIR/database/app_$TIMESTAMP.db
gzip $BACKUP_DIR/database/app_$TIMESTAMP.db

# Backup uploads (if any new files)
echo "📁 Backing up uploads..."
if [ -d "$UPLOADS_PATH" ] && [ "$(ls -A $UPLOADS_PATH)" ]; then
    tar -czf $BACKUP_DIR/uploads/uploads_$TIMESTAMP.tar.gz -C $UPLOADS_PATH .
fi

# Clean old backups
echo "🧹 Cleaning old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR/database -name "app_*.db.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/uploads -name "uploads_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log success
echo "✅ Daily backup completed - $TIMESTAMP"
echo "Backup completed at $(date)" >> /opt/shift-roster/logs/backup.log

# Check application health
curl -f http://localhost:5001/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Application health check passed"
else
    echo "❌ Application health check failed" | tee -a /opt/shift-roster/logs/error.log
fi
```

### Set Up Daily Backup Cron Job
```bash
# Make script executable
chmod +x /opt/shift-roster/scripts/daily_backup.sh

# Add to crontab (runs at 2 AM daily)
crontab -e
# Add this line:
0 2 * * * /opt/shift-roster/scripts/daily_backup.sh
```

## 📊 Weekly Maintenance Tasks

### Weekly System Check Script
```bash
#!/bin/bash
# File: /opt/shift-roster/scripts/weekly_check.sh

echo "🔍 Weekly System Check - $(date)"
echo "=================================="

# Check disk space
echo "💾 Disk Space Usage:"
df -h /opt/shift-roster

# Check Docker containers
echo ""
echo "🐳 Docker Container Status:"
cd /opt/shift-roster/app
docker-compose -f docker-compose.prod.yml ps

# Check container health
echo ""
echo "🏥 Container Health Status:"
docker-compose -f docker-compose.prod.yml exec backend curl -f http://localhost:5001/health
docker-compose -f docker-compose.prod.yml exec frontend curl -f http://localhost:3000

# Check system resources
echo ""
echo "📈 System Resource Usage:"
echo "Memory Usage:"
free -h
echo "CPU Load:"
uptime

# Check log sizes
echo ""
echo "📝 Log File Sizes:"
du -sh /opt/shift-roster/logs/*

# Database size
echo ""
echo "🗃️ Database Size:"
ls -lh /opt/shift-roster/data/database/app.db

# Check for errors in logs
echo ""
echo "❌ Recent Errors in Logs:"
grep -i error /opt/shift-roster/logs/*.log | tail -10

echo ""
echo "✅ Weekly check completed"
```

### Set Up Weekly Check
```bash
chmod +x /opt/shift-roster/scripts/weekly_check.sh

# Add to crontab (runs Sunday at 3 AM)
crontab -e
# Add this line:
0 3 * * 0 /opt/shift-roster/scripts/weekly_check.sh >> /opt/shift-roster/logs/weekly_check.log 2>&1
```

## 🔄 Application Updates

### Update Procedure
```bash
#!/bin/bash
# File: /opt/shift-roster/scripts/update_application.sh

echo "🔄 Starting application update..."

# Stop the application
echo "⏹️ Stopping application..."
cd /opt/shift-roster/app
docker-compose -f docker-compose.prod.yml down

# Backup current database before update
echo "💾 Creating pre-update backup..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp /opt/shift-roster/data/database/app.db /opt/shift-roster/backups/pre_update_$TIMESTAMP.db

# Pull latest changes
echo "⬇️ Pulling latest changes..."
git pull origin main

# Rebuild containers
echo "🔨 Rebuilding containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start application
echo "🚀 Starting updated application..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for startup
echo "⏳ Waiting for startup..."
sleep 30

# Test application
echo "🧪 Testing application..."
if curl -f http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ Update successful - application is healthy"
else
    echo "❌ Update failed - rolling back..."
    docker-compose -f docker-compose.prod.yml down
    git checkout HEAD~1
    docker-compose -f docker-compose.prod.yml up --build -d
fi

echo "Update completed at $(date)"
```

## 🔍 Monitoring & Alerting

### System Monitoring Script
```bash
#!/bin/bash
# File: /opt/shift-roster/scripts/monitor.sh

# Thresholds
DISK_THRESHOLD=80
MEMORY_THRESHOLD=80
CPU_THRESHOLD=2.0

# Check disk space
DISK_USAGE=$(df /opt/shift-roster | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
    echo "⚠️ WARNING: Disk usage is ${DISK_USAGE}% (threshold: ${DISK_THRESHOLD}%)"
    echo "Disk usage alert at $(date): ${DISK_USAGE}%" >> /opt/shift-roster/logs/alerts.log
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt $MEMORY_THRESHOLD ]; then
    echo "⚠️ WARNING: Memory usage is ${MEMORY_USAGE}% (threshold: ${MEMORY_THRESHOLD}%)"
    echo "Memory usage alert at $(date): ${MEMORY_USAGE}%" >> /opt/shift-roster/logs/alerts.log
fi

# Check CPU load
CPU_LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
if (( $(echo "$CPU_LOAD > $CPU_THRESHOLD" | bc -l) )); then
    echo "⚠️ WARNING: CPU load is ${CPU_LOAD} (threshold: ${CPU_THRESHOLD})"
    echo "CPU load alert at $(date): ${CPU_LOAD}" >> /opt/shift-roster/logs/alerts.log
fi

# Check if Docker containers are running
CONTAINER_COUNT=$(docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml ps -q | wc -l)
if [ $CONTAINER_COUNT -lt 2 ]; then
    echo "❌ ERROR: Not all containers are running (found: $CONTAINER_COUNT, expected: 2)"
    echo "Container failure at $(date): Only $CONTAINER_COUNT containers running" >> /opt/shift-roster/logs/alerts.log
fi

# Check application health
if ! curl -f http://localhost:5001/health > /dev/null 2>&1; then
    echo "❌ ERROR: Application health check failed"
    echo "Health check failure at $(date)" >> /opt/shift-roster/logs/alerts.log
fi
```

### Set Up Monitoring
```bash
chmod +x /opt/shift-roster/scripts/monitor.sh

# Add to crontab (runs every 5 minutes)
crontab -e
# Add this line:
*/5 * * * * /opt/shift-roster/scripts/monitor.sh
```

## 📧 Email Alerts (Optional)

### Email Alert Script
```bash
#!/bin/bash
# File: /opt/shift-roster/scripts/send_alert.sh

ALERT_EMAIL="admin@yourcompany.com"
SMTP_SERVER="your-smtp-server.com"
SMTP_PORT="587"
SMTP_USER="alerts@yourcompany.com"
SMTP_PASS="your-smtp-password"

send_email() {
    local subject="$1"
    local body="$2"
    
    echo "Subject: $subject" > /tmp/alert_email.txt
    echo "From: $SMTP_USER" >> /tmp/alert_email.txt
    echo "To: $ALERT_EMAIL" >> /tmp/alert_email.txt
    echo "" >> /tmp/alert_email.txt
    echo "$body" >> /tmp/alert_email.txt
    
    # Send email using sendmail or mail command
    cat /tmp/alert_email.txt | sendmail $ALERT_EMAIL
    rm /tmp/alert_email.txt
}

# Check for new alerts
if [ -f /opt/shift-roster/logs/alerts.log ]; then
    RECENT_ALERTS=$(tail -n 10 /opt/shift-roster/logs/alerts.log)
    if [ ! -z "$RECENT_ALERTS" ]; then
        send_email "Shift Roster App Alert" "$RECENT_ALERTS"
    fi
fi
```

## 🗄️ Database Maintenance

### Database Optimization Script
```bash
#!/bin/bash
# File: /opt/shift-roster/scripts/optimize_database.sh

DATABASE_PATH="/opt/shift-roster/data/database/app.db"

echo "🔧 Optimizing database..."

# Create backup before optimization
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp $DATABASE_PATH /opt/shift-roster/backups/pre_optimize_$TIMESTAMP.db

# Run SQLite optimization
echo "⚡ Running VACUUM and ANALYZE..."
sqlite3 $DATABASE_PATH "VACUUM; ANALYZE;"

# Check database integrity
echo "🔍 Checking database integrity..."
INTEGRITY_CHECK=$(sqlite3 $DATABASE_PATH "PRAGMA integrity_check;")
if [ "$INTEGRITY_CHECK" = "ok" ]; then
    echo "✅ Database integrity check passed"
else
    echo "❌ Database integrity check failed: $INTEGRITY_CHECK"
    echo "Database integrity failure at $(date): $INTEGRITY_CHECK" >> /opt/shift-roster/logs/alerts.log
fi

echo "Database optimization completed at $(date)"
```

### Set Up Monthly Database Optimization
```bash
chmod +x /opt/shift-roster/scripts/optimize_database.sh

# Add to crontab (runs first day of month at 1 AM)
crontab -e
# Add this line:
0 1 1 * * /opt/shift-roster/scripts/optimize_database.sh
```

## 📋 Maintenance Checklist

### Daily Tasks (Automated)
- [ ] Database backup
- [ ] System health check
- [ ] Log rotation
- [ ] Clear temporary files

### Weekly Tasks
- [ ] Review system resources
- [ ] Check error logs
- [ ] Verify backups
- [ ] Test application features

### Monthly Tasks
- [ ] Update system packages
- [ ] Optimize database
- [ ] Review and archive old logs
- [ ] Test disaster recovery procedure

### Quarterly Tasks
- [ ] Update Docker images
- [ ] Security audit
- [ ] Performance optimization
- [ ] Update documentation

## 🆘 Disaster Recovery

### Quick Recovery Procedure
```bash
#!/bin/bash
# File: /opt/shift-roster/scripts/disaster_recovery.sh

echo "🆘 Starting disaster recovery..."

# Stop any running containers
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml down

# Restore latest database backup
LATEST_BACKUP=$(ls -t /opt/shift-roster/backups/database/app_*.db.gz | head -n1)
if [ ! -z "$LATEST_BACKUP" ]; then
    echo "📄 Restoring database from: $LATEST_BACKUP"
    gunzip -c $LATEST_BACKUP > /opt/shift-roster/data/database/app.db
else
    echo "❌ No database backup found!"
    exit 1
fi

# Restore uploads if available
LATEST_UPLOADS=$(ls -t /opt/shift-roster/backups/uploads/uploads_*.tar.gz | head -n1)
if [ ! -z "$LATEST_UPLOADS" ]; then
    echo "📁 Restoring uploads from: $LATEST_UPLOADS"
    rm -rf /opt/shift-roster/data/uploads/*
    tar -xzf $LATEST_UPLOADS -C /opt/shift-roster/data/uploads/
fi

# Start application
echo "🚀 Starting application..."
cd /opt/shift-roster/app
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Disaster recovery completed"
```

## 📊 Performance Monitoring

### Performance Check Script
```bash
#!/bin/bash
# File: /opt/shift-roster/scripts/performance_check.sh

echo "📈 Performance Check - $(date)"
echo "=============================="

# Database size growth
DB_SIZE=$(ls -lh /opt/shift-roster/data/database/app.db | awk '{print $5}')
echo "Database size: $DB_SIZE"

# Application response time
RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:5001/health)
echo "API response time: ${RESPONSE_TIME}s"

# Container resource usage
echo ""
echo "Container Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Log file sizes
echo ""
echo "Log file sizes:"
du -sh /opt/shift-roster/logs/*

# Number of active users (if tracking)
USER_COUNT=$(sqlite3 /opt/shift-roster/data/database/app.db "SELECT COUNT(*) FROM user WHERE last_login > datetime('now', '-7 days');")
echo "Active users (last 7 days): $USER_COUNT"
```

---

## 📞 Emergency Contacts

**System Administrator**: Your Son  
**Application Owner**: You  
**Company IT Support**: [Company IT Contact]  

## 🆘 Emergency Commands

```bash
# Stop application immediately
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml down

# Restart application
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml restart

# View recent logs
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml logs --tail=100

# Check system resources
htop
df -h
free -h

# Emergency database restore
/opt/shift-roster/scripts/disaster_recovery.sh
```

**Remember**: Always create a backup before making any changes!
