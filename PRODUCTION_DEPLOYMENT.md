# 🚀 Production Server Deployment Instructions

## 📦 Pre-Deployment Checklist

### Before Your Son Starts
- [ ] Server meets requirements (see SERVER_REQUIREMENTS.md)
- [ ] Docker and Docker Compose installed
- [ ] Firewall ports configured
- [ ] Application files copied to server
- [ ] Database backup file available
- [ ] Environment variables configured

## 📁 Step 1: Prepare Server Directory

```bash
# Create application directory
sudo mkdir -p /opt/shift-roster
cd /opt/shift-roster

# Create required subdirectories
sudo mkdir -p data/database data/uploads backups logs ssl

# Set proper ownership (replace 'username' with actual user)
sudo chown -R username:username /opt/shift-roster
```

## 📂 Step 2: Transfer Application Files

### Option A: Using SCP (from your local machine)
```bash
# From your local machine, copy the entire project
scp -r employee-shift-roster-app/ username@server-ip:/opt/shift-roster/app/
```

### Option B: Using Git (recommended)
```bash
# Clone the repository on the server
cd /opt/shift-roster
git clone https://github.com/WNVissie/BurgundyShifts.git app
cd app
```

### Option C: Manual File Transfer
Upload these files to `/opt/shift-roster/app/`:
- `docker-compose.prod.yml`
- `shift-roster-backend/` (entire folder)
- `shift-roster-frontend/` (entire folder)
- `PRODUCTION_ENV.template` (rename to `.env`)

## 🗃️ Step 3: Transfer and Restore Database

### Copy Database Files
```bash
# Create database directory
mkdir -p /opt/shift-roster/data/database

# Copy your database file to server (from your local machine)
scp shift-roster-backend/src/database/app.db username@server-ip:/opt/shift-roster/data/database/

# Set proper permissions
chmod 644 /opt/shift-roster/data/database/app.db
```

### Verify Database
```bash
# Test database connection
cd /opt/shift-roster/app/shift-roster-backend
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/shift-roster/data/database/app.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print('Database tables:', tables)
conn.close()
print('Database connection successful!')
"
```

## ⚙️ Step 4: Configure Environment Variables

### Create Production Environment File
```bash
cd /opt/shift-roster/app
cp PRODUCTION_ENV.template .env
```

### Edit Environment Variables
```bash
nano .env
```

**Required Changes:**
```env
# Database path
DATABASE_URL=sqlite:////opt/shift-roster/data/database/app.db

# Server settings
HOST=0.0.0.0
PORT=5001

# Security (generate new secret key)
SECRET_KEY=your-super-secret-key-here

# File uploads
UPLOAD_FOLDER=/opt/shift-roster/data/uploads

# Production settings
FLASK_ENV=production
DEBUG=False

# Domain name (update with your domain)
FRONTEND_URL=https://your-domain.com
```

### Generate Secret Key
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

## 🐳 Step 5: Deploy with Docker

### Build and Start Services
```bash
cd /opt/shift-roster/app

# Use production docker-compose file
docker-compose -f docker-compose.prod.yml up --build -d
```

### Verify Deployment
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs

# Test backend API
curl http://localhost:5001/health

# Test frontend
curl http://localhost:3000
```

## 🌐 Step 6: Configure Reverse Proxy (Recommended)

### Install Nginx
```bash
sudo apt update
sudo apt install nginx
```

### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/shift-roster
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    # SSL configuration (update paths)
    ssl_certificate /opt/shift-roster/ssl/cert.pem;
    ssl_certificate_key /opt/shift-roster/ssl/key.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/shift-roster /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔐 Step 7: SSL Certificate Setup

### Option A: Let's Encrypt (Free)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option B: Company Certificate
- Copy company SSL certificate files to `/opt/shift-roster/ssl/`
- Update Nginx configuration with correct paths

## 🔄 Step 8: Setup Auto-Start

### Create Systemd Service
```bash
sudo nano /etc/systemd/system/shift-roster.service
```

**Service Configuration:**
```ini
[Unit]
Description=Employee Shift Roster App
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/opt/shift-roster/app
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
User=username

[Install]
WantedBy=multi-user.target
```

### Enable Auto-Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable shift-roster.service
sudo systemctl start shift-roster.service
```

## ✅ Step 9: Final Verification

### Test All Features
1. **Access Application**: Navigate to `https://your-domain.com`
2. **Login**: Test admin login functionality
3. **Database**: Verify all data is present
4. **Notifications**: Check admin badges and notifications work
5. **File Uploads**: Test file upload functionality
6. **Reports**: Generate and download reports

### Performance Check
```bash
# Check system resources
htop
df -h
docker stats

# Check application logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🚨 Troubleshooting

### Common Issues

**Containers Won't Start:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check system resources
df -h
free -h
```

**Database Connection Errors:**
```bash
# Check database file permissions
ls -la /opt/shift-roster/data/database/
# Should be readable by container user
```

**Permission Denied:**
```bash
# Fix ownership
sudo chown -R username:username /opt/shift-roster/
```

**Port Already in Use:**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :3000
sudo netstat -tlnp | grep :5001
```

## 📞 Getting Help

### If Problems Occur:
1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify all environment variables are set correctly
3. Check server resources (disk space, memory)
4. Contact you for application-specific issues

### Important Log Locations:
- Docker logs: `docker-compose -f docker-compose.prod.yml logs`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`

## 🎉 Success Indicators

### Application is Working When:
- [ ] Both containers are running: `docker-compose -f docker-compose.prod.yml ps`
- [ ] Website loads at your domain
- [ ] Admin can login successfully
- [ ] All employee data is visible
- [ ] Notification badges appear for pending items
- [ ] Reports can be generated and downloaded

---

**Deployment Complete!** 🎊

The application should now be running on your company server. Make sure to set up regular backups and monitoring as outlined in the maintenance procedures.