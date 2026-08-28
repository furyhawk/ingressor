# Deployment Guide

This guide covers various deployment options for the Marker PDF Converter Reflex application.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Setup](#production-setup)

---

## Local Development

### Standard Setup

```bash
# Clone and setup
git clone <repo-url>
cd reflex-framework-rebuild

# Install dependencies
uv sync

# Run development server
reflex run
```

### Development with Hot Reload

```bash
# Run with file watching
reflex run --env dev

# Or using make
make dev
```

---

## Docker Deployment

### Building Docker Image

```bash
# Build image
docker build -t marker-converter:latest .

# Or with docker-compose
docker-compose build
```

### Running with Docker

```bash
# Run container
docker run -p 3000:3000 marker-converter:latest

# With docker-compose
docker-compose up

# Run in detached mode
docker-compose up -d

# Stop container
docker-compose down
```

### Docker Configuration

The provided `docker-compose.yml` includes:
- ✅ Port mapping (3000 for UI, 8000 for API)
- ✅ Volume mounts for uploads/outputs
- ✅ Shared memory (2GB) for ML models
- ✅ Network isolation

### Environment Variables in Docker

Create `.env` file:

```bash
cp .env.example .env
# Edit .env as needed
docker-compose up
```

---

## Cloud Deployment

### 1. Heroku Deployment

```bash
# Create Heroku app
heroku create marker-converter

# Add Procfile
echo "web: reflex run --env prod" > Procfile

# Add runtime.txt
echo "python-3.11.6" > runtime.txt

# Deploy
git push heroku main
```

**Note**: Heroku free tier may not have enough memory for ML models.

### 2. AWS Deployment

#### Using EC2

1. Launch EC2 instance (at least t3.large)
2. Connect and run:

```bash
# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv curl git

# Clone and setup
git clone <repo-url>
cd reflex-framework-rebuild

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install and run
pip install -e .
reflex run --env prod --host 0.0.0.0
```

#### Using ECS with Docker

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag marker-converter:latest <account>.dkr.ecr.us-east-1.amazonaws.com/marker-converter:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/marker-converter:latest

# Create ECS task definition and service
# (See AWS documentation for detailed steps)
```

### 3. DigitalOcean Deployment

```bash
# 1. Create Droplet (at least 4GB RAM)
# 2. SSH into droplet
# 3. Run setup script:

curl -O https://raw.githubusercontent.com/your-repo/setup.sh
bash setup.sh

# 4. Use systemd service (see below)
```

### 4. Railway Deployment

```bash
# 1. Connect GitHub repo to Railway
# 2. Add environment variables
# 3. Railway auto-deploys on push
```

### 5. Render Deployment

```bash
# Add render.yaml

services:
  - type: web
    name: marker-converter
    env: python
    plan: standard
    buildCommand: "pip install -e ."
    startCommand: "reflex run --env prod --host 0.0.0.0"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

---

## Production Setup

### 1. Using Systemd (Linux)

Create `/etc/systemd/system/marker-converter.service`:

```ini
[Unit]
Description=Marker PDF Converter
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/marker-converter
Environment="PATH=/opt/marker-converter/venv/bin"
ExecStart=/opt/marker-converter/venv/bin/reflex run --env prod --host 0.0.0.0 --port 3000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable marker-converter
sudo systemctl start marker-converter
sudo systemctl status marker-converter
```

### 2. Nginx Reverse Proxy

```nginx
upstream marker_app {
    server localhost:3000;
}

server {
    listen 80;
    server_name marker.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name marker.example.com;

    ssl_certificate /etc/letsencrypt/live/marker.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marker.example.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    client_max_body_size 100M;

    location / {
        proxy_pass http://marker_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d marker.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 4. Resource Optimization

#### Memory Management

```bash
# Check memory usage
free -h
docker stats

# Limit container memory
docker-compose yml update:
# services:
#   marker-converter:
#     deploy:
#       resources:
#         limits:
#           memory: 4G
#         reservations:
#           memory: 2G
```

#### Process Management

```bash
# Use gunicorn for production
pip install gunicorn uvicorn

# Run with gunicorn
gunicorn reflex_app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### 5. Database Backup (if added)

```bash
# Backup strategy
0 2 * * * /opt/marker-converter/backup.sh

# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /backups/marker-$DATE.tar.gz /opt/marker-converter
find /backups -name "marker-*.tar.gz" -mtime +30 -delete
```

---

## Monitoring & Logging

### Using Prometheus & Grafana

```bash
# Add monitoring dependencies
pip install prometheus-client

# Configure in reflex_app.py
from prometheus_client import Counter, Histogram

conversion_count = Counter('conversions_total', 'Total conversions')
conversion_time = Histogram('conversion_seconds', 'Conversion time')
```

### Logging

```bash
# Use structured logging
pip install python-json-logger

# Configure logging in reflex_app.py
import logging
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Log Rotation

```bash
# /etc/logrotate.d/marker-converter
/opt/marker-converter/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 644 www-data www-data
}
```

---

## Performance Tuning

### 1. Enable Caching

```python
# In reflex_app.py
class MarkerState(rx.State):
    model_dict: Dict[str, Any] = {}  # Persistent across requests
    models_loaded: bool = False
```

### 2. Batch Processing Queue

Consider adding a task queue for long-running conversions:

```bash
pip install celery redis
```

### 3. Load Balancing

```nginx
upstream marker_backend {
    server marker1:3000;
    server marker2:3000;
    server marker3:3000;
}

server {
    location / {
        proxy_pass http://marker_backend;
    }
}
```

---

## Security Checklist

- ✅ Use HTTPS/SSL (Let's Encrypt)
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ File upload validation
- ✅ Input sanitization
- ✅ Regular security updates
- ✅ Firewall rules
- ✅ Monitor logs for suspicious activity
- ✅ Regular backups

---

## Troubleshooting Deployment

### Issue: Port already in use
```bash
# Find and kill process
lsof -i :3000
kill -9 <PID>
```

### Issue: Out of memory
```bash
# Increase swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: Models not loading in container
```bash
# Pre-download models
docker run -it marker-converter:latest python -c "from marker.models import create_model_dict; create_model_dict()"
```

### Issue: WebSocket connection fails
```bash
# Check proxy configuration
# Ensure Upgrade headers are passed through
# Check firewall for port 443
```

---

## Cost Optimization

### AWS
- Use S3 for file storage
- Use CloudFront for caching
- Use spot instances for non-critical workloads
- Set up auto-scaling

### DigitalOcean
- Use shared CPU droplets for development
- Combine with managed databases
- Use spaces for file storage

### General
- Monitor resource usage
- Scale down during off-peak hours
- Use CDN for static assets
- Implement file retention policies

---

## Maintenance

### Regular Tasks

```bash
# Update dependencies
pip install --upgrade -e .

# Check for security vulnerabilities
pip-audit

# Clean up old conversions
find /app/uploads -mtime +7 -delete

# Monitor disk space
df -h
du -sh *
```

### Backup Strategy

- Daily backup of configuration
- Weekly backup of application
- Monthly full backup including logs
- Store off-site backups

---

## Getting Help

- Check application logs: `docker logs marker-converter`
- Check system logs: `journalctl -u marker-converter`
- Monitor resources: `top`, `htop`, `docker stats`
- Check Reflex documentation: https://reflex.dev/docs/deployment

---

**For production deployments, consider consulting with DevOps/infrastructure team.**
