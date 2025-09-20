import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf


def fetch_stock_summary():
    ticker = yf.Ticker("TSLA")
    data = ticker.history(period="1d")
    if data.empty:
        return "TSLA price unavailable"
    price = data["Close"].iloc[-1]
    open_price = data["Open"].iloc[-1]
    change = price - open_price
    pct = change / open_price * 100
    return f"TSLA ${price:.2f} ({change:+.2f}, {pct:+.2f}%)"


def fetch_latest_news(count=3):
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        return []
    url = (
        "https://gnews.io/api/v4/search?q=Tesla&lang=en&token="
        f"{api_key}&max={count}"
    )
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()
    return [f"{a['title']} - {a['url']}" for a in data.get('articles', [])[:count]]


def fetch_next_earnings():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/"
    }
    try:
        res = requests.get("https://ir.tesla.com", headers=headers, timeout=10)
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        return "N/A"

    soup = BeautifulSoup(res.text, "html.parser")
    event_view = soup.find("div", class_="view-company-events")
    if not event_view:
        return "N/A"
    first = event_view.find("div", class_="views-row")
    if not first:
        return "N/A"
    date_el = first.find(class_="date-display-single")
    desc = first.get_text(" ", strip=True)
    if date_el:
        date_text = date_el.get_text(strip=True)
        desc = desc.replace(date_text, "").strip()
        return f"{date_text}: {desc}"
    return desc
