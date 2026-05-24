import pytest
from unittest.mock import AsyncMock, patch
from beanie import PydanticObjectId

from app.services.insights_service import is_website, run_analysis_background
from app.repositories.models import CompetitorInsight

# Define test cases for website detection logic
@pytest.mark.parametrize(
    "competitor,expected",
    [
        ("https://google.com", True),
        ("http://localhost:8000", True),
        ("notion.so", True),
        ("subdomain.company.co.uk", True),
        ("Slack", False),
        ("Microsoft Teams", False),
        ("Linear App", False),
    ],
)
def test_is_website(competitor, expected):
    assert is_website(competitor) is expected


@pytest.mark.asyncio
@patch("app.services.insights_service.run_market_analysis", new_callable=AsyncMock)
@patch("app.repositories.models.CompetitorInsight.get", new_callable=AsyncMock)
async def test_run_analysis_background_success(mock_get_insight, mock_run_market_analysis):
    # Mock database object
    mock_insight = AsyncMock(spec=CompetitorInsight)
    mock_insight.id = PydanticObjectId()
    mock_insight.competitor = "https://google.com"
    mock_insight.is_website = True
    mock_insight.status = "PENDING"
    mock_insight.price_insights = None
    mock_insight.sentiment_insights = None
    mock_insight.marketing_insights = None
    
    mock_get_insight.return_value = mock_insight
    
    # Mock agent outputs
    mock_run_market_analysis.return_value = {
        "price_insights": "Price is free.",
        "sentiment_insights": "Users are happy.",
        "marketing_insights": "Good marketing."
    }

    # Execute background worker
    await run_analysis_background(mock_insight.id, mock_insight.competitor, mock_insight.is_website)
    
    # Assert database getters and setters were called correctly
    mock_get_insight.assert_called_once_with(mock_insight.id)
    mock_run_market_analysis.assert_called_once_with("https://google.com", True)
    
    assert mock_insight.price_insights == "Price is free."
    assert mock_insight.sentiment_insights == "Users are happy."
    assert mock_insight.marketing_insights == "Good marketing."
    assert mock_insight.status == "COMPLETED"
    mock_insight.save.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.insights_service.run_market_analysis", new_callable=AsyncMock)
@patch("app.repositories.models.CompetitorInsight.get", new_callable=AsyncMock)
async def test_run_analysis_background_failure(mock_get_insight, mock_run_market_analysis):
    # Mock database object
    mock_insight = AsyncMock(spec=CompetitorInsight)
    mock_insight.id = PydanticObjectId()
    mock_insight.competitor = "Slack"
    mock_insight.is_website = False
    mock_insight.status = "PENDING"
    
    mock_get_insight.return_value = mock_insight
    
    # Make parallel agents raise an exception (e.g. API key invalid / network issue)
    mock_run_market_analysis.side_effect = Exception("API Connection Failed")

    # Execute background worker
    await run_analysis_background(mock_insight.id, mock_insight.competitor, mock_insight.is_website)
    
    # Assert database getters and setters were called correctly
    mock_get_insight.assert_called_once_with(mock_insight.id)
    mock_run_market_analysis.assert_called_once_with("Slack", False)
    
    assert mock_insight.status == "FAILED"
    assert mock_insight.error_message == "API Connection Failed"
    mock_insight.save.assert_called_once()
