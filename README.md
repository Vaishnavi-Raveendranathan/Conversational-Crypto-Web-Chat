# Conversational Crypto Web Chat

A web-based cryptocurrency assistant that allows users to interact with crypto data through natural language. The application provides real-time cryptocurrency prices, charts, portfolio management, and more.

## Features

- Real-time cryptocurrency price tracking
- Interactive price charts
- Portfolio management
- Natural language processing for user queries
- Voice input support
- Text-to-speech responses
- Trending cryptocurrencies
- Detailed cryptocurrency statistics

## Tech Stack

- Frontend: Vue.js 3 with Tailwind CSS
- Backend: FastAPI (Python)
- Database: Supabase (PostgreSQL)
- External APIs: CoinGecko
- Authentication: Supabase Auth

## Prerequisites

- Python 3.8+
- Node.js 14+
- Supabase account
- CoinGecko API access

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Vaishnavi-Raveendranathan/Conversational-Crypto-Web-Chat.git
cd Conversational-Crypto-Web-Chat
```

### 2. Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

4. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

### 3. Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

### 4. Supabase Setup

1. Create a new project on [Supabase](https://supabase.com)
2. Create the portfolio table using the SQL editor:
```sql
create table portfolio (
  id bigint generated by default as identity primary key,
  symbol text not null,
  amount float not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

3. Get your Supabase credentials:
   - Go to Project Settings
   - Find the "Project URL" and "anon/public" key
   - Add these to your `.env` file

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Start chatting with the assistant using natural language
3. Try commands like:
   - "Show me ETH price"
   - "Add 0.5 BTC to my portfolio"
   - "Show my portfolio"
   - "Show BTC chart"
   - "What are the trending coins?"

## API Endpoints

- `GET /api/price/{symbol}` - Get current price for a cryptocurrency
- `GET /api/trending` - Get trending cryptocurrencies
- `GET /api/stats/{symbol}` - Get detailed statistics for a cryptocurrency
- `GET /api/chart/{symbol}` - Get 7-day price chart data
- `GET /api/portfolio` - Get user's portfolio
- `POST /api/portfolio` - Add cryptocurrency to portfolio
- `DELETE /api/portfolio` - Clear portfolio

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- CoinGecko API for cryptocurrency data
- Supabase for database and authentication
- Vue.js and FastAPI communities 