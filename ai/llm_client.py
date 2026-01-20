import os
from openai import OpenAI

# Initialize client once
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt: str) -> str:
    """
    Calls OpenAI GPT-4o-mini with the given prompt.
    Uses the new v1.0+ client syntax.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        # Re-raise to be caught by decision_engine's fallback logic
        raise RuntimeError(f"OpenAI API call failed: {e}")
