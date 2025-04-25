from pydantic import BaseModel, validator
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    title: Optional[str] = None
    manager_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    org_id: int

    @validator('manager_id')
    def validate_manager_id(cls, v):
        if v == 0:  # Example validation
            raise ValueError("manager_id cannot be 0")
        return v

    class Config:
        orm_mode = True