from typing import List
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, BackgroundTasks, status

from app.dtos.insights_dtos import InsightCreateDTO, InsightResponseDTO, InsightListItemDTO
from app.services.insights_service import InsightsService

router = APIRouter()


@router.post(
    "",
    response_model=InsightResponseDTO,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger competitor market analysis",
    description="Accepts a competitor product name or website URL, initiates parallel agent analysis in the background, and returns the pending insight record."
)
async def create_competitor_insight(
    dto: InsightCreateDTO,
    background_tasks: BackgroundTasks
):
    insight = await InsightsService.create_insight(dto, background_tasks)
    return insight


@router.get(
    "/{insight_id}",
    response_model=InsightResponseDTO,
    summary="Get competitor market analysis details",
    description="Retrieves the detailed status and agent insights for a specific competitor analysis by its ID."
)
async def get_competitor_insight(insight_id: PydanticObjectId):
    insight = await InsightsService.get_insight(insight_id)
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competitor insight with ID {insight_id} not found."
        )
    return insight


@router.get(
    "",
    response_model=List[InsightListItemDTO],
    summary="List all competitor analysis tasks",
    description="Retrieves a list of all competitor analyses that have been requested, sorted by creation date."
)
async def list_competitor_insights():
    insights = await InsightsService.list_insights()
    return insights
