# Docker Deployment Guide

This guide explains how to deploy the Employee Shift Roster App using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- Git (to clone the repository)

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/WNVissie/BurgundyShifts.git
   cd BurgundyShifts
   ```

2. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001
   - Backend Health Check: http://localhost:5001/health

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in `shift-roster-backend/` directory:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///src/database/app.db
```

### Frontend Environment Variables

Create a `.env` file in `shift-roster-frontend/` directory:

```env
VITE_API_URL=http://localhost:5001/api
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## Production Deployment

### Using Docker Compose (Recommended)

1. **Update docker-compose.yml for production**:
   ```yaml
   version: '3.8'
   services:
     backend:
       build: ./shift-roster-backend
       ports:
         - "5001:5001"
       environment:
         - FLASK_ENV=production
       volumes:
         - ./data/database:/app/src/database
         - ./data/uploads:/app/src/static/uploads
       restart: always
     
     frontend:
       build: ./shift-roster-frontend
       ports:
         - "80:3000"  # Use port 80 for production
       depends_on:
         - backend
       restart: always
   ```

2. **Start in production mode**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Individual Container Deployment

#### Backend Only
```bash
cd shift-roster-backend
docker build -t shift-roster-backend .
docker run -d -p 5001:5001 \
  -v $(pwd)/src/database:/app/src/database \
  -v $(pwd)/src/static/uploads:/app/src/static/uploads \
  shift-roster-backend
```

#### Frontend Only
```bash
cd shift-roster-frontend
docker build -t shift-roster-frontend .
docker run -d -p 3000:3000 shift-roster-frontend
```

## Development with Docker

For development with hot reloading:

1. **Backend development**:
   ```bash
   cd shift-roster-backend
   docker build -t shift-roster-backend-dev -f Dockerfile.dev .
   docker run -p 5001:5001 -v $(pwd):/app shift-roster-backend-dev
   ```

2. **Frontend development**:
   ```bash
   cd shift-roster-frontend
   docker run -p 3000:3000 -v $(pwd):/app node:18-alpine sh -c "npm install && npm run dev"
   ```

## Database Setup

The SQLite database will be automatically created when the backend starts. To initialize with sample data:

1. **Access the backend container**:
   ```bash
   docker-compose exec backend bash
   ```

2. **Run database migrations**:
   ```bash
   python create_notifications_table.py
   python migrate_user_auth_fields.py
   ```

## Volumes and Data Persistence

- **Database**: `./shift-roster-backend/src/database` is mounted to persist SQLite data
- **Uploads**: `./shift-roster-backend/src/static/uploads` is mounted to persist file uploads
- **Logs**: Application logs are written to stdout and can be viewed with `docker-compose logs`

## Monitoring and Logs

- **View all logs**: `docker-compose logs -f`
- **View backend logs**: `docker-compose logs -f backend`
- **View frontend logs**: `docker-compose logs -f frontend`

## Scaling

To scale the application:

```bash
# Scale backend to 3 instances
docker-compose up --scale backend=3

# Use a load balancer (nginx) in front of the backend
```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   docker-compose down
   # Change ports in docker-compose.yml
   docker-compose up
   ```

2. **Database connection issues**:
   - Check if database directory exists and is writable
   - Verify database file permissions

3. **Frontend can't connect to backend**:
   - Check VITE_API_URL environment variable
   - Ensure backend is running and accessible

4. **Build failures**:
   ```bash
   # Clean build
   docker-compose down --volumes --remove-orphans
   docker-compose build --no-cache
   docker-compose up
   ```

### Health Checks

Check service health:
```bash
# Backend health
curl http://localhost:5001/health

# Frontend health
curl http://localhost:3000
```

## Security Considerations

1. **Production secrets**: Never commit `.env` files with production secrets
2. **Database security**: Use proper database permissions in production
3. **HTTPS**: Use reverse proxy (nginx) with SSL certificates for production
4. **Firewall**: Configure appropriate firewall rules

## Backup and Recovery

```bash
# Backup database
cp shift-roster-backend/src/database/app.db backup/app-$(date +%Y%m%d).db

# Backup uploads
tar -czf backup/uploads-$(date +%Y%m%d).tar.gz shift-roster-backend/src/static/uploads/
```

## Updates and Maintenance

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
# Docker Deployment Guide

This guide explains how to deploy the Employee Shift Roster App using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- Git (to clone the repository)

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/WNVissie/BurgundyShifts.git
   cd BurgundyShifts
   ```

2. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001
   - Backend Health Check: http://localhost:5001/health

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in `shift-roster-backend/` directory:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///src/database/app.db
```

### Frontend Environment Variables

Create a `.env` file in `shift-roster-frontend/` directory:

```env
VITE_API_URL=http://localhost:5001/api
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## Production Deployment

### Using Docker Compose (Recommended)

1. **Update docker-compose.yml for production**:
   ```yaml
   version: '3.8'
   services:
     backend:
       build: ./shift-roster-backend
       ports:
         - "5001:5001"
       environment:
         - FLASK_ENV=production
       volumes:
         - ./data/database:/app/src/database
         - ./data/uploads:/app/src/static/uploads
       restart: always
     
     frontend:
       build: ./shift-roster-frontend
       ports:
         - "80:3000"  # Use port 80 for production
       depends_on:
         - backend
       restart: always
   ```

2. **Start in production mode**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Individual Container Deployment

#### Backend Only
```bash
cd shift-roster-backend
docker build -t shift-roster-backend .
docker run -d -p 5001:5001 \
  -v $(pwd)/src/database:/app/src/database \
  -v $(pwd)/src/static/uploads:/app/src/static/uploads \
  shift-roster-backend
```

#### Frontend Only
```bash
cd shift-roster-frontend
docker build -t shift-roster-frontend .
docker run -d -p 3000:3000 shift-roster-frontend
```

## Development with Docker

For development with hot reloading:

1. **Backend development**:
   ```bash
   cd shift-roster-backend
   docker build -t shift-roster-backend-dev -f Dockerfile.dev .
   docker run -p 5001:5001 -v $(pwd):/app shift-roster-backend-dev
   ```

2. **Frontend development**:
   ```bash
   cd shift-roster-frontend
   docker run -p 3000:3000 -v $(pwd):/app node:18-alpine sh -c "npm install && npm run dev"
   ```

## Database Setup

The SQLite database will be automatically created when the backend starts. To initialize with sample data:

1. **Access the backend container**:
   ```bash
   docker-compose exec backend bash
   ```

2. **Run database migrations**:
   ```bash
   python create_notifications_table.py
   python migrate_user_auth_fields.py
   ```

## Volumes and Data Persistence

- **Database**: `./shift-roster-backend/src/database` is mounted to persist SQLite data
- **Uploads**: `./shift-roster-backend/src/static/uploads` is mounted to persist file uploads
- **Logs**: Application logs are written to stdout and can be viewed with `docker-compose logs`

## Monitoring and Logs

- **View all logs**: `docker-compose logs -f`
- **View backend logs**: `docker-compose logs -f backend`
- **View frontend logs**: `docker-compose logs -f frontend`

## Scaling

To scale the application:

```bash
# Scale backend to 3 instances
docker-compose up --scale backend=3

# Use a load balancer (nginx) in front of the backend
```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   docker-compose down
   # Change ports in docker-compose.yml
   docker-compose up
   ```

2. **Database connection issues**:
   - Check if database directory exists and is writable
   - Verify database file permissions

3. **Frontend can't connect to backend**:
   - Check VITE_API_URL environment variable
   - Ensure backend is running and accessible

4. **Build failures**:
   ```bash
   # Clean build
   docker-compose down --volumes --remove-orphans
   docker-compose build --no-cache
   docker-compose up
   ```

### Health Checks

Check service health:
```bash
# Backend health
curl http://localhost:5001/health

# Frontend health
curl http://localhost:3000
```

## Security Considerations

1. **Production secrets**: Never commit `.env` files with production secrets
2. **Database security**: Use proper database permissions in production
3. **HTTPS**: Use reverse proxy (nginx) with SSL certificates for production
4. **Firewall**: Configure appropriate firewall rules

## Backup and Recovery

```bash
# Backup database
cp shift-roster-backend/src/database/app.db backup/app-$(date +%Y%m%d).db

# Backup uploads
tar -czf backup/uploads-$(date +%Y%m%d).tar.gz shift-roster-backend/src/static/uploads/
```

## Updates and Maintenance

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```