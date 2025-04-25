from sqlalchemy.orm import Session
from app.models.org_chart import OrgChart
from app.schemas.org_chart import OrgChartCreate, OrgChartUpdate

class OrgChartService:
    @staticmethod
    def get_org_chart(db: Session, org_id: int):
        return db.query(OrgChart).filter(OrgChart.id == org_id).first()

    @staticmethod
    def get_org_charts(db: Session, skip: int = 0, limit: int = 100):
        return db.query(OrgChart).offset(skip).limit(limit).all()

    @staticmethod
    def create_org_chart(db: Session, org_chart: OrgChartCreate):
        db_org_chart = OrgChart(**org_chart.dict())
        db.add(db_org_chart)
        db.commit()
        db.refresh(db_org_chart)
        return db_org_chart

    @staticmethod
    def delete_org_chart(db: Session, org_id: int):
        org_chart = db.query(OrgChart).filter(OrgChart.id == org_id).first()
        if org_chart:
            db.delete(org_chart)
            db.commit()
            return True
        return False