#!/bin/bash

# Convoy Routing System Management Script
# Provides easy commands for managing the deployed system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[CONVOY]${NC} $1"
}

# Show help
show_help() {
    echo "Convoy Routing System Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs        Show service logs"
    echo "  logs-f      Follow service logs"
    echo "  update      Update and restart services"
    echo "  backup      Backup database"
    echo "  restore     Restore database from backup"
    echo "  shell       Open shell in backend container"
    echo "  db-shell    Open MySQL shell"
    echo "  clean       Clean up containers and volumes"
    echo "  health      Check service health"
    echo "  help        Show this help message"
}

# Start services
start_services() {
    print_header "Starting Convoy Routing System..."
    docker-compose up -d
    print_status "Services started"
}

# Stop services
stop_services() {
    print_header "Stopping Convoy Routing System..."
    docker-compose down
    print_status "Services stopped"
}

# Restart services
restart_services() {
    print_header "Restarting Convoy Routing System..."
    docker-compose restart
    print_status "Services restarted"
}

# Show status
show_status() {
    print_header "Service Status"
    docker-compose ps
    echo ""
    print_header "Resource Usage"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Show logs
show_logs() {
    docker-compose logs --tail=100
}

# Follow logs
follow_logs() {
    docker-compose logs -f
}

# Update services
update_services() {
    print_header "Updating Convoy Routing System..."
    docker-compose down
    docker-compose up --build -d
    print_status "Services updated and restarted"
}

# Backup database
backup_database() {
    print_header "Backing up database..."
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backup_convoy_${timestamp}.sql"
    
    docker-compose exec mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD:-convoy_root_pass} convoy_routing > "$backup_file"
    print_status "Database backed up to: $backup_file"
}

# Restore database
restore_database() {
    if [ -z "$1" ]; then
        print_error "Please provide backup file path"
        echo "Usage: $0 restore <backup_file.sql>"
        exit 1
    fi
    
    print_header "Restoring database from: $1"
    docker-compose exec -T mysql mysql -u root -p${MYSQL_ROOT_PASSWORD:-convoy_root_pass} convoy_routing < "$1"
    print_status "Database restored"
}

# Open shell in backend
open_shell() {
    print_header "Opening backend shell..."
    docker-compose exec backend /bin/bash
}

# Open database shell
open_db_shell() {
    print_header "Opening MySQL shell..."
    docker-compose exec mysql mysql -u root -p${MYSQL_ROOT_PASSWORD:-convoy_root_pass} convoy_routing
}

# Clean up
clean_up() {
    print_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_header "Cleaning up..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_status "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Health check
health_check() {
    print_header "Health Check"
    
    # Check if containers are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Some services are not running"
        docker-compose ps
        exit 1
    fi
    
    # Check backend health
    if curl -f http://localhost:8000/ >/dev/null 2>&1; then
        print_status "Backend API: ✓ Healthy"
    else
        print_error "Backend API: ✗ Unhealthy"
    fi
    
    # Check frontend health
    if curl -f http://localhost/ >/dev/null 2>&1; then
        print_status "Frontend: ✓ Healthy"
    else
        print_error "Frontend: ✗ Unhealthy"
    fi
    
    # Check database health
    if docker-compose exec mysql mysqladmin ping -h localhost --silent; then
        print_status "Database: ✓ Healthy"
    else
        print_error "Database: ✗ Unhealthy"
    fi
    
    print_status "Health check completed"
}

# Main command handler
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    logs-f)
        follow_logs
        ;;
    update)
        update_services
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database "$2"
        ;;
    shell)
        open_shell
        ;;
    db-shell)
        open_db_shell
        ;;
    clean)
        clean_up
        ;;
    health)
        health_check
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
