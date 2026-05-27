"""
Application Tracker API — manage user's opportunity application progress.
"""
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.application import UserApplication
from app.models.opportunity import Opportunity
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/applications", tags=["applications"])

VALID_STATUSES = {"saved", "planning", "applied", "interview", "accepted", "rejected", "waitlisted"}


@router.get("", response_model=List[ApplicationRead])
async def list_applications(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all tracked applications, optionally filtered by status."""
    query = (
        select(UserApplication)
        .options(selectinload(UserApplication.opportunity))
        .order_by(UserApplication.created_at.desc())
    )
    if status:
        query = query.where(UserApplication.status == status)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ApplicationRead, status_code=201)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Save/track an opportunity application."""
    if data.status and data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {VALID_STATUSES}")

    opp = await db.get(Opportunity, data.opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    existing = await db.execute(
        select(UserApplication).where(UserApplication.opportunity_id == data.opportunity_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already tracking this opportunity")

    app_obj = UserApplication(**data.model_dump())
    db.add(app_obj)
    await db.flush()

    result = await db.execute(
        select(UserApplication)
        .options(selectinload(UserApplication.opportunity))
        .where(UserApplication.id == app_obj.id)
    )
    return result.scalar_one()

@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single application by ID."""
    result = await db.execute(
        select(UserApplication)
        .options(selectinload(UserApplication.opportunity))
        .where(UserApplication.id == application_id)
    )
    app_obj = result.scalar_one_or_none()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


@router.put("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: str,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update application status, notes, priority, etc."""
    result = await db.execute(
        select(UserApplication)
        .options(selectinload(UserApplication.opportunity))
        .where(UserApplication.id == application_id)
    )
    app_obj = result.scalar_one_or_none()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    if data.status and data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {VALID_STATUSES}")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app_obj, field, value)

    await db.flush()

    # Re-fetch with relationship to avoid lazy-load issues
    result = await db.execute(
        select(UserApplication)
        .options(selectinload(UserApplication.opportunity))
        .where(UserApplication.id == application_id)
    )
    return result.scalar_one()


@router.delete("/{application_id}", status_code=204)
async def delete_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove an application from the tracker."""
    result = await db.execute(
        select(UserApplication).where(UserApplication.id == application_id)
    )
    app_obj = result.scalar_one_or_none()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    await db.delete(app_obj)
