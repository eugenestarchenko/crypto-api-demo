from fastapi import APIRouter, HTTPException
from typing import Optional
import requests

router = APIRouter()

# Tickers
tickers = [
    "USD",
    "EUR",
    "RUB",
    "CAD",
    "PHP",
    "DKK",
    "HUF",
    "CZK",
    "AUD",
    "RON",
    "SEK",
    "IDR",
    "INR",
    "BRL",
    "RUB",
    "HRK",
    "JPY",
    "THB",
    "CHF",
    "SGD",
    "PLN",
    "BGN",
    "TRY",
    "CNY",
    "NOK",
    "NZD",
    "ZAR",
    "MXN",
    "ILS",
    "GBP",
    "KRW",
    "MYR",
    "CAD",
]


@router.get("/currency")
async def get_spot_prices(
    ticker: Optional[str] = "USD", max_length=3
):  # can also use EUR, GBP and JPY, etc.
    """Get real-time price for the currency of your choice containing spot price data from Coinbase"""
    try:
        r = requests.get(
            f"https://api.coinbase.com/v2/prices/spot?currency={ticker}", timeout=15
        )
        if ticker not in tickers:
            raise HTTPException(status_code=404, detail="Invalid currency")
        data = r.json()
        return data
    # Handle errors
    except requests.exceptions.RequestException:
        # return "Error: {}".format(e)
        raise HTTPException(status_code=500, detail="Error connecting, retry later")
