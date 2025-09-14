#!/bin/bash

# Convoy Routing System Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

echo "🚀 Starting Convoy Routing System Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
        print_warning "Please edit .env file with your production values before continuing."
        print_warning "Especially change the SECRET_KEY and database passwords!"
        read -p "Press Enter after updating .env file..."
    fi
    print_status "Environment configuration found ✓"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start services
    docker-compose up --build -d
    
    print_status "Services started ✓"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for MySQL
    print_status "Waiting for MySQL..."
    timeout=60
    while ! docker-compose exec mysql mysqladmin ping -h localhost --silent; do
        sleep 2
        timeout=$((timeout - 2))
        if [ $timeout -le 0 ]; then
            print_error "MySQL failed to start within 60 seconds"
            exit 1
        fi
    done
    print_status "MySQL is ready ✓"
    
    # Wait for backend
    print_status "Waiting for backend API..."
    timeout=60
    while ! curl -f http://localhost:8000/ >/dev/null 2>&1; do
        sleep 2
        timeout=$((timeout - 2))
        if [ $timeout -le 0 ]; then
            print_error "Backend API failed to start within 60 seconds"
            exit 1
        fi
    done
    print_status "Backend API is ready ✓"
    
    # Wait for frontend
    print_status "Waiting for frontend..."
    timeout=30
    while ! curl -f http://localhost/ >/dev/null 2>&1; do
        sleep 2
        timeout=$((timeout - 2))
        if [ $timeout -le 0 ]; then
            print_error "Frontend failed to start within 30 seconds"
            exit 1
        fi
    done
    print_status "Frontend is ready ✓"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    # Run database migrations/initialization
    docker-compose exec backend python -c "
from app.db.database import engine, Base
from app.db import models
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
    
    print_status "Database initialized ✓"
}

# Show deployment status
show_status() {
    echo ""
    print_status "🎉 Deployment completed successfully!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 Useful Commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo "   Update services: docker-compose up --build -d"
    echo ""
}

# Main deployment process
main() {
    print_status "Starting deployment process..."
    
    check_docker
    check_env
    deploy_services
    wait_for_services
    init_database
    show_status
}

# Run main function
main "$@"
