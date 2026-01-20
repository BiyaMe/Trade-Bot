from dotenv import load_dotenv
load_dotenv()

from runner.trader import Trader
from utils.logger import get_logger
from exchange.ai_log_uploader import FAIL_COUNT

logger = get_logger("VALIDATION")

def main():
    logger.info("🚀 Starting Production Logic Validation...")
    
    trader = Trader()
    symbol = "cmt_btcusdt" # Test with one symbol
    
    try:
        logger.info(f"▶️ Processing symbol {symbol}...")
        trader.process_symbol(symbol)
        
        logger.info("✅ process_symbol completed without crashing.")
        
        if FAIL_COUNT == 0:
             logger.info("✅ AI Log Upload appears successful (FAIL_COUNT=0).")
             logger.info("🏆 SYSTEM IS READY FOR PRODUCTION.")
        else:
             logger.error(f"❌ AI Log Upload had failures (FAIL_COUNT={FAIL_COUNT}). Check logs.")

    except Exception as e:
        logger.error(f"❌ Validation Crashed: {e}")
        raise e

if __name__ == "__main__":
    main()
