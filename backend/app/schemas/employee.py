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
    name_en: Optional[str] = None
    competency: Optional[str] = None
    grade: Optional[str] = None
    location: Optional[str] = None
    counsellor_name: Optional[str] = None
    counsellor_id: Optional[int] = None
    counsellor_name_en: Optional[str] = None
    counsellor_grade: Optional[str] = None
    counsellor_email: Optional[str] = None
    status: Optional[EmployeeStatus] = None
    ytd_ut: Optional[float] = None
    effective_ut: Optional[float] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    join_date: Optional[date] = None
    skills: List[SkillBrief] = []
    current_project: Optional[ProjectBrief] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SkillInput(BaseModel):
    skill_id: int
    level: int


class ProjectHistoryItem(BaseModel):
    id: int
    project_name: str
    project_code: Optional[str] = None
    role: Optional[str] = None
    team_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False

    class Config:
        from_attributes = True


class TrainingItem(BaseModel):
    id: int
    training_name: str
    training_type: Optional[str] = None
    hours: Optional[float] = None
    start_date: Optional[date] = None
    completed_date: Optional[date] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class PerformanceItem(BaseModel):
    id: int
    year: Optional[int] = None
    quarter: Optional[int] = None
    rating: Optional[str] = None
    voc_score: Optional[float] = None
    comments: Optional[str] = None

    class Config:
        from_attributes = True


class SkillOption(BaseModel):
    id: int
    name: str
    category: Optional[str] = None

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
    phone: Optional[str] = None
    join_date: Optional[date] = None
