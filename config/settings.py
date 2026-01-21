
import os
import yaml

# Strict competition constants
ALLOWED_SYMBOLS = [
    "cmt_btcusdt",
    "cmt_ethusdt",
    "cmt_solusdt",
    "cmt_dogeusdt",
    "cmt_xrpusdt",
    "cmt_adausdt",
    "cmt_bnbusdt",
    "cmt_ltcusdt"
]

MAX_LEVERAGE = 20
MIN_CONFIDENCE = 0.0
MAX_CONFIDENCE = 1.0

_DEFAULT_SETTINGS = {
    "max_open_trades": 2,
    "max_risk_per_trade_pct": 0.02,
    "trade_notional_usdt": 10,
    "take_profit_usdt": 10,
    "stop_loss_usdt": 1,
}

_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.yaml")
_SETTINGS = {}
if os.path.exists(_SETTINGS_PATH):
    with open(_SETTINGS_PATH, "r") as f:
        _SETTINGS = yaml.safe_load(f) or {}

MAX_OPEN_TRADES = int(_SETTINGS.get("max_open_trades", _DEFAULT_SETTINGS["max_open_trades"]))
MAX_RISK_PER_TRADE_PCT = float(
    _SETTINGS.get("max_risk_per_trade_pct", _DEFAULT_SETTINGS["max_risk_per_trade_pct"])
)
TRADE_NOTIONAL_USDT = float(_SETTINGS.get("trade_notional_usdt", _DEFAULT_SETTINGS["trade_notional_usdt"]))
TAKE_PROFIT_USDT = float(_SETTINGS.get("take_profit_usdt", _DEFAULT_SETTINGS["take_profit_usdt"]))
STOP_LOSS_USDT = float(_SETTINGS.get("stop_loss_usdt", _DEFAULT_SETTINGS["stop_loss_usdt"]))

# System constraints
TIMEFRAME = "5m"  # as per "3-10 minutes" horizon implies short term
