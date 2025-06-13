from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta
import json

load_dotenv()

app = FastAPI()

# CORS middleware configuration
origins = [
    "https://conversational-crypto-web-chat.vercel.app",
    "https://conversational-crypto-web-chat-e36a-4zot3izie.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=86400,
)

# Add middleware to set CORS headers
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://conversational-crypto-web-chat.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

# Models
class PortfolioItem(BaseModel):
    symbol: str
    amount: float

class PortfolioResponse(BaseModel):
    total_value: float
    holdings: List[dict]

# CoinGecko API base URL
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Symbol to CoinGecko ID mapping
COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "MATIC": "matic-network"
}

@app.get("/api/price/{symbol}")
async def get_price(symbol: str):
    try:
        coin_id = COIN_IDS.get(symbol.upper())
        if not coin_id:
            raise HTTPException(status_code=404, detail=f"Unsupported cryptocurrency: {symbol}")
            
        response = requests.get(f"{COINGECKO_API}/simple/price", 
                              params={"ids": coin_id, "vs_currencies": "usd"})
        data = response.json()
        if coin_id not in data:
            raise HTTPException(status_code=404, detail="Cryptocurrency not found")
        return {"price": data[coin_id]["usd"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trending")
async def get_trending():
    try:
        response = requests.get(f"{COINGECKO_API}/search/trending")
        data = response.json()
        return {"coins": data["coins"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/{symbol}")
async def get_stats(symbol: str):
    try:
        coin_id = COIN_IDS.get(symbol.upper())
        if not coin_id:
            raise HTTPException(status_code=404, detail=f"Unsupported cryptocurrency: {symbol}")
            
        response = requests.get(f"{COINGECKO_API}/coins/{coin_id}")
        data = response.json()
        
        # Get the first paragraph of the description
        full_description = data["description"]["en"]
        brief_description = full_description.split('\n')[0]  # Get first paragraph
            
        return {
            "symbol": data["symbol"].upper(),
            "name": data["name"],
            "market_cap": data["market_data"]["market_cap"]["usd"],
            "price_change_24h": data["market_data"]["price_change_percentage_24h"],
            "description": brief_description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chart/{symbol}")
async def get_chart(symbol: str):
    try:
        coin_id = COIN_IDS.get(symbol.upper())
        if not coin_id:
            raise HTTPException(status_code=404, detail=f"Unsupported cryptocurrency: {symbol}")
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        try:
            response = requests.get(
                f"{COINGECKO_API}/coins/{coin_id}/market_chart/range",
                params={
                    "vs_currency": "usd",
                    "from": int(start_date.timestamp()),
                    "to": int(end_date.timestamp())
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if "prices" not in data:
                raise HTTPException(status_code=404, detail="No price data available")
                
            if not data["prices"] or len(data["prices"]) < 2:
                raise HTTPException(status_code=404, detail="Insufficient price data")
                
            return {"prices": data["prices"]}
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error fetching data from CoinGecko: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio")
async def update_portfolio(item: PortfolioItem):
    try:
        # Insert into Supabase
        data = supabase.table('portfolio').insert({
            "symbol": item.symbol.upper(),
            "amount": item.amount
        }).execute()
        
        return {"message": "Portfolio updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio")
async def get_portfolio():
    try:
        # Get all holdings from Supabase
        response = supabase.table('portfolio').select("*").execute()
        holdings = response.data

        total_value = 0
        portfolio_data = []

        for holding in holdings:
            symbol = holding['symbol']
            amount = holding['amount']
            
            coin_id = COIN_IDS.get(symbol.upper())
            if not coin_id:
                continue
                
            price_response = requests.get(f"{COINGECKO_API}/simple/price",
                                       params={"ids": coin_id, "vs_currencies": "usd"})
            price_data = price_response.json()
            if coin_id in price_data:
                value = price_data[coin_id]["usd"] * amount
                total_value += value
                portfolio_data.append({
                    "symbol": symbol,
                    "amount": amount,
                    "value": value
                })

        return PortfolioResponse(total_value=total_value, holdings=portfolio_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/portfolio")
async def clear_portfolio():
    try:
        # Delete all records from Supabase
        supabase.table('portfolio').delete().execute()
        return {"message": "Portfolio cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
