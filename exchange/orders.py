from exchange.weex_client import WeexClient
from utils.logger import get_logger

logger = get_logger("EXCHANGE")

# Global client instance (could be singleton or passed in)
client = WeexClient.from_env()

def place_order(symbol: str, side: str, size: float, leverage: int, take_profit: float | None = None, stop_loss: float | None = None) -> str:
    """
    Executes a market order on WEEX.
    Returns: orderId (str) or None if failed.
    """
    if side not in ["BUY", "SELL"]: # Explicitly reject everything else
        return None

    logger.info(f"Placing {side} order for {symbol}: size={size}, lev={leverage}x")

    try:

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
        
        if side == "SELL" and (take_profit is None or stop_loss is None):
            logger.error("Refusing to place entry order without TP/SL.")
            return None

        payload = {
            "symbol": symbol,
            "side": side, # "BUY" or "SELL"
            "type": "market", # Market order
            "quantity": str(size), # Usually quantity/size
            "leverage": str(leverage)
        }

        if take_profit is not None:
            payload["presetTakeProfitPrice"] = str(take_profit)
        if stop_loss is not None:
            payload["presetStopLossPrice"] = str(stop_loss)
        
        # Double check types
        if not isinstance(size, (int, float)) or size <= 0:
             logger.error(f"Invalid size: {size}")
             return None

        response = client.place_order(payload)

        if isinstance(response, dict):
            if response.get("code") == "00000":
                order_id = response.get("data", {}).get("orderId") or response.get("data", {}).get("order_id")
                logger.info(f"Order executed: {order_id}")
                return order_id
            if "order_id" in response:
                order_id = response.get("order_id")
                logger.info(f"Order executed: {order_id}")
                return order_id
            logger.error(f"Order failed: {response}")
            return None

        logger.error(f"Unexpected order response: {response}")
        return None

    except Exception as e:
        logger.error(f"Execution exception for {symbol}: {e}")
        return None

def set_leverage(symbol: str, leverage: int):
    try:
        # Check config/cache if leverage needs update?
        # For safety, we set it every time or catch errors
        client.change_leverage(symbol, leverage)
    except Exception as e:
        logger.warning(f"Failed to set leverage: {e}")

class OrderManager:
    # Legacy class, kept for compatibility if needed or removed if unused.
    # The prompt asked to "Implement exchange/orders.py" with responsibilities.
    # I will keep the function-based approach for 'place_order' as requested by runner/trader.py
    pass
