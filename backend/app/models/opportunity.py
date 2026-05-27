"""
Opportunity ORM model.

Uses PostgreSQL ARRAY for tags/country (matches the existing DB schema).
For tests (SQLite), the conftest overrides these with JSON columns.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(500), nullable=False, index=True)
    organization = Column(String(300))
    description = Column(Text)

    category = Column(String(100), index=True)
    tags = Column(ARRAY(String), default=list)

    country = Column(ARRAY(String), default=list)
    is_remote = Column(Boolean, default=False)

    women_friendly = Column(Boolean, default=False, index=True)
    india_eligible = Column(Boolean, default=False, index=True)
    student_eligible = Column(Boolean, default=False, index=True)
    age_limit = Column(String(100))
    eligibility = Column(Text)

    funding_amount = Column(String(200))
    application_fee = Column(String(100))

    link = Column(String(2000), unique=True, nullable=False, index=True)
    source_url = Column(String(2000))
    source_name = Column(String(200))

    deadline = Column(Date, index=True)
    is_expired = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    applications = relationship("UserApplication", back_populates="opportunity", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Opportunity id={self.id} title={self.title!r}>"
