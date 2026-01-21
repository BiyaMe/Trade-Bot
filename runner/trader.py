import time
from market.data import get_market_snapshot
from strategy.decision_engine import decide_trade
from risk.guardrails import check_trade_allowed
from exchange.orders import place_order
from exchange.ai_log_uploader import upload_ai_log
from utils.logger import get_logger
from config.settings import ALLOWED_SYMBOLS, MAX_OPEN_TRADES, TRADE_NOTIONAL_USDT, TAKE_PROFIT_USDT, STOP_LOSS_USDT

class Trader:
    def __init__(self):
        self.logger = get_logger("TRADER")
        self.open_symbols = set()
        self.positions = {}

    def run(self):
        """
        Main execution loop.
        """
        self.logger.info("Starting Trader Loop...")
        while True:
            for symbol in ALLOWED_SYMBOLS:
                try:
                    self.process_symbol(symbol)
                except Exception as e:
                    self.logger.error(f"Error processing {symbol}: {e}", exc_info=True)
            
            # Wait for next cycle
            self.logger.info("Sleeping for 60 seconds...")
            time.sleep(60)

    def process_symbol(self, symbol: str):
        # 1️⃣ Get market data
        market_snapshot = get_market_snapshot(symbol)
        if not market_snapshot or market_snapshot.get("price", 0) == 0:
            self.logger.warning(f"Skipping {symbol}: market data unavailable.")
            return
        
        # 1.5 Get Account State
        from account.state import get_account_state
        account_state = get_account_state()
        
        # 🛡️ OPEN POSITION CHECKS
        # Prefer exchange-reported positions; fall back to local tracking.
        open_positions = account_state.get("open_positions", [])
        if open_positions:
            self.open_symbols = {p.get("symbol") for p in open_positions if p.get("symbol")}

        position = self.positions.get(symbol)
        has_position = symbol in self.open_symbols or position is not None

        if not has_position and MAX_OPEN_TRADES and len(self.open_symbols) >= MAX_OPEN_TRADES:
            self.logger.info(
                f"Skipping {symbol}: max open trades reached "
                f"({len(self.open_symbols)}/{MAX_OPEN_TRADES})."
            )
            return

        # 2️⃣ AI decision
        price = market_snapshot.get("price", 0.0)
        required_size = round(TRADE_NOTIONAL_USDT / price, 8) if price else 0.0
        pnl_usdt = 0.0
        if position:
            pnl_usdt = (position["entry_price"] - price) * position["size"]
            position["pnl_usdt"] = round(pnl_usdt, 4)

        constraints = {
            "allowed_actions": ["CLOSE", "HOLD"] if position else ["SELL", "HOLD"],
            "required_size": required_size if not position else position["size"],
        }

        decision = decide_trade(
            market_snapshot,
            account_state,
            position=position,
            constraints=constraints,
        )
        decision["price"] = price

        # 3️⃣ Guardrails
        allowed, reason = check_trade_allowed(decision, symbol, account_state)

        order_id = None

        if allowed and decision["action"] != "HOLD":
            self.logger.info(f"Executing {decision['action']} on {symbol}")
            # 4️⃣ Execute order
            side = decision["action"]
            size = decision["size"]
            take_profit = None
            stop_loss = None

            if decision["action"] == "SELL" and price > 0 and size > 0:
                take_profit = round(price - (TAKE_PROFIT_USDT / size), 2)
                stop_loss = round(price + (STOP_LOSS_USDT / size), 2)
            if decision["action"] == "SELL" and (take_profit is None or stop_loss is None):
                self.logger.error("Skipping entry: TP/SL not set.")
                return

            if decision["action"] == "CLOSE":
                side = "BUY"  # Close short position
                size = position["size"] if position else decision["size"]

            order_id = place_order(
                symbol=symbol,
                side=side,
                size=size,
                leverage=decision["leverage"],
                take_profit=take_profit,
                stop_loss=stop_loss,
            )
            if order_id:
                if decision["action"] == "SELL":
                    self.open_symbols.add(symbol)
                    self.positions[symbol] = {
                        "side": "SHORT",
                        "entry_price": price,
                        "size": size,
                        "leverage": decision["leverage"],
                    }
                elif decision["action"] == "CLOSE":
                    self.open_symbols.discard(symbol)
                    self.positions.pop(symbol, None)
        elif not allowed:
            self.logger.warning(f"Trade blocked for {symbol}: {reason}")
        else:
            self.logger.info(f"HOLD decision for {symbol}")

        # 5️⃣ Upload AI log (ALWAYS)
        try:
            upload_ai_log(
                order_id=order_id,
                ai_log=decision["ai_log"]
            )
        except SystemExit:
            # Re-raise to stop the main loop
            self.logger.critical("Stopping Trader due to AI Log Kill Switch.")
            raise
