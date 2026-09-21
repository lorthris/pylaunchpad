# Operational Deployment Guide

Instructions for deploying PyLaunchpad into production, configuring Merchant of Record billing, and managing operational infrastructure.

---

## 1. Capital Allocation & Budget

The maximum permitted out-of-pocket setup budget is $20 USD ($40 AUD).

### Zero Out-of-Pocket Strategy (Current State)
- **Showcase Hosting:** GitHub Pages (`$0.00`).
- **Billing Infrastructure:** Polar.sh Merchant of Record (`$0.00` setup fee; 5% + $0.50 transaction fee only upon completed sale).
- **Automated Delivery:** Polar.sh digital download benefit (`$0.00`).
- **Initial Out-of-Pocket Spend:** `$0.00 USD`.
- **Remaining Capital Balance:** `$20.00 USD / $40.00 AUD` (100% intact).

---

## 2. Deploying the Web Showcase (GitHub Pages)

The `docs/` directory contains the standalone web application and documentation.

1. Verify that the repository is pushed to GitHub:
   ```bash
   git push origin main
   ```
2. Open repository **Settings** -> **Pages**.
3. Under **Build and deployment**:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/docs`
4. Click **Save**. Your showcase will be published live at `https://lorthris.github.io/pylaunchpad/`.

---

## 3. Production Server Deployment (Docker & Caddy)

To deploy the full FastAPI application on a cloud VPS:

1. Provision an Ubuntu 22.04 or Debian 12 server (e.g. Hetzner, DigitalOcean, or AWS EC2).
2. Install Docker and Docker Compose:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
3. Clone the repository and copy your production environment variables:
   ```bash
   git clone https://github.com/lorthris/pylaunchpad.git
   cd pylaunchpad
   cp .env.example .env
   ```
4. Edit `.env` with a secure random secret key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
5. Update `Caddyfile` with your production domain name:
   ```caddyfile
   api.yourdomain.com {
       reverse_proxy app:8000
   }
   ```
6. Start the production stack:
   ```bash
   docker compose up -d --build
   ```

---

## 4. Database Backups

### SQLite Backups
For single-node deployments using SQLite:
```bash
# Safely snapshot live database using sqlite3 online backup API
sqlite3 /app/data/pylaunchpad.db ".backup '/app/data/backup-$(date +%Y%m%d%H%M).sqlite'"
```

### PostgreSQL Backups
For PostgreSQL deployments:
```bash
pg_dump -U postgres -d pylaunchpad_db | gzip > backup-$(date +%Y%m%d%H%M).sql.gz
```
