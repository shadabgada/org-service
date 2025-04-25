from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class OrgChart(Base):
    __tablename__ = "org_charts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    employees = relationship("Employee", back_populates="org_chart", cascade="all, delete-orphan")