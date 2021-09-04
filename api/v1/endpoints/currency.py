from fastapi import APIRouter, HTTPException
from typing import Optional
import requests

router = APIRouter()

# Tickers
tickers = ['USD', "EUR", "RUB", "CAD", 'PHP', 'DKK', 'HUF', 'CZK', 'AUD', 'RON', 'SEK', 'IDR',
            'INR', 'BRL', 'RUB', 'HRK', 'JPY', 'THB', 'CHF', 'SGD', 'PLN', 'BGN', 'TRY',
            'CNY', 'NOK', 'NZD', 'ZAR', 'MXN', 'ILS', 'GBP', 'KRW', 'MYR', 'CAD']

@router.get("/currency")
async def get_spot_prices(
    ticker: Optional[str] = "USD"
):  # can also use EUR, GBP and JPY, etc.
    """ Get real-time price for the currency of your choice containing spot price data from Coinbase """
    r = requests.get(f"https://api.coinbase.com/v2/prices/spot?currency={ticker}")
    data = r.json()
    if ticker not in tickers:
        raise HTTPException(status_code=404, detail="Invalid currency")
    return data
