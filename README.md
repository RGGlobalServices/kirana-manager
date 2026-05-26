# Vyapar Sarthi — Kirana Manager

All-in-one billing, inventory, udhar tracking, and AI-powered analytics for Indian kirana stores.

## Architecture

```
├── backend/        # FastAPI (Python) — REST API
├── frontend/       # Next.js (React/TypeScript) — Dashboard
├── landing-page/   # Vite (HTML/JS) — Public marketing site & login
```

## Quick Start

### 1. Environment
```bash
cp .env.example .env.local
# Edit .env.local with your config
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Landing Page
```bash
cd landing-page
npm install
npm run dev
```

### 4. Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```

Or run all at once from root:
```bash
npm install
npm run install:all
npm run dev
```

## Deployment

### Backend (Render / Railway / any Docker host)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend (Vercel)
Set `NEXT_PUBLIC_API_URL` and other env vars in Vercel dashboard, then:
```bash
cd frontend
npm run build
```

### Landing Page (Vercel / Netlify)
```bash
cd landing-page
npm run build
# Deploy the dist/ folder
```

## Tech Stack
- **Backend:** FastAPI, PostgreSQL/SQLite, SQLAlchemy, JWT
- **Dashboard:** Next.js, React 19, Tailwind CSS, Recharts
- **Landing:** Vanilla HTML/JS, Vite, i18n (en/hi/mr)
- **Payments:** PayU

## License
Private — GBRO Industries
