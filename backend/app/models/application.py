"""
UserApplication ORM model.
"""
import uuid
from sqlalchemy import Column, String, Text, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class UserApplication(Base):
    __tablename__ = "user_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    opportunity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status = Column(String(50), default="saved", nullable=False, index=True)
    notes = Column(Text)
    priority = Column(Integer, default=3)
    applied_at = Column(Date)
    reminder_date = Column(Date)
    document_links = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    opportunity = relationship("Opportunity", back_populates="applications")

    def __repr__(self):
        return f"<UserApplication id={self.id} status={self.status!r}>"
