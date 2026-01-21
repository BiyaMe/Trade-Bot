import json

from ai.llm_client import call_llm
from ai.schema import DecisionSchema
from utils.logger import get_logger

logger = get_logger("AI_INFERENCE")

from ai.prompt import build_prompt

def run_inference(context: dict) -> dict:
    """
    Calls LLM with provided context and validates against schema.
    """
    # 1. Build Prompt
    prompt_text = build_prompt(context)

    # 2. Call LLM
    try:
        raw_response = call_llm(prompt_text)
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}")

    # 3. Parse & Validate
    try:
        # Assuming LLM returns standard markdown code block or plain JSON
        cleaned_json = raw_response.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned_json)
        
        # Validation
        validated = DecisionSchema(**data)
        result = validated.model_dump() # Pydantic v2
        
        # Attach Metadata for logging
        result["ai_log"] = {
            "stage": "Decision Making",
            "model": "gpt-4o-mini",
            "input": context, # Pass full dict
            "output": result.copy(), # Pass full dict
            "explanation": result.get("reason", "")
        }
        
        return result

    except Exception as e:
        logger.error(f"Validation failed: {e}. Raw: {raw_response}")
        raise ValueError(f"Invalid AI response: {e}")
