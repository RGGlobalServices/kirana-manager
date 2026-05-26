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
