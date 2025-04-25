from fastapi import APIRouter
from app.api.v1.endpoints import employees, org_charts, data_loader

api_router = APIRouter()
api_router.include_router(org_charts.router, prefix="/orgcharts", tags=["orgcharts"])
api_router.include_router(employees.router, prefix="/orgcharts", tags=["employees"])
api_router.include_router(data_loader.router, prefix="/seed-data", tags=["orgcharts"])
