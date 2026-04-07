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

## Folder Structure
- `/app`: Next.js App Router (Frontend)
- `/backend`: FastAPI Application
- `/messages`: i18n Translation files
- `/components`: Reusable UI components
- `/lib`: Utilities and State management
