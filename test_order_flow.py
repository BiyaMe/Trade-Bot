from exchange.weex_client import WeexClient
from exchange.orders import OrderManager
from dotenv import load_dotenv
import os
import yaml
import time

load_dotenv()

with open("config/settings.yaml") as f:
    settings = yaml.safe_load(f)

client = WeexClient(
    api_key=os.getenv("WEEX_API_KEY"),
    secret_key=os.getenv("WEEX_SECRET_KEY"),
    passphrase=os.getenv("WEEX_PASSPHRASE"),
    base_url=settings["base_url"]
)

orders = OrderManager(client)

SYMBOL = "cmt_btcusdt"

print("Setting leverage...")
print(orders.set_leverage(SYMBOL, leverage=1))

print("Fetching ticker...")
ticker = client.get(
    "/capi/v2/market/ticker",
    params={"symbol": SYMBOL}
)
print(ticker)

price = float(ticker["last"])

# Place a small order (~10 USDT)
size = 0.0001  # small & safe
limit_price = price * 0.98  # below market to avoid instant fill

print("Placing order...")
order_resp = orders.place_limit_order(
    symbol=SYMBOL,
    side="BUY",
    price=limit_price,
    size=size,
    client_oid="api-test"
)

print(order_resp)

order_id = order_resp.get("order_id")
if not order_id:
    raise RuntimeError("Order ID not returned")

print("Waiting for fill...")
time.sleep(5)

print("Fetching fills...")
fills = orders.get_fills(SYMBOL, order_id)
print(fills)
