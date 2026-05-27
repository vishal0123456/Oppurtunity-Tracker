"""
Pydantic schemas for UserApplication.

IDs are str (UUID stored as String(36)) for SQLite compatibility.
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime
from app.schemas.opportunity import OpportunityRead


class ApplicationBase(BaseModel):
    opportunity_id: str
    status: Optional[str] = "saved"
    notes: Optional[str] = None
    priority: Optional[int] = 3
    applied_at: Optional[date] = None
    reminder_date: Optional[date] = None
    document_links: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[int] = None
    applied_at: Optional[date] = None
    reminder_date: Optional[date] = None
    document_links: Optional[str] = None


class ApplicationRead(ApplicationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    opportunity: Optional[OpportunityRead] = None

    @field_validator("id", "opportunity_id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v)

    model_config = {"from_attributes": True}
