# Deployment Guide - Employee Shift Roster System

This guide provides detailed instructions for deploying the Employee Shift Roster application to various platforms and environments.

## 🌐 Deployment Options Overview

| Platform | Frontend | Backend | Database | Cost | Complexity |
|----------|----------|---------|----------|------|------------|
| **Local Development** | Vite Dev Server | Flask Dev Server | SQLite | Free | Low |
| **Netlify + Render** | Netlify | Render | PostgreSQL | Free Tier | Medium |
| **Vercel + Railway** | Vercel | Railway | PostgreSQL | Free Tier | Medium |
| **Heroku** | Heroku | Heroku | Heroku Postgres | Paid | Low |
| **AWS** | S3 + CloudFront | EC2/ECS | RDS | Variable | High |
| **Docker** | Docker Container | Docker Container | Docker Volume | Infrastructure Cost | Medium |

## 🚀 Quick Deployment (Recommended for POC)

### Option 1: Netlify + Render (Free Tier)

**Frontend on Netlify:**
1. Build the frontend:
```bash
cd shift-roster-frontend
npm run build
```

2. Deploy to Netlify:
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop the `dist` folder
   - Configure custom domain (optional)

**Backend on Render:**
1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Configure build settings:
   - **Build Command**: `cd shift-roster-backend && pip install -r requirements.txt`
   - **Start Command**: `cd shift-roster-backend && python src/main.py`
   - **Environment**: Python 3.11

5. Add environment variables:
```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
CORS_ORIGINS=https://your-netlify-app.netlify.app
```

### Option 2: Vercel + Railway

**Frontend on Vercel:**
1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd shift-roster-frontend
vercel --prod
```

**Backend on Railway:**
1. Create account at [railway.app](https://railway.app)
2. Connect GitHub repository
3. Deploy backend service
4. Add PostgreSQL database
5. Configure environment variables

## 🐳 Docker Deployment

### Docker Compose (Recommended)

1. **Create docker-compose.yml**:
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./shift-roster-frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build:
      context: ./shift-roster-backend
      dockerfile: Dockerfile
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/shift_roster
      - SECRET_KEY=your-secret-key
      - JWT_SECRET_KEY=your-jwt-secret
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=shift_roster
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

2. **Create Frontend Dockerfile**:
```dockerfile
# shift-roster-frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

3. **Create Backend Dockerfile**:
```dockerfile
# shift-roster-backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD ["python", "src/main.py"]
```

4. **Deploy with Docker Compose**:
```bash
docker-compose up --build -d
```

## ☁️ Cloud Platform Deployments

### AWS Deployment

**Frontend (S3 + CloudFront):**
1. Create S3 bucket for static hosting
2. Upload built frontend files
3. Configure CloudFront distribution
4. Set up custom domain with Route 53

**Backend (ECS or EC2):**
1. Create ECS cluster or EC2 instance
2. Deploy Docker container
3. Configure Application Load Balancer
4. Set up RDS PostgreSQL database

**Infrastructure as Code (Terraform):**
```hcl
# main.tf
provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "frontend" {
  bucket = "shift-roster-frontend"
}

resource "aws_ecs_cluster" "backend" {
  name = "shift-roster-backend"
}

resource "aws_db_instance" "postgres" {
  identifier = "shift-roster-db"
  engine     = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  
  db_name  = "shift_roster"
  username = "postgres"
  password = var.db_password
  
  skip_final_snapshot = true
}
```

### Google Cloud Platform

**Frontend (Cloud Storage + CDN):**
```bash
# Build and deploy frontend
cd shift-roster-frontend
npm run build
gsutil -m cp -r dist/* gs://your-bucket-name/
```

**Backend (Cloud Run):**
```bash
# Build and deploy backend
cd shift-roster-backend
gcloud builds submit --tag gcr.io/PROJECT-ID/shift-roster-backend
gcloud run deploy --image gcr.io/PROJECT-ID/shift-roster-backend --platform managed
```

### Microsoft Azure

**Frontend (Static Web Apps):**
```bash
# Deploy using Azure CLI
az staticwebapp create \
  --name shift-roster-frontend \
  --resource-group myResourceGroup \
  --source https://github.com/username/repo \
  --location "West US 2" \
  --branch main \
  --app-location "/shift-roster-frontend" \
  --output-location "dist"
```

**Backend (Container Instances):**
```bash
# Deploy backend container
az container create \
  --resource-group myResourceGroup \
  --name shift-roster-backend \
  --image your-registry/shift-roster-backend:latest \
  --dns-name-label shift-roster-api \
  --ports 5001
```

## 🔧 Production Configuration

### Environment Variables

**Backend (.env.production):**
```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-production-key

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
CORS_ORIGINS=https://your-frontend-domain.com

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Redis (Optional for caching)
REDIS_URL=redis://localhost:6379/0
```

**Frontend (vite.config.js):**
```javascript
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-select']
        }
      }
    }
  },
  define: {
    'process.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || 'http://localhost:5001')
  }
})
```

### Database Migration

**Production Database Setup:**
```sql
-- Create production database
CREATE DATABASE shift_roster_prod;
CREATE USER shift_roster_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE shift_roster_prod TO shift_roster_user;
```

**Migration Script:**
```python
# migrate_to_production.py
import os
from src.models.models import db
from src.main import create_app

def migrate_database():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Run initial data setup
        from src.init_db import create_sample_data
        create_sample_data()
        
        print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate_database()
```

### SSL/HTTPS Configuration

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        root /var/www/shift-roster-frontend;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring and Logging

### Application Monitoring

**Backend Logging:**
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/shift_roster.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

**Health Check Endpoints:**
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

@app.route('/api/health')
def api_health():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

### Performance Monitoring

**Frontend (Web Vitals):**
```javascript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to your analytics service
  console.log(metric);
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Use HTTPS for all communications
- [ ] Set secure session cookies
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for trusted domains
- [ ] Implement proper input validation
- [ ] Use parameterized database queries
- [ ] Set up proper backup procedures
- [ ] Monitor for security vulnerabilities
- [ ] Implement proper error handling (don't expose stack traces)

### Security Headers

```python
from flask_talisman import Talisman

# Add security headers
Talisman(app, force_https=True)

@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## 🚨 Troubleshooting Deployment Issues

### Common Deployment Problems

**Build Failures:**
```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Database Connection Issues:**
```python
# Test database connection
import psycopg2
try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")
```

**CORS Issues:**
```python
# Update CORS configuration
CORS(app, 
     origins=['https://your-frontend-domain.com'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

### Deployment Verification

**Automated Testing:**
```bash
#!/bin/bash
# deployment-test.sh

echo "Testing frontend deployment..."
curl -f https://your-frontend-domain.com || exit 1

echo "Testing backend health..."
curl -f https://your-api-domain.com/health || exit 1

echo "Testing API endpoints..."
curl -f https://your-api-domain.com/api/roles || exit 1

echo "All tests passed! Deployment successful."
```

## 📈 Scaling Considerations

### Horizontal Scaling

**Load Balancer Configuration:**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    build: ./shift-roster-backend
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/shift_roster
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

**Database Optimization:**
```sql
-- Add indexes for better performance
CREATE INDEX idx_employee_role ON employees(role_id);
CREATE INDEX idx_roster_date ON roster(date);
CREATE INDEX idx_roster_employee ON roster(employee_id);
CREATE INDEX idx_timesheet_date ON timesheets(date);
```

This deployment guide provides comprehensive instructions for deploying the Employee Shift Roster application across various platforms and environments, from simple POC deployments to production-ready scalable solutions.

