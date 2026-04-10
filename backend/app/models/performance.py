from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    year = Column(Integer, nullable=False, comment="考核年份")
    quarter = Column(Integer, nullable=True, comment="考核季度 1-4，null 表示年度")
    rating = Column(String(20), comment="绩效评级，如 EX/ME/NI")
    voc_score = Column(Float, comment="VoC 满意度评分")
    comments = Column(Text, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="评审人")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="performances", foreign_keys="Performance.employee_id")
    reviewer = relationship("Employee", foreign_keys="Performance.reviewer_id")
