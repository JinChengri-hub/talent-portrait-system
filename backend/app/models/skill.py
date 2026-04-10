from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="技能名称，如 ABAP/PP/前端")
    category = Column(String(100), comment="技能分类，如 SAP/前端/后端/管理")
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee_skills = relationship("EmployeeSkill", back_populates="skill")
