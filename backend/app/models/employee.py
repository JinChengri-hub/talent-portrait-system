from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class EmployeeStatus(str, enum.Enum):
    on_project = "在项"
    bench = "bench"
    leave = "休假"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    gpn = Column(String(50), unique=True, nullable=False, index=True, comment="全球人员编号，唯一标识")
    name = Column(String(100), nullable=False, comment="姓名")
    name_en = Column(String(100), nullable=True, comment="英文名")
    competency = Column(String(100), comment="所属部门，如 DE/Platforms/RC")
    industry = Column(String(200), nullable=True, comment="擅长行业，如 金融/制造/零售")
    grade = Column(String(20), comment="职级，如 SM/M/S/C")
    location = Column(String(100), comment="当前所在地")
    counsellor_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="指导上级")
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.bench, comment="状态：在项/bench/休假")
    ytd_ut = Column(Float, default=0.0, comment="Year-to-Date UT 利用率（百分比，如 85.0）")
    email = Column(String(200), unique=True, nullable=True)
    join_date = Column(Date, nullable=True, comment="入职日期")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    counsellor = relationship("Employee", remote_side=[id], foreign_keys=[counsellor_id], backref="subordinates")
    employee_projects = relationship("EmployeeProject", back_populates="employee", cascade="all, delete-orphan")
    employee_skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    performances = relationship("Performance", back_populates="employee", cascade="all, delete-orphan", foreign_keys="Performance.employee_id")
    trainings = relationship("TrainingCPE", back_populates="employee", cascade="all, delete-orphan")


class EmployeeProject(Base):
    __tablename__ = "employee_projects"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(100), comment="在项目中的角色")
    team_name = Column(String(200), nullable=True, comment="所支持项目团队")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=True, comment="是否当前项目")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="employee_projects")
    project = relationship("Project", back_populates="employee_projects")


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    level = Column(Integer, default=1, comment="技能等级 1-5")
    certified_date = Column(Date, nullable=True, comment="认证日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="employee_skills")
    skill = relationship("Skill", back_populates="employee_skills")
