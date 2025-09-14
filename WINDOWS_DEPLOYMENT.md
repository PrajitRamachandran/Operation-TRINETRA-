# Convoy Routing System - Windows Deployment Guide

Since you're on Windows, here are the Windows-specific deployment instructions:

## Prerequisites for Windows

### 1. Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop/
- Install and restart your computer
- Ensure Docker Desktop is running

### 2. Install Git (if not already installed)
- Download from: https://git-scm.com/download/win
- Or use Windows Subsystem for Linux (WSL)

## Windows Deployment Steps

### Option 1: Using PowerShell/Command Prompt

```powershell
# Navigate to your project directory
cd "C:\Users\nagal\OneDrive\Pictures\TVS HACKATHON"

# Copy environment template
copy env.example .env

# Edit .env file with your settings
notepad .env
```

### Option 2: Using Git Bash or WSL
```bash
# Navigate to project directory
cd "/c/Users/nagal/OneDrive/Pictures/TVS HACKATHON"

# Copy environment template
cp env.example .env

# Edit environment file
nano .env
```

## Deploy Using Docker Compose

### 1. Start Services
```powershell
# In PowerShell or Command Prompt
docker-compose up --build -d
```

### 2. Check Status
```powershell
# View running containers
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access Application
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Windows Management Commands

### Start Services
```powershell
docker-compose up -d
```

### Stop Services
```powershell
docker-compose down
```

### View Logs
```powershell
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mysql
```

### Restart Services
```powershell
docker-compose restart
```

### Update Services
```powershell
docker-compose down
docker-compose up --build -d
```

### Backup Database
```powershell
docker-compose exec mysql mysqldump -u root -p convoy_routing > backup.sql
```

### Access Database Shell
```powershell
docker-compose exec mysql mysql -u root -p convoy_routing
```

## Environment Configuration for Windows

Create a `.env` file with these settings:

```env
# Database Configuration
MYSQL_ROOT_PASSWORD=convoy_root_pass_2024
MYSQL_DATABASE=convoy_routing
MYSQL_USER=convoy_user
MYSQL_PASSWORD=convoy_secure_pass_2024

# Backend Configuration
DATABASE_URL=mysql+pymysql://convoy_user:convoy_secure_pass_2024@mysql:3306/convoy_routing
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Production Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

## Troubleshooting on Windows

### Docker Desktop Not Starting
1. Check Windows features: Enable "Hyper-V" and "Windows Subsystem for Linux"
2. Restart Docker Desktop
3. Check if virtualization is enabled in BIOS

### Port Already in Use
```powershell
# Check what's using port 80
netstat -ano | findstr :80

# Kill process using port 80 (replace PID)
taskkill /PID <process_id> /F
```

### Permission Issues
- Run PowerShell as Administrator
- Check Docker Desktop settings for shared drives

### Memory Issues
- Increase Docker Desktop memory allocation
- Close unnecessary applications

## Quick Start Script for Windows

Create a `deploy.bat` file:

```batch
@echo off
echo Starting Convoy Routing System Deployment...

REM Copy environment file if it doesn't exist
if not exist .env (
    copy env.example .env
    echo Please edit .env file with your settings
    pause
)

REM Start services
echo Building and starting services...
docker-compose up --build -d

REM Wait for services
echo Waiting for services to start...
timeout /t 30

REM Check status
echo Checking service status...
docker-compose ps

echo.
echo Deployment complete!
echo Frontend: http://localhost
echo Backend: http://localhost:8000
echo.
pause
```

Run it with: `deploy.bat`

## Production Considerations for Windows

### Security
- Use Windows Firewall to restrict access
- Enable Windows Defender real-time protection
- Regular Windows updates

### Performance
- Allocate sufficient RAM to Docker Desktop (4GB+)
- Use SSD storage for better performance
- Close unnecessary Windows services

### Backup
- Use Windows Task Scheduler for automated backups
- Store backups on external drives or cloud storage
- Test restore procedures regularly

---

**Ready to deploy on Windows! 🚀**
