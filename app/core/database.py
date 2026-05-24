from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.repositories.models import CompetitorInsight

async def init_db(mongodb_url: str):
    """Initializes the database connection and registers Beanie models."""
    client = AsyncIOMotorClient(mongodb_url)
    # Beanie handles extracting the DB name from the MongoDB URL (or defaults to the URL path)
    db_name = client.get_default_database().name
    await init_beanie(
        database=client[db_name],
        document_models=[CompetitorInsight]
    )
