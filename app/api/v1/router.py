from fastapi import APIRouter
from app.api.v1.endpoints.insights import router as insights_router

api_router = APIRouter()
api_router.include_router(insights_router, prefix="/insights", tags=["Insights"])
