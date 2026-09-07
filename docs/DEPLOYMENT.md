# Unividown Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose 2+
- Domain name with DNS pointing to server
- SSL certificates (Let's Encrypt recommended)
- Minimum 2GB RAM, 2 CPU cores
- 10GB+ disk space for media storage

---

## Quick Start (Development)

```bash
# Clone repository
git clone https://github.com/your-org/unividown.git
cd unividown

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access at http://localhost:3000
```

---

## Production Deployment

### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose (if not included)
sudo apt install docker-compose-plugin
```

### 2. Configure Environment

```bash
# Create .env file
cat > .env << EOF
NODE_ENV=production
WORKER_URL=http://worker:8000
PYTHON_ENV=production
DATABASE_URL=sqlite:////app/data/unividown.db
REDIS_URL=redis://redis:6379
MAX_FILE_SIZE=10737418240
EOF
```

### 3. SSL Certificates

**Option A: Let's Encrypt (Recommended)**

```bash
# Install certbot
sudo apt install certbot

# Get certificates
sudo certbot certonly --standalone -d your-domain.com

# Copy to nginx ssl directory
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
sudo chown -R $USER:$USER nginx/ssl

# Set up auto-renewal
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/* /path/to/unividown/nginx/ssl/ && docker-compose restart nginx
```

**Option B: Self-signed (Development/Testing)**

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048   -keyout nginx/ssl/privkey.pem   -out nginx/ssl/fullchain.pem   -subj "/CN=localhost"
```

### 4. Deploy

```bash
# Build and start production stack
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs -f
```

### 5. Verify Deployment

```bash
# Health checks
curl -k https://your-domain.com/api/health
curl -k https://your-domain.com/metrics

# Web interface
open https://your-domain.com
```

---

## Docker Images

### Pre-built Images (GHCR)

```bash
# Pull latest
docker pull ghcr.io/your-org/unividown-web:latest
docker pull ghcr.io/your-org/unividown-worker:latest

# Run with pre-built images
docker-compose -f docker-compose.prod.yml up -d
```

### Multi-arch Builds

```bash
# Build for multiple architectures
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64   -t ghcr.io/your-org/unividown-web:latest   -f docker/Dockerfile.web . --push
```

---

## Kubernetes Deployment

### Namespace & Config

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: unividown
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: unividown-config
  namespace: unividown
data:
  NODE_ENV: "production"
  WORKER_URL: "http://unividown-worker:8000"
  PYTHON_ENV: "production"
  DATABASE_URL: "sqlite:////app/data/unividown.db"
  REDIS_URL: "redis://unividown-redis:6379"
```

### Deployments

```yaml
# k8s/web-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unividown-web
  namespace: unividown
spec:
  replicas: 2
  selector:
    matchLabels:
      app: unividown-web
  template:
    metadata:
      labels:
        app: unividown-web
    spec:
      containers:
      - name: web
        image: ghcr.io/your-org/unividown-web:latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: unividown-config
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: unividown-data
---
# k8s/worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unividown-worker
  namespace: unividown
spec:
  replicas: 1
  selector:
    matchLabels:
      app: unividown-worker
  template:
    metadata:
      labels:
        app: unividown-worker
    spec:
      containers:
      - name: worker
        image: ghcr.io/your-org/unividown-worker:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: unividown-config
        resources:
          limits:
            memory: "2Gi"
            cpu: "2000m"
          requests:
            memory: "1Gi"
            cpu: "1000m"
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: unividown-data
```

### Services & Ingress

```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: unividown-web
  namespace: unividown
spec:
  selector:
    app: unividown-web
  ports:
  - port: 80
    targetPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: unividown-worker
  namespace: unividown
spec:
  selector:
    app: unividown-worker
  ports:
  - port: 8000
    targetPort: 8000
---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: unividown-ingress
  namespace: unividown
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-body-size: "10G"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - your-domain.com
    secretName: unividown-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: unividown-web
            port:
              number: 80
```

---

## Monitoring

### Prometheus + Grafana

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'unividown-worker'
    static_configs:
    - targets: ['unividown-worker:8000']
    metrics_path: '/metrics'
```

Import Grafana dashboard from `docs/grafana-dashboard.json`

### Logs

```bash
# View application logs
docker-compose logs -f worker
docker-compose logs -f web
docker-compose logs -f nginx

# Structured JSON logs (production)
docker-compose logs --no-color worker | jq .
```

---

## Backup & Restore

### Backup Database & Data

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/unividown"

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T worker sqlite3 /app/data/unividown.db .dump > $BACKUP_DIR/db_$DATE.sql

# Backup media files (optional, large)
# tar -czf $BACKUP_DIR/media_$DATE.tar.gz ./data

# Keep last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

### Restore

```bash
# Stop services
docker-compose down

# Restore database
docker-compose up -d worker
sleep 5
docker-compose exec -T worker sqlite3 /app/data/unividown.db < /backups/unividown/db_20240101_000000.sql

# Restore media (if backed up)
# tar -xzf /backups/unividown/media_20240101_000000.tar.gz

# Start all services
docker-compose up -d
```

---

## Troubleshooting

### Worker Not Processing Jobs

```bash
# Check worker logs
docker-compose logs worker

# Check queue
curl -k https://your-domain.com/api/downloads?status=pending

# Restart worker
docker-compose restart worker
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Reduce concurrent downloads in config
# Increase memory limits in docker-compose.yml
```

### SSL Certificate Issues

```bash
# Test certificate
openssl x509 -in nginx/ssl/fullchain.pem -text -noout

# Check nginx config
docker-compose exec nginx nginx -t

# Reload nginx
docker-compose exec nginx nginx -s reload
```

---

## Upgrading

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Run database migrations (if any)
docker-compose exec worker python -m alembic upgrade head
```

---

## Security Checklist

- [ ] Use HTTPS with valid certificates
- [ ] Configure firewall (allow only 80/443)
- [ ] Rate limiting enabled in nginx
- [ ] Regular security updates (`apt update && apt upgrade`)
- [ ] Scan Docker images for vulnerabilities
- [ ] Monitor access logs for suspicious activity
- [ ] Backup encryption for sensitive data
