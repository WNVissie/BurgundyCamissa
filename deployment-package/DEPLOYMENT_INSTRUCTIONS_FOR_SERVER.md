# 🚀 Server Deployment Instructions - Employee Shift Roster

## 📦 **What's in this Package**

This deployment package contains everything needed to run the Employee Shift Roster application on your server:

- ✅ **Complete Docker Setup**: Frontend + Backend containers
- ✅ **Production Database**: Pre-populated with sample data and 48 hourly rates
- ✅ **All Configuration Files**: Ready for production deployment
- ✅ **Documentation**: API docs, deployment guides, and feature documentation

## 🏗️ **Server Requirements**

- **Docker** and **Docker Compose** installed
- **Minimum 2GB RAM**
- **10GB free disk space**
- **Ports 3000 and 5001** available
- **Linux/Ubuntu Server** (recommended) or Windows Server

## 🚀 **Quick Start Deployment**

### **Step 1: Upload Package to Server**
```bash
# Upload the entire project folder to your server
scp -r employee-shift-roster-app user@your-server:/home/user/
```

### **Step 2: Setup Database**
```bash
cd /home/user/employee-shift-roster-app
mkdir -p shift-roster-backend/src/database
cp deployment-package/database/app.db shift-roster-backend/src/database/
```

### **Step 3: Deploy with Docker**
```bash
# On Linux/Mac server:
chmod +x start-docker.bat
./start-docker.bat

# Or manually:
docker-compose up --build -d
```

### **Step 4: Verify Deployment**
- **Frontend**: http://your-server-ip:3000
- **Backend API**: http://your-server-ip:5001/api/health
- **Admin Panel**: Login and check all functions work

## 🔧 **Configuration for Production**

### **Environment Variables (Optional)**
Create a `.env` file in the root directory:

```env
# Production Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-production-key

# Database (using SQLite included in package)
DATABASE_URL=sqlite:///src/database/app.db

# Security
CORS_ORIGINS=http://your-domain.com,https://your-domain.com

# Optional: Email notifications
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### **Docker Compose Override (if needed)**
If you need to customize ports or settings, create `docker-compose.override.yml`:

```yaml
version: '3.8'
services:
  frontend:
    ports:
      - "80:3000"  # Change to port 80 for web
  backend:
    ports:
      - "8000:5001"  # Change backend port if needed
    environment:
      - FLASK_ENV=production
```

## 🌐 **Domain Setup (Optional)**

### **Nginx Reverse Proxy**
If you want to use a domain name, install Nginx:

```bash
sudo apt install nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/shift-roster
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/shift-roster /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔐 **Production Login Credentials**

The database comes with the production user account:

### **Admin User:**
- **Email**: wanda.nezar@icloud.com  
- **Password**: Wanda1970!
- **Role**: Administrator (full access)

### **Alternative Admin Email:**
- **Email**: wanda.nezar@gmail.com
- **Password**: Wanda1970!
- **Role**: Administrator (if configured)

**✅ These are the production credentials - ready to use!**

## 📊 **Database Information**

### **Pre-loaded Data:**
- ✅ **48 Hourly Rates** for cost calculations
- ✅ **Sample Employees** (Admin, Manager, Employee roles)
- ✅ **Skills & Designations** (Electrician, Plumber, etc.)
- ✅ **Areas & Licenses** for employee assignments
- ✅ **Cost calculation** system fully functional

### **Database Location:**
- **File**: `shift-roster-backend/src/database/app.db`
- **Backup**: Always backup this file before updates
- **Size**: ~180KB with sample data

## 🔧 **Management Commands**

### **Check Container Status:**
```bash
docker-compose ps
docker-compose logs -f
```

### **Stop/Start Application:**
```bash
docker-compose down    # Stop
docker-compose up -d   # Start
```

### **View Logs:**
```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only  
docker-compose logs -f frontend
```

### **Update Application:**
```bash
# Stop containers
docker-compose down

# Backup database
cp shift-roster-backend/src/database/app.db backup-$(date +%Y%m%d).db

# Pull new version and rebuild
git pull origin main
docker-compose up --build -d
```

## 🚨 **Troubleshooting**

### **Common Issues:**

**Port Already in Use:**
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :5001

# Change ports in docker-compose.yml if needed
```

**Database Permission Issues:**
```bash
# Fix database permissions
sudo chown -R 1000:1000 shift-roster-backend/src/database/
chmod 664 shift-roster-backend/src/database/app.db
```

**Container Won't Start:**
```bash
# Check Docker daemon
sudo systemctl status docker

# View detailed logs
docker-compose logs backend
docker-compose logs frontend
```

### **Health Checks:**
- **Backend Health**: `curl http://localhost:5001/health`
- **API Test**: `curl http://localhost:5001/api/roles`
- **Frontend**: Open `http://localhost:3000` in browser

## 📱 **Application Features Ready**

### **Fully Functional:**
- ✅ **User Authentication** (Login/Register/Google OAuth)
- ✅ **Employee Management** (Add, edit, view employees)
- ✅ **Roster Scheduling** (Create and manage shifts)
- ✅ **Leave Management** (Request, approve, track leave)
- ✅ **Timesheets** (Track hours worked)
- ✅ **Analytics Dashboard** (Cost calculations with hourly rates)
- ✅ **Admin Panel** (Manage roles, areas, skills, shifts, licenses)
- ✅ **File Uploads** (Image compression, document attachments)
- ✅ **Export/Import** (Excel, CSV data exchange)

### **Security Features:**
- ✅ **JWT Authentication** with secure tokens
- ✅ **Role-based Access Control** (Admin/Manager/Employee)
- ✅ **Input Validation** and SQL injection protection
- ✅ **File Upload Security** with type validation
- ✅ **Password Hashing** with bcrypt

## 📞 **Support & Maintenance**

### **Backup Strategy:**
```bash
#!/bin/bash
# Create backup script: backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp shift-roster-backend/src/database/app.db backups/app_db_$DATE.db
echo "Database backed up to: backups/app_db_$DATE.db"
```

### **Log Rotation:**
```bash
# Add to crontab for log cleanup
0 2 * * * docker system prune -f
0 3 * * 0 find /var/lib/docker/containers -name "*.log" -exec truncate -s 0 {} \;
```

### **Monitoring:**
- Monitor disk space (database will grow over time)
- Check logs for errors: `docker-compose logs -f`
- Backup database regularly
- Update containers periodically for security

## 🎯 **Next Steps After Deployment**

1. **Change Default Passwords** for all test users
2. **Add Real Employee Data** via admin panel
3. **Configure Email Settings** for notifications (optional)
4. **Setup SSL Certificate** if using domain name
5. **Configure Backups** for database
6. **Test All Features** to ensure everything works
7. **Train Users** on the application

## 📚 **Additional Documentation**

- **API_DOCUMENTATION.md** - Complete API reference
- **DEPLOYMENT_GUIDE.md** - Detailed deployment options
- **IMAGE_COMPRESSION_GUIDE.md** - File upload features
- **userguide.md** - End-user instructions

---

**🎉 Your Employee Shift Roster application is ready for production!**

The application includes everything needed for managing employee schedules, tracking time, calculating costs, and handling leave requests. All features are fully functional and ready for your team to use.

If you encounter any issues during deployment, check the logs with `docker-compose logs -f` and ensure all ports are available.