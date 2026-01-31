# Stock Check Project

A full-stack application to check and compare stock & ETF prices, featuring a **FastAPI** backend and a **React (Vite)** frontend.

## Features
- Real-time stock data (via `yfinance`).
- Interactive price history charts (via `recharts`).
- Fully responsive design (Desktop & Mobile).
- Dockerized backend (optional).

## Tech Stack
- **Backend**: Python 3.9, FastAPI, yfinance, Pandas, `uv` (package manager).
- **Frontend**: React, Vite, Recharts, Vanilla CSS.

## Getting Started

### Backend
1. Navigate to the project root:
   ```bash
   cd stock_check
   ```
2. Install dependencies using `uv` (or pip):
   ```bash
   uv pip install -r backend/pyproject.toml
   # or
   pip install -r backend/pyproject.toml
   ```
   *Note: If using `uv`, create a venv first: `uv venv` and `source .venv/bin/activate`.*

3. Start the server:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The API will be available at `http://localhost:8000`.

### Frontend
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:5173`.

## Docker (Backend)
To run the backend with Docker:
```bash
docker build -t stock-check-backend ./backend
docker run -p 8000:8000 stock-check-backend
```
