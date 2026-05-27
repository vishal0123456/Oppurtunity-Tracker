"""
Pydantic schemas for Opportunity — request validation and response serialization.

IDs are str (UUID stored as String(36) in the model) for SQLite compatibility.
"""
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime


VALID_CATEGORIES = {
    "scholarship", "fellowship", "accelerator", "vc_program", "grant",
    "competition", "conference", "exhibition", "exchange_program",
    "travel_program", "government_scheme", "giveaway", "other"
}

VALID_STATUSES = {
    "saved", "planning", "applied", "interview", "accepted", "rejected", "waitlisted"
}


class OpportunityBase(BaseModel):
    title: str
    organization: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    country: Optional[List[str]] = []
    is_remote: Optional[bool] = False
    women_friendly: Optional[bool] = False
    india_eligible: Optional[bool] = False
    student_eligible: Optional[bool] = False
    age_limit: Optional[str] = None
    eligibility: Optional[str] = None
    funding_amount: Optional[str] = None
    application_fee: Optional[str] = None
    link: str
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    deadline: Optional[date] = None
    is_expired: Optional[bool] = False


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    country: Optional[List[str]] = None
    is_remote: Optional[bool] = None
    women_friendly: Optional[bool] = None
    india_eligible: Optional[bool] = None
    student_eligible: Optional[bool] = None
    age_limit: Optional[str] = None
    eligibility: Optional[str] = None
    funding_amount: Optional[str] = None
    application_fee: Optional[str] = None
    deadline: Optional[date] = None
    is_expired: Optional[bool] = None


class OpportunityRead(OpportunityBase):
    id: str
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v)

    @field_validator("tags", "country", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return []
        return v

    model_config = {"from_attributes": True}


class OpportunityListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[OpportunityRead]
