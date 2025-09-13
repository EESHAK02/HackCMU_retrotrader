import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd

# Example mapping (expand later)
COMPETITORS = {
    "AAPL": ["MSFT", "GOOGL", "AMZN", "TSLA"],
    "TSLA": ["AAPL", "GM", "F", "NIO"],
    "AMZN": ["WMT", "BABA", "EBAY", "SHOP"],
    "MSFT": ["GOOGL", "AAPL", "ORCL", "IBM"]
}

COMPANY_TICKER_MAP = {
    "apple": "AAPL",
    "tesla": "TSLA",
    "amazon": "AMZN",
    "google": "GOOGL",
    "microsoft": "MSFT"
}

def extract_article_text(url: str) -> str:
    """Scrape main text from an article URL."""
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = soup.find_all("p")
        return "\n".join(p.get_text() for p in paragraphs)
    except Exception as e:
        return f"Error fetching article: {e}"



def get_stock_info(ticker: str) -> dict:
    """Fetch stock price and trend info with defaults for missing data."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="5d")
        price = hist["Close"].iloc[-1] if len(hist) > 0 else None
        prev = hist["Close"].iloc[-2] if len(hist) > 1 else price
        delta = price - prev if price is not None and prev is not None else 0
        trend = "BULLISH" if delta > 0 else "BEARISH" if delta < 0 else "NEUTRAL"
        pct = (delta / prev * 100) if prev else 0
        return {
            "ticker": ticker,
            "price": price,
            "trend": trend,
            "delta": delta,
            "pct": pct,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "name": info.get("shortName", ticker)
        }
    except:
        return {"ticker": ticker, "price": None, "trend": "UNKNOWN", "delta": 0, "pct": None, "sector": "N/A", "industry": "N/A", "name": ticker}


def get_competitors(ticker: str):
    return [get_stock_info(c) for c in COMPETITORS.get(ticker, [])]

TICKER_DB = pd.read_csv("tickers.csv") 
TICKER_DB['Name_lower'] = TICKER_DB['Name'].str.lower()

FMP_API_KEY = "AVt8Z4GQU2zdXEfZ69jqJOfsduyRHX1H"  

def get_ticker(company_name: str) -> str:
    """
    Map company name to ticker symbol using local CSV.
    Returns None if not found.
    """
    if not company_name:
        return None

    name_lower = company_name.lower()

    # Try exact match
    row = TICKER_DB[TICKER_DB['Name_lower'] == name_lower]
    if not row.empty:
        return row['Symbol'].values[0]

    # Try partial match
    row = TICKER_DB[TICKER_DB['Name_lower'].str.contains(name_lower)]
    if not row.empty:
        return row['Symbol'].values[0]

    # Could add fallback to yfinance search if desired
    return None
