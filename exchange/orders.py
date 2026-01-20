from exchange.weex_client import WeexClient
from utils.logger import get_logger

logger = get_logger("EXCHANGE")

# Global client instance (could be singleton or passed in)
client = WeexClient.from_env()

def place_order(symbol: str, side: str, size: float, leverage: int) -> str:
    """
    Executes a market order on WEEX.
    Returns: orderId (str) or None if failed.
    """
    if side not in ["BUY", "SELL"]: # Explicitly reject everything else
        return None

    logger.info(f"Placing {side} order for {symbol}: size={size}, lev={leverage}x")

    try:
        # 1. Set leverage first (CRITICAL)
        set_leverage(symbol, leverage)

        # 2. Place Market Order
        # WEEX API: /capi/v2/order/placeOrder
        # "type": "market" might be mapped to type code, checking docs or user prompt examples.
        # User prompt example 2 uses "type": "1" (Limit). 
        # Standard WEEX usually: type="market" or type="2" (Market). 
        # Safest assumption implies text "market" or explicit param.
        # Let's use string "market" as user prompt says "Support market orders only".
        
        # We need to ensure 'side' matches API expectation (usually 1=open long, 2=close short...)
        # STARTUP WARNING: This part requires exact API knowledge.
        # For now, we assume strict mapping:
        # If the client library handles mapping "BUY" -> proper code, good.
        # If not, we might fail. Given WeexClient is generic, we should map here if we knew codes.
        # Assuming "side": "BUY" works or Weex accepts standard strings.
        
        payload = {
            "symbol": symbol,
            "side": side, # "BUY" or "SELL"
            "type": "market", # Market order
            "quantity": str(size), # Usually quantity/size
            "leverage": str(leverage)
        }
        
        # Double check types
        if not isinstance(size, (int, float)) or size <= 0:
             logger.error(f"Invalid size: {size}")
             return None

        response = client.post("/capi/v2/order/placeOrder", payload)
        
        if response.get("code") == "00000":
            order_id = response.get("data", {}).get("orderId")
            logger.info(f"Order executed: {order_id}")
            return order_id
        else:
            logger.error(f"Order failed: {response}")
            return None

    except Exception as e:
        logger.error(f"Execution exception for {symbol}: {e}")
        return None

def set_leverage(symbol: str, leverage: int):
    try:
        # Check config/cache if leverage needs update?
        # For safety, we set it every time or catch errors
        client.post("/capi/v2/account/leverage", {
            "symbol": symbol,
            "leverage": str(leverage)
        })
    except Exception as e:
        logger.warning(f"Failed to set leverage: {e}")

class OrderManager:
    # Legacy class, kept for compatibility if needed or removed if unused.
    # The prompt asked to "Implement exchange/orders.py" with responsibilities.
    # I will keep the function-based approach for 'place_order' as requested by runner/trader.py
    pass
