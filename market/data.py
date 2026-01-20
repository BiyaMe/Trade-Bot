from exchange.weex_client import WeexClient
from utils.logger import get_logger

logger = get_logger("MARKET_DATA")
client = WeexClient.from_env()

def get_latest_price(symbol: str) -> float:
    """
    Fetches the latest price of a symbol from WEEX API.
    """
    try:
        # Assuming WEEX endpoint /capi/v2/market/ticker?symbol=...
        response = client.get(f"/capi/v2/market/ticker", params={"symbol": symbol})
        if response.get("code") == "00000":
             # Structure might vary, assuming typical data.ticker.last
             return float(response["data"]["ticker"]["last"])
        else:
            logger.error(f"Price fetch error {symbol}: {response}")
            return None
    except Exception as e:
        logger.error(f"Price exception {symbol}: {e}")
        return None

def get_market_snapshot(symbol: str) -> dict:
    """
    Returns a market snapshot including OHLCV and indicators.
    Calculates RSI/EMA locally from fetched candles.
    """
    try:
        # 1. Get Candles (e.g. 5m candles)
        # Endpoint: /capi/v2/market/kline?symbol=...&limit=100&interval=5m
        response = client.get("/capi/v2/market/kline", params={
            "symbol": symbol,
            "interval": "5m",
            "limit": "50"
        })
        
        if response.get("code") != "00000":
             logger.error(f"Kline fetch failed for {symbol}")
             return {}

        candles = response.get("data", [])
        if not candles:
            return {}

        # Parse candles (Timestamp, Open, High, Low, Close, Vol, ...)
        # Assuming standard format: [t, o, h, l, c, v]
        closes = [float(c[4]) for c in candles]
        
        # 2. Calculate Indicators (Simple local calc for dependency-free speed)
        current_price = closes[-1]
        
        # RSI (14)
        rsi = calculate_rsi(closes, 14)
        
        # EMA (20)
        ema = calculate_ema(closes, 20)
        
        # Funding Rate
        funding_resp = client.get("/capi/v2/market/funding-rate", params={"symbol": symbol})
        funding = 0.0
        if funding_resp.get("code") == "00000":
            funding = float(funding_resp["data"]["fundingRate"])

        return {
            "symbol": symbol,
            "price": current_price,
            "rsi": round(rsi, 2),
            "ema": round(ema, 2),
            "atr": 0.0, # Skip for now or implement if critical
            "funding": funding
        }

    except Exception as e:
        logger.error(f"Snapshot error {symbol}: {e}")
        return {"symbol": symbol, "price": 0.0}

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gain = sum([d for d in deltas if d > 0]) / period
    loss = abs(sum([d for d in deltas if d < 0])) / period
    
    if loss == 0: return 100.0
    rs = gain / loss
    return 100.0 - (100.0 / (1 + rs))

def calculate_ema(prices, period=20):
    if len(prices) < period:
        return prices[-1]
    
    multiplier = 2 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = (p - ema) * multiplier + ema
    return ema
