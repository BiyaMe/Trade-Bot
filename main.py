from dotenv import load_dotenv
load_dotenv()

from runner.trader import Trader
from utils.logger import get_logger

if __name__ == "__main__":
    logger = get_logger("MAIN")
    logger.info("Initializing Trade-Bot...")
    
    trader = Trader()
    trader.run()
