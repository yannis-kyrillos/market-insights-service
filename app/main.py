from dotenv import load_dotenv
load_dotenv()

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing application startup...")
    try:
        logger.info(f"Connecting to MongoDB at: {settings.MONGODB_URL}")
        await init_db(settings.MONGODB_URL)
        logger.info("MongoDB and Beanie ODM initialized successfully.")
    except Exception as e:
        logger.error(f"Critical error during database initialization: {str(e)}", exc_info=True)
        raise e
    
    yield
    
    # Shutdown actions
    logger.info("Shutting down application...")


# Initialize the FastAPI application
app = FastAPI(
    title="Market Insights Service",
    description="REST API to gather competitor pricing, sentiment, and marketing positioning using Google ADK parallel agents.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

# Include v1 REST API endpoints
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["General"])
async def root():
    """Service status checking endpoint."""
    return {
        "status": "online",
        "service": "Market Insights Service",
        "docs_url": "/docs"
    }
