from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Enum
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
    client = Column(String(200), comment="客户名称")
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employee_projects = relationship("EmployeeProject", back_populates="project")
    requirements = relationship("ProjectRequirement", back_populates="project", cascade="all, delete-orphan")


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
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="requirements")
