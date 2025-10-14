# 🚀 Complete Server Deployment Guide (For First-Time Deployers)

**Employee Shift Roster Application - Production Deployment**  
*Step-by-step guide for deploying Docker containers to a company server*

---

## 📋 Before You Start - What You Need

### 👥 People Involved
- **You**: The person deploying (probably Wanda's son)
- **Wanda**: The application owner (contact for questions)
- **Company IT**: Your company's IT support team

### 💻 What You'll Need
- A server (computer) that will host the application
- Admin access to that server
- Internet connection
- About 2-4 hours of time
- Wanda's database file (contains all the employee data)

### 📦 Files Wanda Should Give You
- `database-package/` folder (contains the employee database)
- `shift-roster-backend/` folder (the application backend)
- `shift-roster-frontend/` folder (the web interface)
- All the Docker files (Dockerfile, docker-compose files)
- This deployment guide

---

## 🖥️ STEP 1: Prepare Your Server

### 1.1 Server Requirements (Give This to Your IT Team)
```
Operating System: Ubuntu 20.04 LTS (or newer Linux)
CPU: 2 cores minimum (4 cores preferred)
RAM: 4 GB minimum (8 GB preferred)
Storage: 50 GB available space
Network: Reliable internet connection
Ports needed: 80 (HTTP), 443 (HTTPS), 3000, 5001
```

### 1.2 Get Server Access
Ask your IT team to:
1. Set up the Linux server with the above specifications
2. Give you SSH access (username and password or SSH key)
3. Open the required network ports (80, 443, 3000, 5001)
4. Provide a domain name (like `shifts.yourcompany.com`)

### 1.3 Test Server Connection
```bash
# Connect to your server (replace with your details)
ssh your-username@your-server-ip

# You should see a Linux command prompt like:
username@server:~$
```

---

## 🔧 STEP 2: Install Required Software

### 2.1 Update the Server
```bash
# Run these commands one by one
sudo apt update
sudo apt upgrade -y
```

### 2.2 Install Docker
```bash
# Download and install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and log back in for this to take effect
exit
# Then reconnect: ssh your-username@your-server-ip
```

### 2.3 Install Docker Compose
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Test installation
docker --version
docker-compose --version
```

**✅ Success Check**: You should see version numbers for both Docker and Docker Compose.

---

## 📁 STEP 3: Create Application Directory

### 3.1 Create Main Directory
```bash
# Create the main application folder
sudo mkdir -p /opt/shift-roster
sudo chown -R $USER:$USER /opt/shift-roster
cd /opt/shift-roster

# Create subdirectories
mkdir -p data/database data/uploads backups logs
```

### 3.2 Directory Structure
After this step, you should have:
```
/opt/shift-roster/
├── data/
│   ├── database/    (will contain the employee database)
│   └── uploads/     (for file uploads)
├── backups/         (for database backups)
└── logs/            (for application logs)
```

---

## 📂 STEP 4: Transfer Application Files

### 4.1 Get Files From Wanda
Ask Wanda to provide you with:
- The entire project folder OR
- A zip file containing all application files

### 4.2 Upload Files to Server

**Option A: Using SCP (from your local computer)**
```bash
# From your local machine (not the server)
scp -r path/to/employee-shift-roster-app/ username@server-ip:/opt/shift-roster/app/
```

**Option B: Using Git (if code is on GitHub)**
```bash
# On the server
cd /opt/shift-roster
git clone https://github.com/WNVissie/BurgundyShifts.git app
```

**Option C: Manual Upload**
- Use FileZilla, WinSCP, or similar tool
- Upload all files to `/opt/shift-roster/app/`

### 4.3 Verify Files Are There
```bash
cd /opt/shift-roster/app
ls -la

# You should see:
# shift-roster-backend/
# shift-roster-frontend/ 
# docker-compose.yml
# docker-compose.prod.yml
```

---

## 🗃️ STEP 5: Install the Database (CRITICAL STEP)

### 5.1 Get Database from Wanda
Wanda should give you a `database-package` folder containing:
- `app.db` (the main database file with all employee data)
- `migration_info.txt` (information about the database)

### 5.2 Copy Database to Server
```bash
# Copy the database file to the correct location
cp /path/to/database-package/app.db /opt/shift-roster/data/database/

# Set correct permissions
chmod 664 /opt/shift-roster/data/database/app.db
```

### 5.3 Verify Database Works
```bash
# Test the database
cd /opt/shift-roster/app/shift-roster-backend
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/shift-roster/data/database/app.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM user')
print('Number of users:', cursor.fetchone()[0])
conn.close()
print('Database test successful!')
"
```

**✅ Success Check**: Should show "Database test successful!" and the number of users.

---

## ⚙️ STEP 6: Configure the Application

### 6.1 Create Environment File
```bash
cd /opt/shift-roster/app
cp PRODUCTION_ENV.template .env
```

### 6.2 Edit Configuration Settings
```bash
nano .env
```

**Important Settings to Change:**
```env
# Database location
DATABASE_URL=sqlite:////opt/shift-roster/data/database/app.db

# Your company domain (ask IT team)
FRONTEND_URL=https://shifts.yourcompany.com

# Generate a secret key (run this command to get one):
SECRET_KEY=your-generated-secret-key-here

# Company details
COMPANY_NAME=Your Company Name
COMPANY_EMAIL=admin@yourcompany.com

# File uploads
UPLOAD_FOLDER=/opt/shift-roster/data/uploads

# Set to production
FLASK_ENV=production
DEBUG=False
```

### 6.3 Generate Secret Key
```bash
# Run this to generate a secure secret key
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Copy the output and paste it in your .env file
```

---

## 🐳 STEP 7: Start the Application

### 7.1 Build and Start Containers
```bash
cd /opt/shift-roster/app

# Start the application (this may take 5-10 minutes first time)
docker-compose -f docker-compose.prod.yml up --build -d
```

### 7.2 Check If It's Working
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# You should see two containers running:
# backend (port 5001)
# frontend (port 3000)
```

### 7.3 Test the Application
```bash
# Test backend API
curl http://localhost:5001/health

# Test frontend
curl http://localhost:3000

# Both should return successful responses
```

---

## 🌐 STEP 8: Set Up Web Access

### 8.1 Install Web Server (Nginx)
```bash
sudo apt install nginx -y
```

### 8.2 Configure Web Server
```bash
sudo nano /etc/nginx/sites-available/shift-roster
```

**Add this configuration (replace 'your-domain.com' with your actual domain):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

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

### 8.3 Enable the Site
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/shift-roster /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 🔐 STEP 9: Set Up HTTPS (SSL Certificate)

### 9.1 Install Certbot (for free SSL)
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 9.2 Get SSL Certificate
```bash
# Replace 'your-domain.com' with your actual domain
sudo certbot --nginx -d your-domain.com

# Follow the prompts (it will ask for email and agreement to terms)
```

**✅ Success Check**: Certbot should say "Congratulations! Your certificate and chain have been saved."

---

## ✅ STEP 10: Test Everything

### 10.1 Access the Website
1. Open a web browser
2. Go to `https://your-domain.com`
3. You should see the Employee Shift Roster login page

### 10.2 Test Login (Ask Wanda for Admin Credentials)
1. Use the admin username and password Wanda gives you
2. You should be able to log in successfully
3. Check that you can see employee data, rosters, etc.

### 10.3 Test Key Features
- [ ] Login works
- [ ] Can see employee list
- [ ] Can view rosters/timesheets
- [ ] Notification badges appear (red numbers on menu items)
- [ ] Can generate reports
- [ ] Community posts are visible

---

## 🔄 STEP 11: Set Up Automatic Backups

### 11.1 Create Backup Script
```bash
mkdir -p /opt/shift-roster/scripts
nano /opt/shift-roster/scripts/daily_backup.sh
```

**Add this backup script:**
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/shift-roster/backups"

# Backup database
cp /opt/shift-roster/data/database/app.db $BACKUP_DIR/app_$TIMESTAMP.db
gzip $BACKUP_DIR/app_$TIMESTAMP.db

# Keep only last 30 days of backups
find $BACKUP_DIR -name "app_*.db.gz" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

### 11.2 Make Script Executable and Schedule
```bash
# Make executable
chmod +x /opt/shift-roster/scripts/daily_backup.sh

# Add to daily schedule (runs at 2 AM every day)
crontab -e
# Add this line:
0 2 * * * /opt/shift-roster/scripts/daily_backup.sh
```

---

## 🎉 STEP 12: Make It Start Automatically

### 12.1 Create System Service
```bash
sudo nano /etc/systemd/system/shift-roster.service
```

**Add this service configuration:**
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
User=your-username

[Install]
WantedBy=multi-user.target
```

### 12.2 Enable Auto-Start
```bash
# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable shift-roster.service

# Test the service
sudo systemctl start shift-roster.service
sudo systemctl status shift-roster.service
```

---

## ✅ FINAL CHECKLIST

### Deployment Complete When:
- [ ] Server is set up with Docker installed
- [ ] Application files are uploaded to `/opt/shift-roster/app/`
- [ ] Database is copied to `/opt/shift-roster/data/database/app.db`
- [ ] Environment variables are configured in `.env` file
- [ ] Docker containers are running (`docker-compose ps` shows 2 running containers)
- [ ] Website loads at your domain name
- [ ] Admin can log in successfully
- [ ] All employee data is visible
- [ ] Notification badges work (red numbers on menu items)
- [ ] SSL certificate is installed (https:// works)
- [ ] Daily backups are scheduled
- [ ] Service auto-starts when server reboots

---

## 🆘 If Something Goes Wrong

### Common Problems and Solutions

**Problem**: "Database connection error"
**Solution**: Check that `/opt/shift-roster/data/database/app.db` exists and has correct permissions

**Problem**: "Containers won't start"  
**Solution**: Run `docker-compose -f docker-compose.prod.yml logs` to see error messages

**Problem**: "Website doesn't load"
**Solution**: Check that nginx is running: `sudo systemctl status nginx`

**Problem**: "Login doesn't work"
**Solution**: Verify the database was copied correctly - ask Wanda for correct admin credentials

**Problem**: "No employee data visible"
**Solution**: Database wasn't copied correctly - restore from Wanda's `database-package/app.db`

### Emergency Commands
```bash
# Stop application
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml down

# Start application  
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml up -d

# View error logs
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml logs

# Check system resources
df -h  (disk space)
free -h  (memory usage)
```

### Getting Help
1. **For application issues**: Contact Wanda
2. **For server issues**: Contact your company IT team
3. **For Docker issues**: Check Docker documentation online

---

## 📞 Important Contacts

**Application Owner**: Wanda  
**Email**: [Wanda's email]  
**Phone**: [Wanda's phone]  

**Company IT Support**: [Your IT team contact]

**Domain/DNS**: [Who manages your company domain]

---

## 🎊 Success!

If you've reached this point and all the checkboxes are ticked, congratulations! 

The Employee Shift Roster application is now running on your company server with:
- ✅ All employee data preserved from Wanda's system
- ✅ Secure HTTPS access
- ✅ Automatic daily backups
- ✅ Admin notification system working
- ✅ Professional deployment ready for company use

**The application includes an admin notification system that will show red badges on menu items when there are pending approvals (timesheets, rosters, leave requests) and when new community posts are added.**

Your employees can now access the system at your company domain, and administrators will be notified of items requiring attention!

---

# 🚀 Complete Server Deployment Guide (For First-Time Deployers)

**Employee Shift Roster Application - Production Deployment**  
*Step-by-step guide for deploying Docker containers to a company server*

---

## 📋 Before You Start - What You Need

### 👥 People Involved
- **You**: The person deploying (probably Wanda's son)
- **Wanda**: The application owner (contact for questions)
- **Company IT**: Your company's IT support team

### 💻 What You'll Need
- A server (computer) that will host the application
- Admin access to that server
- Internet connection
- About 2-4 hours of time
- Wanda's database file (contains all the employee data)

### 📦 Files Wanda Should Give You
- `database-package/` folder (contains the employee database)
- `shift-roster-backend/` folder (the application backend)
- `shift-roster-frontend/` folder (the web interface)
- All the Docker files (Dockerfile, docker-compose files)
- This deployment guide

---

## 🖥️ STEP 1: Prepare Your Server

### 1.1 Server Requirements (Give This to Your IT Team)
```
Operating System: Ubuntu 20.04 LTS (or newer Linux)
CPU: 2 cores minimum (4 cores preferred)
RAM: 4 GB minimum (8 GB preferred)
Storage: 50 GB available space
Network: Reliable internet connection
Ports needed: 80 (HTTP), 443 (HTTPS), 3000, 5001
```

### 1.2 Get Server Access
Ask your IT team to:
1. Set up the Linux server with the above specifications
2. Give you SSH access (username and password or SSH key)
3. Open the required network ports (80, 443, 3000, 5001)
4. Provide a domain name (like `shifts.yourcompany.com`)

### 1.3 Test Server Connection
```bash
# Connect to your server (replace with your details)
ssh your-username@your-server-ip

# You should see a Linux command prompt like:
username@server:~$
```

---

## 🔧 STEP 2: Install Required Software

### 2.1 Update the Server
```bash
# Run these commands one by one
sudo apt update
sudo apt upgrade -y
```

### 2.2 Install Docker
```bash
# Download and install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and log back in for this to take effect
exit
# Then reconnect: ssh your-username@your-server-ip
```

### 2.3 Install Docker Compose
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Test installation
docker --version
docker-compose --version
```

**✅ Success Check**: You should see version numbers for both Docker and Docker Compose.

---

## 📁 STEP 3: Create Application Directory

### 3.1 Create Main Directory
```bash
# Create the main application folder
sudo mkdir -p /opt/shift-roster
sudo chown -R $USER:$USER /opt/shift-roster
cd /opt/shift-roster

# Create subdirectories
mkdir -p data/database data/uploads backups logs
```

### 3.2 Directory Structure
After this step, you should have:
```
/opt/shift-roster/
├── data/
│   ├── database/    (will contain the employee database)
│   └── uploads/     (for file uploads)
├── backups/         (for database backups)
└── logs/            (for application logs)
```

---

## 📂 STEP 4: Transfer Application Files

### 4.1 Get Files From Wanda
Ask Wanda to provide you with:
- The entire project folder OR
- A zip file containing all application files

### 4.2 Upload Files to Server

**Option A: Using SCP (from your local computer)**
```bash
# From your local machine (not the server)
scp -r path/to/employee-shift-roster-app/ username@server-ip:/opt/shift-roster/app/
```

**Option B: Using Git (if code is on GitHub)**
```bash
# On the server
cd /opt/shift-roster
git clone https://github.com/WNVissie/BurgundyShifts.git app
```

**Option C: Manual Upload**
- Use FileZilla, WinSCP, or similar tool
- Upload all files to `/opt/shift-roster/app/`

### 4.3 Verify Files Are There
```bash
cd /opt/shift-roster/app
ls -la

# You should see:
# shift-roster-backend/
# shift-roster-frontend/ 
# docker-compose.yml
# docker-compose.prod.yml
```

---

## 🗃️ STEP 5: Install the Database (CRITICAL STEP)

### 5.1 Get Database from Wanda
Wanda should give you a `database-package` folder containing:
- `app.db` (the main database file with all employee data)
- `migration_info.txt` (information about the database)

### 5.2 Copy Database to Server
```bash
# Copy the database file to the correct location
cp /path/to/database-package/app.db /opt/shift-roster/data/database/

# Set correct permissions
chmod 664 /opt/shift-roster/data/database/app.db
```

### 5.3 Verify Database Works
```bash
# Test the database
cd /opt/shift-roster/app/shift-roster-backend
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/shift-roster/data/database/app.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM user')
print('Number of users:', cursor.fetchone()[0])
conn.close()
print('Database test successful!')
"
```

**✅ Success Check**: Should show "Database test successful!" and the number of users.

---

## ⚙️ STEP 6: Configure the Application

### 6.1 Create Environment File
```bash
cd /opt/shift-roster/app
cp PRODUCTION_ENV.template .env
```

### 6.2 Edit Configuration Settings
```bash
nano .env
```

**Important Settings to Change:**
```env
# Database location
DATABASE_URL=sqlite:////opt/shift-roster/data/database/app.db

# Your company domain (ask IT team)
FRONTEND_URL=https://shifts.yourcompany.com

# Generate a secret key (run this command to get one):
SECRET_KEY=your-generated-secret-key-here

# Company details
COMPANY_NAME=Your Company Name
COMPANY_EMAIL=admin@yourcompany.com

# File uploads
UPLOAD_FOLDER=/opt/shift-roster/data/uploads

# Set to production
FLASK_ENV=production
DEBUG=False
```

### 6.3 Generate Secret Key
```bash
# Run this to generate a secure secret key
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Copy the output and paste it in your .env file
```

---

## 🐳 STEP 7: Start the Application

### 7.1 Build and Start Containers
```bash
cd /opt/shift-roster/app

# Start the application (this may take 5-10 minutes first time)
docker-compose -f docker-compose.prod.yml up --build -d
```

### 7.2 Check If It's Working
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# You should see two containers running:
# backend (port 5001)
# frontend (port 3000)
```

### 7.3 Test the Application
```bash
# Test backend API
curl http://localhost:5001/health

# Test frontend
curl http://localhost:3000

# Both should return successful responses
```

---

## 🌐 STEP 8: Set Up Web Access

### 8.1 Install Web Server (Nginx)
```bash
sudo apt install nginx -y
```

### 8.2 Configure Web Server
```bash
sudo nano /etc/nginx/sites-available/shift-roster
```

**Add this configuration (replace 'your-domain.com' with your actual domain):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

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

### 8.3 Enable the Site
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/shift-roster /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 🔐 STEP 9: Set Up HTTPS (SSL Certificate)

### 9.1 Install Certbot (for free SSL)
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 9.2 Get SSL Certificate
```bash
# Replace 'your-domain.com' with your actual domain
sudo certbot --nginx -d your-domain.com

# Follow the prompts (it will ask for email and agreement to terms)
```

**✅ Success Check**: Certbot should say "Congratulations! Your certificate and chain have been saved."

---

## ✅ STEP 10: Test Everything

### 10.1 Access the Website
1. Open a web browser
2. Go to `https://your-domain.com`
3. You should see the Employee Shift Roster login page

### 10.2 Test Login (Ask Wanda for Admin Credentials)
1. Use the admin username and password Wanda gives you
2. You should be able to log in successfully
3. Check that you can see employee data, rosters, etc.

### 10.3 Test Key Features
- [ ] Login works
- [ ] Can see employee list
- [ ] Can view rosters/timesheets
- [ ] Notification badges appear (red numbers on menu items)
- [ ] Can generate reports
- [ ] Community posts are visible

---

## 🔄 STEP 11: Set Up Automatic Backups

### 11.1 Create Backup Script
```bash
mkdir -p /opt/shift-roster/scripts
nano /opt/shift-roster/scripts/daily_backup.sh
```

**Add this backup script:**
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/shift-roster/backups"

# Backup database
cp /opt/shift-roster/data/database/app.db $BACKUP_DIR/app_$TIMESTAMP.db
gzip $BACKUP_DIR/app_$TIMESTAMP.db

# Keep only last 30 days of backups
find $BACKUP_DIR -name "app_*.db.gz" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

### 11.2 Make Script Executable and Schedule
```bash
# Make executable
chmod +x /opt/shift-roster/scripts/daily_backup.sh

# Add to daily schedule (runs at 2 AM every day)
crontab -e
# Add this line:
0 2 * * * /opt/shift-roster/scripts/daily_backup.sh
```

---

## 🎉 STEP 12: Make It Start Automatically

### 12.1 Create System Service
```bash
sudo nano /etc/systemd/system/shift-roster.service
```

**Add this service configuration:**
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
User=your-username

[Install]
WantedBy=multi-user.target
```

### 12.2 Enable Auto-Start
```bash
# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable shift-roster.service

# Test the service
sudo systemctl start shift-roster.service
sudo systemctl status shift-roster.service
```

---

## ✅ FINAL CHECKLIST

### Deployment Complete When:
- [ ] Server is set up with Docker installed
- [ ] Application files are uploaded to `/opt/shift-roster/app/`
- [ ] Database is copied to `/opt/shift-roster/data/database/app.db`
- [ ] Environment variables are configured in `.env` file
- [ ] Docker containers are running (`docker-compose ps` shows 2 running containers)
- [ ] Website loads at your domain name
- [ ] Admin can log in successfully
- [ ] All employee data is visible
- [ ] Notification badges work (red numbers on menu items)
- [ ] SSL certificate is installed (https:// works)
- [ ] Daily backups are scheduled
- [ ] Service auto-starts when server reboots

---

## 🆘 If Something Goes Wrong

### Common Problems and Solutions

**Problem**: "Database connection error"
**Solution**: Check that `/opt/shift-roster/data/database/app.db` exists and has correct permissions

**Problem**: "Containers won't start"  
**Solution**: Run `docker-compose -f docker-compose.prod.yml logs` to see error messages

**Problem**: "Website doesn't load"
**Solution**: Check that nginx is running: `sudo systemctl status nginx`

**Problem**: "Login doesn't work"
**Solution**: Verify the database was copied correctly - ask Wanda for correct admin credentials

**Problem**: "No employee data visible"
**Solution**: Database wasn't copied correctly - restore from Wanda's `database-package/app.db`

### Emergency Commands
```bash
# Stop application
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml down

# Start application  
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml up -d

# View error logs
docker-compose -f /opt/shift-roster/app/docker-compose.prod.yml logs

# Check system resources
df -h  (disk space)
free -h  (memory usage)
```

### Getting Help
1. **For application issues**: Contact Wanda
2. **For server issues**: Contact your company IT team
3. **For Docker issues**: Check Docker documentation online

---

## 📞 Important Contacts

**Application Owner**: Wanda  
**Email**: [Wanda's email]  
**Phone**: [Wanda's phone]  

**Company IT Support**: [Your IT team contact]

**Domain/DNS**: [Who manages your company domain]

---

## 🎊 Success!

If you've reached this point and all the checkboxes are ticked, congratulations! 

The Employee Shift Roster application is now running on your company server with:
- ✅ All employee data preserved from Wanda's system
- ✅ Secure HTTPS access
- ✅ Automatic daily backups
- ✅ Admin notification system working
- ✅ Professional deployment ready for company use

**The application includes an admin notification system that will show red badges on menu items when there are pending approvals (timesheets, rosters, leave requests) and when new community posts are added.**

Your employees can now access the system at your company domain, and administrators will be notified of items requiring attention!

---

*This guide was created specifically for deploying Wanda's Employee Shift Roster Application. For questions about specific features or functionality, contact Wanda directly.*