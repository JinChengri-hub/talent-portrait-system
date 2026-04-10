from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TrainingStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TrainingCPE(Base):
    __tablename__ = "training_cpe"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    training_name = Column(String(200), nullable=False, comment="培训名称")
    training_type = Column(String(50), comment="类型：CPE/certification/internal/external")
    hours = Column(Float, default=0.0, comment="培训时长（小时）")
    start_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    status = Column(Enum(TrainingStatus), default=TrainingStatus.planned)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="trainings")
