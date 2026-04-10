from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.employee import EmployeeStatus


class SkillBrief(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    level: int

    class Config:
        from_attributes = True


class ProjectBrief(BaseModel):
    id: int
    name: str
    code: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeListItem(BaseModel):
    id: int
    gpn: str
    name: str
    competency: Optional[str] = None
    grade: Optional[str] = None
    location: Optional[str] = None
    counsellor_name: Optional[str] = None
    counsellor_id: Optional[int] = None
    status: Optional[EmployeeStatus] = None
    ytd_ut: Optional[float] = None
    current_project: Optional[ProjectBrief] = None

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    total: int
    items: List[EmployeeListItem]


class EmployeeDetail(BaseModel):
    id: int
    gpn: str
    name: str
    competency: Optional[str] = None
    grade: Optional[str] = None
    location: Optional[str] = None
    counsellor_name: Optional[str] = None
    counsellor_id: Optional[int] = None
    status: Optional[EmployeeStatus] = None
    ytd_ut: Optional[float] = None
    email: Optional[str] = None
    join_date: Optional[date] = None
    skills: List[SkillBrief] = []
    current_project: Optional[ProjectBrief] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeCreate(BaseModel):
    gpn: str
    name: str
    competency: Optional[str] = None
    grade: Optional[str] = None
    location: Optional[str] = None
    counsellor_id: Optional[int] = None
    status: Optional[EmployeeStatus] = EmployeeStatus.bench
    ytd_ut: Optional[float] = 0.0
    email: Optional[str] = None
    join_date: Optional[date] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    competency: Optional[str] = None
    grade: Optional[str] = None
    location: Optional[str] = None
    counsellor_id: Optional[int] = None
    status: Optional[EmployeeStatus] = None
    ytd_ut: Optional[float] = None
    email: Optional[str] = None
    join_date: Optional[date] = None
