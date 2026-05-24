from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field

class InsightCreateDTO(BaseModel):
    competitor: str = Field(
        ...,
        min_length=2,
        description="The name of the competitor product or their website URL"
    )

class InsightResponseDTO(BaseModel):
    id: PydanticObjectId
    competitor: str
    is_website: bool
    status: str
    price_insights: Optional[str] = None
    sentiment_insights: Optional[str] = None
    marketing_insights: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

class InsightListItemDTO(BaseModel):
    id: PydanticObjectId
    competitor: str
    is_website: bool
    status: str
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
