from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ProjectStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    pending = "pending"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="项目名称")
    code = Column(String(50), unique=True, nullable=True, comment="项目代码")
    code_type = Column(String(50), nullable=True, comment="Code类型，如内部项目/外部项目")
    client = Column(String(200), comment="客户名称")
    competency = Column(String(100), nullable=True, comment="项目Competency，如SAP/前端/数据")
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    hours = Column(Float, nullable=True, comment="小时数")
    progress = Column(Integer, default=0, comment="进度百分比 0-100")
    em_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="EM")
    ep_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="EP")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    em = relationship("Employee", foreign_keys=[em_id])
    ep = relationship("Employee", foreign_keys=[ep_id])
    employee_projects = relationship("EmployeeProject", back_populates="project")
    requirements = relationship("ProjectRequirement", back_populates="project", cascade="all, delete-orphan")
    voc_list = relationship("ProjectVoC", back_populates="project", cascade="all, delete-orphan")


class ProjectRequirement(Base):
    __tablename__ = "project_requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(100), comment="所需角色")
    grade_required = Column(String(20), comment="所需职级")
    headcount = Column(Integer, default=1, comment="需要人数")
    required_skills = Column(String(500), comment="所需技能，逗号分隔")
    start_date = Column(Date, nullable=True)
    status = Column(String(50), default="open", comment="open/filled/cancelled")
    description = Column(Text, nullable=True)
    fiscal_year = Column(String(20), nullable=True, comment="财年，如 FY2025")
    location = Column(String(100), nullable=True, comment="工作地点")
    match_status = Column(String(20), nullable=True, comment="匹配状态：匹配中/已匹配/部分匹配")
    requester = Column(String(100), nullable=True, comment="需求提出者")
    job_content = Column(Text, nullable=True, comment="工作内容")
    request_date = Column(Date, nullable=True, comment="需求提出日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="requirements")
    consultants = relationship("RequirementConsultant", back_populates="requirement", cascade="all, delete-orphan")


class ProjectVoC(Base):
    __tablename__ = "project_voc"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    client_name = Column(String(100), comment="客户名称")
    rating = Column(Integer, comment="评分 1-5")
    comment = Column(Text, nullable=True, comment="详细反馈")
    voc_date = Column(Date, nullable=True, comment="反馈日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="voc_list")


class RequirementConsultant(Base):
    __tablename__ = "requirement_consultants"
    __table_args__ = (UniqueConstraint("requirement_id", "employee_id", name="uq_req_consultant"),)

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("project_requirements.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    requirement = relationship("ProjectRequirement", back_populates="consultants")
    employee = relationship("Employee")
