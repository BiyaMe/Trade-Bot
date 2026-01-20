def upload_ai_log(client, decision, market_snapshot):
    payload = {
        "orderId": None,
        "stage": "Decision Making",
        "model": "RuleBased-AI-v1",
        "input": market_snapshot,
        "output": decision,
        "explanation": decision["reason"]
    }

    client.post(
        "/capi/v2/order/uploadAiLog",
        data=payload,
        private=True
    )
