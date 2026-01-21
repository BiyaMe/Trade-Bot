from ai.inference import run_inference
from utils.logger import get_logger

logger = get_logger("DECISION_ENGINE")

def decide_trade(market_snapshot: dict, account_state: dict, position: dict | None = None, constraints: dict | None = None) -> dict:
    """
    Orchestrates the AI decision process.
    1. Prepares inputs from market and account state.
    2. Calls AI inference layer.
    3. Returns a validated trading decision.
    """
    
    symbol = market_snapshot.get("symbol", "UNKNOWN")

    # Prepare enriched context for AI
    context = {
        "market": market_snapshot,
        "account": account_state,
        "position": position or {},
        "constraints": constraints or {},
    }

    logger.info(f"Requesting AI decision for {symbol}...")

    # 1️⃣ Call AI Inference
    try:
        # Pass the full context to run_inference
        # run_inference will call build_prompt(context)
        decision = run_inference(context)
        
        # Ensure decision has 'ai_log' populated correctly by inference.py
        if "ai_log" not in decision:
             decision["ai_log"] = {
                 "stage": "Decision Making",
                 "model": "gpt-4o-mini",
                 "input": context, # Pass pure dict, not string
                 "output": decision, # Pass pure dict, not string
                 "explanation": decision.get("reason", "No reason provided")
             }
             
    except Exception as e:
        logger.error(f"AI Inference failed for {symbol}: {e}")
        # Fallback to safe HOLD on error
        return {
            "action": "HOLD",
            "confidence": 0.0,
            "leverage": 1,
            "size": 0.0,
            "reason": f"System Error: {str(e)}",
            "ai_log": {
                "stage": "Error Handling",
                "model": "System",
                "input": str(context), 
                "output": {"error": str(e)},
                "explanation": "Fallback due to inference exception"
            }
        }

    return decision


