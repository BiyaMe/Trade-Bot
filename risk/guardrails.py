def apply_guardrails(decision, account_state):
    # Confidence filter
    if decision["confidence"] < 0.65:
        decision["signal"] = "HOLD"

    # Max risk per trade (1% equity)
    max_risk = account_state["equity"] * 0.01

    decision["risk_usd"] = min(decision.get("risk_usd", max_risk), max_risk)

    # Hard leverage cap
    decision["leverage"] = min(decision.get("leverage", 5), 20)

    # Kill-switch
    if account_state["drawdown"] > 0.15:
        decision["signal"] = "HOLD"

    return decision
from config.settings import MAX_LEVERAGE, MIN_CONFIDENCE, MAX_CONFIDENCE

from config.settings import MAX_LEVERAGE, ALLOWED_SYMBOLS

def check_trade_allowed(decision: dict, symbol: str, account_state: dict):
    """
    Enforces hard safety rules on AI decisions.
    Returns: (is_allowed: bool, reason: str)
    """
    action = decision.get("action", "HOLD")
    
    # 1. Allow HOLD always
    if action == "HOLD":
        return True, "OK"

    # 2. Symbol Validation
    if symbol not in ALLOWED_SYMBOLS:
        return False, f"Symbol {symbol} not in ALLOWED_SYMBOLS"

    # 3. Leverage Validation
    leverage = decision.get("leverage", 1)
    if leverage > MAX_LEVERAGE:
        # Auto-correct or reject? User said "Convert violations to HOLD"
        return False, f"Leverage {leverage} exceeds limit {MAX_LEVERAGE}"

    # 4. Position Size / Balance Validation
    # Assuming 'size' is a percentage of equity (e.g. 0.05 for 5%)
    size = decision.get("size", 0.0)
    if size <= 0:
        return False, "Position size must be positive"
    
    # Check if we have enough balance (simplified check)
    equity = account_state.get("equity", 0)
    cost = (equity * size) / leverage
    balance = account_state.get("balance", 0)

    if cost > balance:
        return False, f"Insufficient balance for trade cost {cost}"

    return True, "OK"
