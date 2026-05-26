# Kirana Smart Dashboard

Production-ready POS and store management system for Indian Kirana stores.

## Features
- Fast POS Billing (<10s)
- QR/Barcode Scanning
- Multilingual (English, Hindi, Marathi)
- Udhar (Credit) Management
- Inventory & Low Stock Alerts
- Sales & Profit Reports

## Tech Stack
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Shadcn/UI, Zustand, Recharts
- **Backend**: FastAPI (Python), PostgreSQL, SQLAlchemy, Redis, Celery
- **Infrastructure**: Docker, Nginx

## Setup Instructions

### 1. Environment Variables
Copy `.env.example` to `.env` and fill in the details.

### 2. Docker Deployment
```bash
docker-compose up --build
```

### 3. Database Migrations & Seeding
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed initial data
docker-compose exec backend python seed.py
```

### 4. Manual Development
**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**:
```bash
npm install
npm run dev
```

---

## Render Deployment (Recommended for MVP)

### Landing Page (Vite — static site)

1. Go to https://dashboard.render.com → **New + → Static Site**
2. Connect your GitHub repo `RGGlobalServices/kirana-manager`
3. Fill in:
   - **Name:** `kirana-landing`
   - **Root Directory:** `landing-page`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
4. Click **Create Static Site**
5. Your landing page will be live at `https://kirana-landing.onrender.com`

> **Note:** The landing page is a standalone Vite site (`landing-page/`). It does not require a server — Render serves the built static files directly.

### Backend (FastAPI — web service)

1. **New + → Web Service**
2. Connect the same repo
3. Fill in:
   - **Name:** `kirana-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (under **Environment**):
   - `DATABASE_URL` — use Render's free PostgreSQL (see below)
   - `SECRET_KEY` — generate a random string
   - `LANDING_URL` — `https://kirana-landing.onrender.com`
   - `APP_URL` — your frontend URL (Next.js, see below)
   - `BACKEND_URL` — `https://kirana-backend.onrender.com`
   - `KS_GOOGLE_CLIENT_ID` — your Google OAuth client ID
5. Click **Create Web Service**

### Database (Render PostgreSQL)

1. **New + → PostgreSQL**
2. **Name:** `kirana-db`
3. Choose **Free** plan (1 GB storage, expires after 90 days)
4. After creation, copy the **Internal Database URL** and set it as `DATABASE_URL` in your backend web service

### Frontend (Next.js — web service or static)

**Option 1 — Web Service (recommended for SSR):**
1. **New + → Web Service**
2. **Name:** `kirana-frontend`
3. **Root Directory:** `frontend`
4. **Runtime:** `Node`
5. **Build Command:** `npm install && npm run build`
6. **Start Command:** `npm start`
7. Add env vars:
   - `NODE_ENV=production`
   - (other vars are read from the backend API at runtime)

**Option 2 — Static Site (if using `next export`):**
1. **New + → Static Site**
2. **Root Directory:** `frontend`
3. **Build Command:** `npm install && npm run build && npx next export`
4. **Publish Directory:** `out`

### Separate Domains (Custom)

After deployment, each service gets its own `*.onrender.com` URL. To use custom domains:
- Go to each service's **Settings → Custom Domain**
- Add your domain (e.g., `vyaparsarthi.com` for landing, `api.vyaparsarthi.com` for backend)
- Update your DNS with the provided CNAME records

---

## AWS Deployment

### Option A — Backend on EC2 + Frontend on S3/CloudFront

**Backend (FastAPI on EC2):**
```bash
# SSH into your EC2 instance (Amazon Linux 2023)
sudo yum update -y
sudo yum install -y python3-pip nginx

# Clone the repo
git clone https://github.com/RGGlobalServices/kirana-manager.git /app
cd /app/backend

# Install deps & start
pip install -r requirements.txt
pip install uvicorn gunicorn

# Run with systemd or screen
screen -S backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Nginx reverse proxy (for HTTPS & domain):**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Frontend (Next.js on S3 + CloudFront):**
```bash
cd frontend
npm install
npm run build

# Sync the .next/static & public folders to S3
aws s3 sync out/ s3://your-bucket/ --delete

# Point CloudFront distribution to the S3 bucket
```

**Database (RDS PostgreSQL):**
- Create a free-tier PostgreSQL instance in AWS RDS
- Set `DATABASE_URL` in your EC2 environment

### Option B — Elastic Beanstalk (simpler)

```bash
# Install EB CLI
pip install awsebcli

# Deploy backend
cd backend
eb init -p python-3.10 kirana-manager --region ap-south-1
eb create production

# Set environment variables via EB console or CLI:
eb setenv SECRET_KEY=... DATABASE_URL=postgres://... ...
```

### Option C — ECS / Fargate (Docker)

```bash
# Build and push image to ECR
aws ecr create-repository --repository-name kirana-backend
docker tag kirana-backend:latest <account>.dkr.ecr.ap-south-1.amazonaws.com/kirana-backend
docker push <account>.dkr.ecr.ap-south-1.amazonaws.com/kirana-backend

# Deploy via ECS Fargate with the task definition in docker-compose.yml
# or use AWS Copilot:
copilot init --app kirana --name backend --type 'Load Balanced Web Service' --dockerfile ./backend/Dockerfile
copilot deploy
```

### Required AWS Resources Summary

| Service    | Purpose                  | Approx Cost (ap-south-1) |
|------------|--------------------------|--------------------------|
| EC2 t4g.nano  | Backend API (FastAPI)    | ~₹450/month            |
| RDS db.t4g.micro | PostgreSQL database   | ~₹650/month            |
| S3 + CloudFront | Frontend hosting     | ~₹200/month            |
| Route 53   | Domain (optional)        | ~₹400/month            |
| **Total**  |                          | **~₹1,700/month**      |

Set these env vars on your EC2/EB/ECS environment:
```
DATABASE_URL=postgresql://user:pass@your-rds-endpoint:5432/kirana
SECRET_KEY=<random-secret>
APP_URL=https://your-frontend-domain.com
LANDING_URL=https://your-landing-domain.com
BACKEND_URL=https://api.yourdomain.com
KS_GOOGLE_CLIENT_ID=...
SMTP_USER=...
SMTP_PASSWORD=...
```

---

## Folder Structure
- `/app`: Next.js App Router (Frontend)
- `/backend`: FastAPI Application
- `/messages`: i18n Translation files
- `/components`: Reusable UI components
- `/lib`: Utilities and State management
