from exchange.weex_client import WeexClient
from utils.logger import get_logger
import json

logger = get_logger("AI_LOG")
client = WeexClient.from_env()

FAIL_COUNT = 0
MAX_FAILURES = 3

def upload_ai_log(order_id: str, ai_log: dict):
    """
    Uploads AI log to WEEX validation endpoint.
    Payload must match competition specs.
    HALTS TRADING if repeated failures occur.
    """
    global FAIL_COUNT
    
    try:
        # Prepare Payload
        # NOTE: input/output MUST represent dicts. If they come as strings, user must fix upstream.
        # Check types explicitly to prevent serialization errors or API rejection.
        _input = ai_log.get("input", {})
        if not isinstance(_input, dict):
            _input = {"raw": str(_input)}
            
        _output = ai_log.get("output", {})
        if not isinstance(_output, dict):
            _output = {"raw": str(_output)}

        # Explanation length check (max 1000)
        expl = ai_log.get("explanation", "No explanation provided")
        if len(expl) > 1000:
            expl = expl[:997] + "..."

        payload = {
            "orderId": order_id if order_id else None,
            "stage": ai_log.get("stage", "Decision Making"),
            "model": ai_log.get("model", "gpt-4o-mini"),
            "input": _input,
            "output": _output,
            "explanation": expl
        }
        
        # DEBUG: Print exact payload so user can verify structure in logs
        logger.debug(f"AI_LOG_PAYLOAD: {json.dumps(payload, default=str)}")

        # Use the specific from_env client which has credentials
        response = client.post("/capi/v2/order/uploadAiLog", payload)
        
        if response.get("code") == "00000":
             logger.info(f"AI Log uploaded orderId={order_id} (Success)")
             FAIL_COUNT = 0 # Reset on success
        else:
            logger.error(f"AI Log Upload Failed: {response}")
            FAIL_COUNT += 1

    except Exception as e:
        logger.error(f"Failed to upload AI log: {e}")
        FAIL_COUNT += 1

    # CRITICAL: Disqualification Protection
    if FAIL_COUNT >= MAX_FAILURES:
        msg = f"CRITICAL: AI Logging failed {FAIL_COUNT} times. Stopping bot to prevent disqualification."
        logger.critical(msg)
        raise SystemExit(msg)
