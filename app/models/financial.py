from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # income or expense
    category = Column(String, nullable=False)  # like salary, food, rent etc
    date = Column(DateTime, nullable=False)
    notes = Column(String, nullable=True)  # optional description
    is_deleted = Column(Boolean, default=False)  # soft delete
    created_by = Column(Integer, ForeignKey("users.id"))  # which user created this
    created_at = Column(DateTime, default=func.now())