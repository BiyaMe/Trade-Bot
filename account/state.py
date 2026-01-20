from exchange.weex_client import WeexClient
from utils.logger import get_logger

logger = get_logger("ACCOUNT_STATE")
client = WeexClient.from_env()

def get_account_state() -> dict:
    """
    Fetches real account equity and balance.
    """
    try:
        # Endpoint: /capi/v2/account/assets
        # Or specific futures account endpoint
        response = client.get("/capi/v2/account/assets", params={"accountType": "futures"}) # params hypothetical
        
        if response.get("code") == "00000":
             data = response.get("data", {})
             # Map response fields (hypothetical mapping, adjust to real API docs)
             equity = float(data.get("equity", 0.0))
             balance = float(data.get("availableBalance", 0.0))
             
             return {
                 "equity": equity,
                 "balance": balance,
                 "drawdown": 0.0, # Calculation requires historical tracking, simplified for now
                 "open_positions": [] # Retrieve positions if needed
             }
        else:
            logger.error(f"Account fetch failed: {response}")
            return {"equity": 0, "balance": 0}

    except Exception as e:
        logger.error(f"Account exception: {e}")
        return {"equity": 0, "balance": 0}
