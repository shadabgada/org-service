from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    org_id = Column(Integer, ForeignKey("org_charts.id", ondelete="CASCADE"), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"))

    org_chart = relationship("OrgChart", back_populates="employees")
    manager = relationship("Employee", remote_side=[id], backref="reports")