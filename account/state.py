from exchange.weex_client import WeexClient
from utils.logger import get_logger

logger = get_logger("ACCOUNT_STATE")
client = WeexClient.from_env()

def get_account_state() -> dict:
    """
    Fetches real account equity and balance.
    """
    try:
        # Endpoint: /capi/v2/account/getAccounts
        # Docs: https://www.weex.com/api-doc/contract/Account_API/AllContractAccountsInfo
        response = client.get_accounts()

        # Some endpoints return raw payload without {code,data}. Handle both.
        payload = response
        if isinstance(response, dict) and response.get("code") == "00000":
            payload = response.get("data", response)

        collateral = payload.get("collateral", []) if isinstance(payload, dict) else []
        usdt = next((c for c in collateral if c.get("coin") == "USDT"), None)
        amount = float(usdt.get("amount", 0.0)) if usdt else 0.0

        if amount > 0 or collateral:
            return {
                "equity": amount,
                "balance": amount,
                "drawdown": 0.0,  # Calculation requires historical tracking, simplified for now
                "open_positions": []  # Retrieve positions via positions endpoint if needed
            }

        logger.error(f"Account fetch failed: {response}")
        return {"equity": 0, "balance": 0}

    except Exception as e:
        logger.error(f"Account exception: {e}")
        return {"equity": 0, "balance": 0}
