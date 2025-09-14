# Convoy Routing System - Production Deployment Checklist

## Pre-Deployment Checklist

### ✅ Environment Setup
- [ ] Docker and Docker Compose installed
- [ ] At least 4GB RAM available
- [ ] Ports 80, 443, 8000 available
- [ ] Sufficient disk space (at least 10GB)

### ✅ Security Configuration
- [ ] Changed default MySQL root password
- [ ] Changed default MySQL user password
- [ ] Set strong SECRET_KEY (minimum 32 characters)
- [ ] Updated CORS_ORIGINS with production domains
- [ ] Configured ALLOWED_HOSTS properly

### ✅ SSL/HTTPS Setup (Recommended)
- [ ] Obtained SSL certificates
- [ ] Placed certificates in `./ssl/` directory
- [ ] Updated nginx.conf with HTTPS configuration
- [ ] Updated CORS_ORIGINS to use HTTPS

### ✅ Domain Configuration
- [ ] DNS records pointing to server
- [ ] Domain name updated in nginx.conf
- [ ] Domain name updated in .env file

## Deployment Steps

### 1. Initial Setup
```bash
# Clone repository
git clone <your-repo-url>
cd convoy-routing-system

# Copy environment template
cp env.example .env

# Edit environment variables
nano .env
```

### 2. Deploy Services
```bash
# Make scripts executable (Linux/Mac)
chmod +x deploy.sh manage.sh

# Run deployment
./deploy.sh
```

### 3. Verify Deployment
```bash
# Check service status
./manage.sh status

# Run health check
./manage.sh health

# Test endpoints
curl http://localhost/
curl http://localhost:8000/
```

## Post-Deployment Tasks

### ✅ Verification
- [ ] Frontend loads correctly
- [ ] Backend API responds
- [ ] Database connection working
- [ ] Login functionality works
- [ ] Maps display properly
- [ ] All navigation links work

### ✅ Monitoring Setup
- [ ] Log monitoring configured
- [ ] Resource usage monitoring
- [ ] Backup schedule established
- [ ] Health check automation

### ✅ Security Hardening
- [ ] Firewall rules configured
- [ ] Regular security updates scheduled
- [ ] Access logs monitored
- [ ] Backup encryption enabled

## Production Environment Variables

### Required Variables
```bash
# Database
MYSQL_ROOT_PASSWORD=<strong_password>
MYSQL_DATABASE=convoy_routing
MYSQL_USER=convoy_user
MYSQL_PASSWORD=<strong_password>

# Backend
SECRET_KEY=<32+_character_random_string>
DATABASE_URL=mysql+pymysql://convoy_user:<password>@mysql:3306/convoy_routing
ENVIRONMENT=production
DEBUG=false

# Security
CORS_ORIGINS=["https://your-domain.com"]
ALLOWED_HOSTS=["your-domain.com", "www.your-domain.com"]
```

### Optional Variables
```bash
# External APIs
WEATHER_API_KEY=<your_weather_api_key>
MAPS_API_KEY=<your_maps_api_key>

# Monitoring
SENTRY_DSN=<your_sentry_dsn>
PROMETHEUS_ENABLED=true
```

## Scaling Considerations

### Horizontal Scaling
- Multiple backend instances
- Load balancer configuration
- Database read replicas
- CDN for static assets

### Vertical Scaling
- Increase container memory limits
- Optimize database configuration
- Enable query caching
- Implement connection pooling

## Backup Strategy

### Database Backups
```bash
# Daily automated backup
./manage.sh backup

# Manual backup
docker-compose exec mysql mysqldump -u root -p convoy_routing > backup_$(date +%Y%m%d).sql
```

### Application Backups
- Configuration files
- SSL certificates
- Custom modifications
- Environment files

## Maintenance Schedule

### Daily
- [ ] Check service health
- [ ] Monitor resource usage
- [ ] Review error logs

### Weekly
- [ ] Database backup verification
- [ ] Security updates check
- [ ] Performance metrics review

### Monthly
- [ ] Full system backup
- [ ] Security audit
- [ ] Dependency updates
- [ ] Capacity planning review

## Troubleshooting Guide

### Service Won't Start
1. Check Docker status: `docker ps -a`
2. Review logs: `./manage.sh logs`
3. Verify environment variables
4. Check port availability

### Database Issues
1. Check MySQL logs: `docker-compose logs mysql`
2. Verify connection string
3. Check disk space
4. Test database connectivity

### Frontend Issues
1. Check Nginx configuration: `docker-compose exec frontend nginx -t`
2. Verify static file serving
3. Check browser console errors
4. Test API connectivity

### Performance Issues
1. Monitor resource usage: `./manage.sh status`
2. Check database query performance
3. Review application logs
4. Consider scaling options

## Emergency Procedures

### Service Recovery
```bash
# Stop all services
./manage.sh stop

# Clean restart
docker-compose down
docker-compose up -d

# Check health
./manage.sh health
```

### Database Recovery
```bash
# Restore from backup
./manage.sh restore backup_file.sql

# Verify data integrity
./manage.sh db-shell
```

### Rollback Procedure
```bash
# Stop current version
./manage.sh stop

# Deploy previous version
git checkout <previous_commit>
./manage.sh update
```

---

**Remember**: Always test deployments in a staging environment before production!
