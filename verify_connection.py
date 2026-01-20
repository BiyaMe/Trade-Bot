from dotenv import load_dotenv
load_dotenv()

from exchange.weex_client import WeexClient
from utils.logger import get_logger
import sys

logger = get_logger("VERIFY")

def main():
    logger.info("Checking API Connectivity...")
    
    try:
        client = WeexClient.from_env()
    except Exception as e:
        logger.error(f"Failed to load client from env: {e}")
        return

    # 1. Check System Time (Public)
    try:
        logger.info("1. Testing Public Endpoint...")
        # Check if we can hit a public endpoint (e.g. market data) without auth
        res = client.get("/capi/v2/market/ticker", params={"symbol": "cmt_btcusdt"})
        if res.get("code") == "00000":
            logger.info("✅ Public API connection successful.")
        else:
            logger.error(f"❌ Public API failed: {res}")
            
    except Exception as e:
        logger.error(f"❌ Public API Exception: {e}")

    # 2. Check Account Assets (Private/Auth)
    try:
        logger.info("2. Testing Authenticated Endpoint...")
        # Endpoint may vary, using what we implemented in account/state.py
        res = client.get("/capi/v2/account/assets", params={"accountType": "futures"})
        
        if res.get("code") == "00000":
             logger.info("✅ Authenticated API successful.")
             data = res.get("data", {})
             equity = data.get("equity", "Unknown")
             logger.info(f"   Connection verified! Account Equity: {equity}")
        else:
            logger.error(f"❌ Authenticated API failed: {res}")
            logger.error("   Please check your API_KEY, SECRET_KEY, and PASSPHRASE in .env")
            
    except Exception as e:
        logger.error(f"❌ Authenticated API Exception: {e}")

if __name__ == "__main__":
    main()
