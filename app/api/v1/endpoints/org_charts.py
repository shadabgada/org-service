from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.org_chart import OrgChartCreate, OrgChartResponse, OrgChartUpdate
from app.services.org_chart_service import OrgChartService
from app.api.deps import get_db

router = APIRouter()


@router.post("/", response_model=OrgChartResponse, status_code=status.HTTP_201_CREATED)
def create_org_chart(org_chart: OrgChartCreate, db: Session = Depends(get_db)):
    return OrgChartService.create_org_chart(db, org_chart)


@router.get("/", response_model=List[OrgChartResponse])
def read_org_charts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return OrgChartService.get_org_charts(db, skip=skip, limit=limit)


@router.get("/{org_id}", response_model=OrgChartResponse)
def read_org_chart(org_id: int, db: Session = Depends(get_db)):
    org_chart = OrgChartService.get_org_chart(db, org_id)
    if not org_chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return org_chart


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_org_chart(org_id: int, db: Session = Depends(get_db)):
    if not OrgChartService.delete_org_chart(db, org_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return None
