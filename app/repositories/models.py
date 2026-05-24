from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class CompetitorInsight(Document):
    competitor: str
    is_website: bool
    status: str = "PENDING"  # PENDING, COMPLETED, FAILED
    price_insights: Optional[str] = None
    sentiment_insights: Optional[str] = None
    marketing_insights: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "competitor_insights"
        use_state_holding = True  # Allows tracking state changes easily
