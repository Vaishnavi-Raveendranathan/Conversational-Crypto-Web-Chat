# Conversational Crypto Web-Chat

A mobile-friendly chat interface for cryptocurrency information, portfolio tracking, and voice interactions.

## Features

- Real-time cryptocurrency price checking
- Trending coins listing
- Basic crypto statistics
- Portfolio tracking
- 7-day price charts
- Voice input/output

## Tech Stack

- Backend: Python (FastAPI)
- Frontend: Vue.js 3
- Database: SQLite (for portfolio storage)
- Crypto API: CoinGecko (free tier)
- Voice: Web Speech API

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Setup Instructions

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python backend/main.py
```

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## API Endpoints

- `GET /api/price/{symbol}` - Get current price
- `GET /api/trending` - Get trending coins
- `GET /api/stats/{symbol}` - Get basic stats
- `GET /api/chart/{symbol}` - Get 7-day price chart
- `POST /api/portfolio` - Update portfolio
- `GET /api/portfolio` - Get portfolio value

## Environment Variables

Create a `.env` file in the backend directory with:

```
COINGECKO_API_KEY=your_api_key_here
```

## License

MIT 