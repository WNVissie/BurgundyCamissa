#!/bin/bash

echo "🚀 Starting Employee Shift Roster App with Docker"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ Error: Docker Compose is not installed."
    exit 1
fi

# Create data directories if they don't exist
echo "📁 Creating data directories..."
mkdir -p data/database
mkdir -p data/uploads

# Set permissions for data directories
chmod 755 data/database
chmod 755 data/uploads

echo "🔨 Building and starting containers..."

# Build and start services
docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo "✅ Application started successfully!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:5001"
    echo ""
    echo "📊 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
else
    echo "❌ Failed to start the application."
    echo "📋 Check logs: docker-compose logs"
    exit 1
fi