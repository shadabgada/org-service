from pydantic import BaseModel
from typing import Optional

class OrgChartBase(BaseModel):
    name: str

class OrgChartCreate(OrgChartBase):
    pass

class OrgChartUpdate(OrgChartBase):
    pass

class OrgChartResponse(OrgChartBase):
    id: int

    class Config:
        orm_mode = True