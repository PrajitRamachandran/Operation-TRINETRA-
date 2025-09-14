# Convoy Routing System - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 80, 443, and 8000 available

### 1. Clone and Setup
```bash
# Clone your repository
git clone <your-repo-url>
cd convoy-routing-system

# Copy environment template
cp env.example .env

# Edit .env with your production values
nano .env
```

### 2. Deploy
```bash
# Run the deployment script
./deploy.sh
```

### 3. Access Your Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Environment Configuration

### Required Environment Variables
```bash
# Database
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_DATABASE=convoy_routing
MYSQL_USER=convoy_user
MYSQL_PASSWORD=your_secure_password

# Backend
SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
DATABASE_URL=mysql+pymysql://convoy_user:your_secure_password@mysql:3306/convoy_routing
```

### Security Notes
- **CHANGE DEFAULT PASSWORDS** before production deployment
- Use a strong SECRET_KEY (minimum 32 characters)
- Consider using environment-specific configurations

## 🛠️ Management Commands

Use the `manage.sh` script for common operations:

```bash
# Start services
./manage.sh start

# Stop services
./manage.sh stop

# View status
./manage.sh status

# View logs
./manage.sh logs

# Follow logs in real-time
./manage.sh logs-f

# Update services
./manage.sh update

# Backup database
./manage.sh backup

# Health check
./manage.sh health
```

## 🏗️ Architecture

### Services
- **Frontend**: Nginx serving static files and proxying API requests
- **Backend**: FastAPI application with Python 3.11
- **Database**: MySQL 8.0 with persistent storage

### Network
- All services communicate through Docker network
- Frontend accessible on port 80/443
- Backend API accessible on port 8000
- Database accessible on port 3306 (internal only)

## 🔧 Customization

### Adding SSL/HTTPS
1. Place your SSL certificates in `./ssl/` directory
2. Uncomment HTTPS server block in `Front-End/nginx.conf`
3. Update domain name in configuration

### Scaling Backend
Edit `docker-compose.yml`:
```yaml
backend:
  # ... existing config
  deploy:
    replicas: 3  # Run 3 backend instances
```

### Custom Domains
1. Update `CORS_ORIGINS` in `.env`
2. Update `server_name` in `Front-End/nginx.conf`
3. Configure DNS to point to your server

## 📊 Monitoring

### Health Checks
- Backend: `curl http://localhost:8000/`
- Frontend: `curl http://localhost/`
- Database: Built into Docker health checks

### Logs
- Application logs: `docker-compose logs backend`
- Web server logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs mysql`

### Performance
- Monitor resource usage: `./manage.sh status`
- Check service health: `./manage.sh health`

## 🚨 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check logs
./manage.sh logs

# Check Docker status
docker ps -a

# Restart services
./manage.sh restart
```

#### Database Connection Issues
```bash
# Check database status
./manage.sh db-shell

# Verify environment variables
docker-compose exec backend env | grep DATABASE
```

#### Frontend Not Loading
```bash
# Check Nginx configuration
docker-compose exec frontend nginx -t

# Restart frontend
docker-compose restart frontend
```

### Performance Issues
- Increase Docker memory allocation
- Check disk space: `df -h`
- Monitor CPU usage: `htop`

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull

# Update services
./manage.sh update
```

### Database Maintenance
```bash
# Backup before updates
./manage.sh backup

# Access database
./manage.sh db-shell
```

### Cleanup
```bash
# Remove old containers and images
./manage.sh clean
```

## 🛡️ Security Considerations

### Production Deployment
1. **Change all default passwords**
2. **Use strong SECRET_KEY**
3. **Enable HTTPS with valid certificates**
4. **Configure firewall rules**
5. **Regular security updates**
6. **Monitor access logs**

### Network Security
- Database is not exposed externally
- API rate limiting configured
- Security headers enabled
- CORS properly configured

## 📞 Support

For issues or questions:
1. Check logs: `./manage.sh logs`
2. Run health check: `./manage.sh health`
3. Review this documentation
4. Check Docker and system resources

---

**Happy Deploying! 🎉**
