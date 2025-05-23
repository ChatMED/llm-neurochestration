from fastapi import APIRouter

from api.routers import neurology

api_router = APIRouter()
api_router.include_router(neurology.router)