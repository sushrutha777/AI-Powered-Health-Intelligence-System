"""
API v1 router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.chat import router as chat_router
from src.api.v1.endpoints.dashboard import router as dashboard_router
from src.api.v1.endpoints.disease import router as disease_router
from src.api.v1.endpoints.drug import router as drug_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(disease_router)

api_v1_router.include_router(drug_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(dashboard_router)
