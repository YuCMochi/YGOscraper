# YGOscraper V2.0.0

A modern web application for optimizing Yu-Gi-Oh! card purchases from Ruten (露天拍賣).

## Architecture

- **Frontend**: React + Vite + TailwindCSS (v4)
- **Backend**: FastAPI (Python)
- **Database**: 
  - `cards.cdb` (SQLite): Offline card database (managed by Frontend via `sql.js`)
  - Local JSON storage for projects and shopping carts.
- **Scraper**: Custom Python scripts (`scraper.py`, `konami_scraper.py`) for Ruten and Konami DB.

## Prerequisites

- **Python**: 3.9+
- **Node.js**: 18+ (Required for Frontend)
- **cards.cdb**: A valid YGOPro card database file placed in `data/cards.cdb` (or root).

## Installation

### 1. Backend Setup

```bash
# Create and activate virtual environment (optional but recommended)
python -m venv env
source env/bin/activate  # Mac/Linux
# env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup (Important)

> **⚠️ Known Issue**: Due to file permission restrictions in the development environment, `frontend/package.json` might be locked. If you encounter errors, please run:

```bash
cd frontend
# If package.json is missing or corrupted, restore it manually or run:
npm install
```

If `npm install` fails due to `package.json` issues, verify that `frontend/package.json` exists and is readable.

## Running the Application

### 1. Start Backend Server

```bash
# In the project root
uvicorn server:app --reload
```
API will run at `http://localhost:8000`.

### 2. Start Frontend Dev Server

```bash
# In a new terminal, inside frontend/ directory
cd frontend
npm run dev
```
Frontend will run at `http://localhost:5173`.

## Usage

1.  **Create Project**: Open the web UI and create a new project.
2.  **Search Cards**: Go to the project page -> "Search Cards".
3.  **Add to Cart**: Search for cards (supports Chinese/Japanese) and add them to your cart.
    - The backend automatically fetches the correct card numbers (e.g., `DABL-JP035`) from Konami DB.
4.  **Run Scraper**: In the project detail page, click **"Run Scraper"**.
    - This triggers the backend to scrape Ruten, clean data, and calculate the optimal purchase plan.
5.  **View Results**: The optimal plan (lowest total price + shipping) will be displayed.

## Version History

- **v2.0.0**: Complete rewrite with React Frontend and FastAPI Backend.
- **v1.0.0**: Legacy CLI/HTML version (Deprecated).
