from pydantic import BaseModel, Field, field_validator
class DecisionSchema(BaseModel):
    action: str = Field(..., description="Action to take: BUY, SELL, or HOLD")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    leverage: int = Field(..., ge=1, le=20, description="Leverage to use, max 20")
    size: float = Field(
        ...,
        ge=0.0,
        description="Position size scaling factor (e.g. 0.05 for 5%). Use 0 for HOLD.",
    )
    reason: str = Field(..., min_length=10, description="Human-readable explanation for audit logs")

    @field_validator('leverage', mode='before')
    def parse_leverage(cls, v):
        if isinstance(v, str):
            v = v.lower().replace("x", "").strip()
        return int(v)

    @field_validator('action', mode='before')
    def parse_action(cls, v):
        if isinstance(v, str):
            v = v.upper().strip()
        if v not in ["BUY", "SELL", "HOLD", "CLOSE"]:
            raise ValueError("Invalid action")
        return v

    @field_validator("size")
    def validate_size_for_action(cls, v, info):
        action = info.data.get("action")
        if action in ["BUY", "SELL", "CLOSE"] and v <= 0:
            raise ValueError("Size must be > 0 for BUY/SELL/CLOSE")
        return v

