# Docker Compose Setup

This project uses the standard Docker Compose pattern with base and override files.

## File Structure

- **`docker-compose.yml`** - Base configuration (shared across all environments)
- **`docker-compose.override.yml`** - Local development overrides (automatically loaded)
- **`docker-compose.prod.yml`** - Production-specific configuration

## Usage

### Local Development

Simply run:
```bash
docker-compose up
```

This automatically uses:
- `docker-compose.yml` (base)
- `docker-compose.override.yml` (local dev)

Features:
- Hot reload for React (port 3000)
- Volume mounts for live code updates
- Exposed ports for debugging
- Development Dockerfiles

### Production

Run with explicit file specification:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Features:
- Production Dockerfiles with optimized builds
- No volume mounts (uses built images)
- SSL/HTTPS with Let's Encrypt
- Automatic certificate renewal
- Restricted port exposure
- Restart policies

## Services

- **db** - PostgreSQL database
- **api** - Django backend
- **web** - React frontend (dev server locally, built static files in prod)
- **nginx** - Routes up all the /api vs web stuff and helps with HTTPS stuff.
- **certbot** - SSL(Https) certificate management (production only)

## First Time Setup

### Local
```bash
docker-compose up --build
```

### Production
```bash
# Build and start
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Initial SSL certificate (if needed)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot -d your-domain.com
```
