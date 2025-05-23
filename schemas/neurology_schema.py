from pydantic import BaseModel
from datetime import datetime


class ReportSummary(BaseModel):
    id: int
    name: str
    created_at: datetime
    summary: str
    full_report: dict

    class Config:
        from_attributes = True
