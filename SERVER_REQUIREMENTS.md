# 🖥️ Server Requirements for Employee Shift Roster App

## 📋 System Requirements

### Minimum Hardware Specifications
- **CPU**: 2 vCPUs or cores
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 50 GB available disk space
- **Network**: Stable internet connection with adequate bandwidth

### Operating System
- **Recommended**: Ubuntu 20.04 LTS or newer
- **Alternative**: CentOS 8, RHEL 8, or any modern Linux distribution
- **Windows Server**: Supported but Linux preferred for Docker deployments

## 🔧 Software Prerequisites

### Docker Installation
Your son needs to install:
1. **Docker Engine** (version 20.10 or newer)
2. **Docker Compose** (version 2.0 or newer)

Installation commands for Ubuntu:
```bash
# Update system
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

## 🌐 Network & Firewall Configuration

### Required Ports
- **Port 80**: HTTP access (will redirect to HTTPS)
- **Port 443**: HTTPS access (recommended for production)
- **Port 3000**: Frontend application (if not using reverse proxy)
- **Port 5001**: Backend API (if not using reverse proxy)

### Firewall Rules (UFW - Ubuntu)
```bash
# Enable firewall
sudo ufw enable

# Allow SSH (important - don't lock yourself out!)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# If not using reverse proxy, allow app ports
sudo ufw allow 3000
sudo ufw allow 5001
```

## 🏢 Company Network Considerations

### Internal Access
- Determine if the app should be accessible only internally or externally
- Configure company firewall/proxy settings if needed
- Consider VPN requirements for remote access

### Domain & SSL
- **Domain Name**: Decide on internal domain (e.g., shifts.company.com)
- **SSL Certificate**: Obtain SSL certificate for HTTPS (Let's Encrypt recommended)
- **DNS Configuration**: Point domain to server IP address

## 📁 Directory Structure on Server

Recommended server directory layout:
```
/opt/shift-roster/
├── app/                    # Application files
├── data/                   # Persistent data
│   ├── database/          # SQLite database files
│   └── uploads/           # File uploads
├── backups/               # Database backups
├── logs/                  # Application logs
└── ssl/                   # SSL certificates
```

## 🔐 Security Requirements

### User Accounts
- Create dedicated user for the application (not root)
- Use SSH key authentication instead of passwords
- Disable root SSH login

### File Permissions
```bash
# Create app user
sudo useradd -m -s /bin/bash shiftapp
sudo mkdir -p /opt/shift-roster
sudo chown -R shiftapp:shiftapp /opt/shift-roster
```

### Regular Updates
- Keep system packages updated
- Monitor Docker security updates
- Implement automated security patches

## 📊 Monitoring & Logging

### System Monitoring
- Monitor disk space (database will grow over time)
- Monitor memory usage
- Monitor CPU utilization
- Set up alerts for system issues

### Application Logs
- Docker container logs: `docker-compose logs`
- System logs: `/var/log/syslog`
- Application logs: `/opt/shift-roster/logs/`

## 🔄 Backup Strategy

### What to Backup
1. **Database**: `/opt/shift-roster/data/database/`
2. **Uploads**: `/opt/shift-roster/data/uploads/`
3. **Configuration**: Docker compose files and environment variables

### Backup Schedule
- **Daily**: Automated database backups
- **Weekly**: Full system backup including uploads
- **Monthly**: Archive old backups

## 🌐 Reverse Proxy (Recommended)

Consider using Nginx as reverse proxy:
- Handles SSL termination
- Load balancing (if scaling later)
- Better security
- Standard web server ports (80/443)

## 📞 Contact Information for Deployment

**Primary Contact**: [Your Name]
**Email**: [Your Email]
**Phone**: [Your Phone]

**Technical Support**:
- For Docker issues: Check Docker documentation
- For application issues: Contact primary contact
- For server issues: Contact company IT department

## 🚨 Emergency Procedures

### If Application Goes Down
1. Check Docker containers: `docker-compose ps`
2. Check logs: `docker-compose logs`
3. Restart services: `docker-compose restart`
4. Contact primary contact if issues persist

### If Server Goes Down
1. Check system status and resources
2. Restart server if needed
3. Verify all services start automatically
4. Contact company IT if hardware issues

---

**Note**: This document should be reviewed with your son and the company's IT department to ensure all requirements and security policies are met.