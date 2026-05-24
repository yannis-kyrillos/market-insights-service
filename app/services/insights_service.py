import re
import logging
from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
from fastapi import BackgroundTasks

from app.repositories.models import CompetitorInsight
from app.dtos.insights_dtos import InsightCreateDTO
from app.agents.market_agents import run_market_analysis

logger = logging.getLogger(__name__)


def is_website(competitor: str) -> bool:
    """
    Checks if a competitor string represents a website URL or domain.
    Matches starting with http://, https:// or having domain endings like google.com.
    """
    val = competitor.strip()
    if val.lower().startswith(("http://", "https://")):
        return True
    
    # Simple regex for domains: string.suffix (e.g. apple.com, co.uk, etc.)
    domain_regex = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"
    )
    # Remove protocol if any and port, then match domain name
    clean_val = val.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    return bool(domain_regex.match(clean_val))


async def run_analysis_background(insight_id: PydanticObjectId, competitor: str, is_website: bool):
    """
    Background worker task to trigger the Google ADK parallel agent run
    and update the MongoDB document with findings or error messages.
    """
    logger.info(f"Background task started for Insight ID: {insight_id}")
    insight = await CompetitorInsight.get(insight_id)
    if not insight:
        logger.error(f"Insight document with ID {insight_id} not found.")
        return

    try:
        # Execute parallel agents via Google ADK
        results = await run_market_analysis(competitor, is_website)
        
        # Save results in Beanie model
        insight.price_insights = results.get("price_insights")
        insight.sentiment_insights = results.get("sentiment_insights")
        insight.marketing_insights = results.get("marketing_insights")
        insight.status = "COMPLETED"
        insight.updated_at = datetime.utcnow()
        await insight.save()
        logger.info(f"Background task successfully completed for Insight ID: {insight_id}")
    except Exception as e:
        logger.error(f"Background task failed for Insight ID: {insight_id}. Error: {str(e)}", exc_info=True)
        insight.status = "FAILED"
        insight.error_message = str(e)
        insight.updated_at = datetime.utcnow()
        await insight.save()


class InsightsService:
    @staticmethod
    async def create_insight(dto: InsightCreateDTO, background_tasks: BackgroundTasks) -> CompetitorInsight:
        """
        Creates a new competitor insight document, enqueues the agent work in a background task,
        and returns the pending insight record.
        """
        competitor_input = dto.competitor.strip()
        is_web = is_website(competitor_input)
        
        # Create and persist initial pending record
        insight = CompetitorInsight(
            competitor=competitor_input,
            is_website=is_web,
            status="PENDING"
        )
        await insight.insert()
        
        # Dispatch background task for parallel agents execution
        background_tasks.add_task(
            run_analysis_background,
            insight.id,
            competitor_input,
            is_web
        )
        
        return insight

    @staticmethod
    async def get_insight(insight_id: PydanticObjectId) -> Optional[CompetitorInsight]:
        """Retrieves a single competitor insight from the database."""
        return await CompetitorInsight.get(insight_id)

    @staticmethod
    async def list_insights() -> List[CompetitorInsight]:
        """Retrieves all competitor insights from the database, ordered by creation date."""
        return await CompetitorInsight.find_all().sort(-CompetitorInsight.created_at).to_list()
