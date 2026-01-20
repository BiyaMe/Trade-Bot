import time
from market.data import get_market_snapshot
from strategy.decision_engine import decide_trade
from risk.guardrails import check_trade_allowed
from exchange.orders import place_order
from exchange.ai_log_uploader import upload_ai_log
from utils.logger import get_logger
from config.settings import ALLOWED_SYMBOLS

class Trader:
    def __init__(self):
        self.logger = get_logger("TRADER")

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
        
        # 1.5 Get Account State
        from account.state import get_account_state
        account_state = get_account_state()
        
        # 🛡️ DUPLICATE CHECK: Don't trade if position exists
        # In a real system, we'd check 'open_positions' for 'symbol'
        # Since this is a simple bot, we rely on account_state populated by Exchange
        open_positions = account_state.get("open_positions", [])
        # Assuming open_positions is list of dicts with 'symbol' key
        if any(p.get("symbol") == symbol for p in open_positions):
             self.logger.info(f"Skipping {symbol}: Position already exists.")
             return

        # 2️⃣ AI decision
        decision = decide_trade(market_snapshot, account_state)

        # 3️⃣ Guardrails
        allowed, reason = check_trade_allowed(decision, symbol, account_state)

        order_id = None

        if allowed and decision["action"] != "HOLD":
            self.logger.info(f"Executing {decision['action']} on {symbol}")
            # 4️⃣ Execute order
            order_id = place_order(
                symbol=symbol,
                side=decision["action"],
                size=decision["size"],
                leverage=decision["leverage"]
            )
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
