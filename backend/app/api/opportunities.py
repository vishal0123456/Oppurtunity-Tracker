"""
Opportunities API — CRUD endpoints with filtering and pagination.
"""
import logging
from typing import Optional
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.opportunity import Opportunity
from app.schemas.opportunity import (
    OpportunityRead, OpportunityListResponse,
    OpportunityCreate, OpportunityUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Returns aggregate stats for the dashboard header."""
    today = date.today()
    week_from_now = today + timedelta(days=7)

    total = (await db.execute(
        select(func.count()).select_from(Opportunity)
    )).scalar_one()

    active = (await db.execute(
        select(func.count()).select_from(Opportunity)
        .where(Opportunity.is_expired == False)
    )).scalar_one()

    expiring_soon = (await db.execute(
        select(func.count()).select_from(Opportunity).where(
            Opportunity.is_expired == False,
            Opportunity.deadline != None,
            Opportunity.deadline <= week_from_now,
            Opportunity.deadline >= today,
        )
    )).scalar_one()

    cat_result = await db.execute(
        select(Opportunity.category, func.count().label("count"))
        .where(Opportunity.is_expired == False)
        .group_by(Opportunity.category)
        .order_by(func.count().desc())
    )
    categories = [{"category": row[0], "count": row[1]} for row in cat_result.all()]

    return {
        "total": total,
        "active": active,
        "expiring_soon": expiring_soon,
        "by_category": categories,
    }


@router.get("", response_model=OpportunityListResponse)
async def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    women_friendly: Optional[bool] = Query(None),
    india_eligible: Optional[bool] = Query(None),
    student_eligible: Optional[bool] = Query(None),
    is_remote: Optional[bool] = Query(None),
    is_expired: Optional[bool] = Query(False),
    deadline_before: Optional[date] = Query(None),
    deadline_after: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List opportunities with optional filters and pagination."""
    query = select(Opportunity)
    conditions = []

    if category:
        conditions.append(Opportunity.category == category)
    if country:
        conditions.append(Opportunity.country.any(country))
    if tag:
        conditions.append(Opportunity.tags.any(tag))
    if women_friendly is not None:
        conditions.append(Opportunity.women_friendly == women_friendly)
    if india_eligible is not None:
        conditions.append(Opportunity.india_eligible == india_eligible)
    if student_eligible is not None:
        conditions.append(Opportunity.student_eligible == student_eligible)
    if is_remote is not None:
        conditions.append(Opportunity.is_remote == is_remote)
    if is_expired is not None:
        conditions.append(Opportunity.is_expired == is_expired)
    if deadline_before:
        conditions.append(Opportunity.deadline <= deadline_before)
    if deadline_after:
        conditions.append(Opportunity.deadline >= deadline_after)
    if search:
        term = f"%{search.lower()}%"
        conditions.append(or_(
            func.lower(Opportunity.title).like(term),
            func.lower(Opportunity.description).like(term),
            func.lower(Opportunity.organization).like(term),
        ))

    if conditions:
        query = query.where(and_(*conditions))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = (
        query
        .order_by(Opportunity.deadline.asc().nulls_last(), Opportunity.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    opportunities = result.scalars().all()

    return OpportunityListResponse(
        total=total, page=page, page_size=page_size, results=opportunities,
    )


@router.get("/search", response_model=OpportunityListResponse)
async def ai_search(
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """AI-powered natural language search."""
    from app.ai.search_assistant import parse_search_query

    filters = await parse_search_query(q)
    logger.info(f"AI search '{q}' → filters: {filters}")

    base_query = select(Opportunity).where(Opportunity.is_expired == False)
    conditions = []

    if filters.get("category"):
        conditions.append(Opportunity.category == filters["category"])
    if filters.get("women_friendly"):
        conditions.append(Opportunity.women_friendly == True)
    if filters.get("india_eligible"):
        conditions.append(Opportunity.india_eligible == True)
    if filters.get("student_eligible"):
        conditions.append(Opportunity.student_eligible == True)
    if filters.get("is_remote"):
        conditions.append(Opportunity.is_remote == True)
    if filters.get("country"):
        country_conditions = [Opportunity.country.any(c) for c in filters["country"]]
        if country_conditions:
            conditions.append(or_(*country_conditions))
    if filters.get("tags"):
        tag_conditions = [Opportunity.tags.any(t) for t in filters["tags"]]
        if tag_conditions:
            conditions.append(or_(*tag_conditions))
    if filters.get("keyword"):
        kw = f"%{filters['keyword'].lower()}%"
        conditions.append(or_(
            func.lower(Opportunity.title).like(kw),
            func.lower(Opportunity.description).like(kw),
            func.lower(Opportunity.organization).like(kw),
        ))

    # Keyword fallback — search individual meaningful words from the query
    stop_words = {"for", "the", "a", "an", "in", "of", "to", "and", "or", "with", "by", "at", "fully", "funded"}
    query_words = [w.lower() for w in q.split() if w.lower() not in stop_words and len(w) > 3]

    fallback_conditions = []
    for word in query_words:
        wk = f"%{word}%"
        fallback_conditions.append(or_(
            func.lower(Opportunity.title).like(wk),
            func.lower(Opportunity.description).like(wk),
            func.lower(Opportunity.eligibility).like(wk),
        ))

    keyword_fallback = or_(*fallback_conditions) if fallback_conditions else None

    if conditions:
        # Try structured filters first
        structured_query = base_query.where(and_(*conditions))
        count_check = select(func.count()).select_from(structured_query.subquery())
        structured_count = (await db.execute(count_check)).scalar_one()

        if structured_count > 0:
            # Structured filters found results — use them
            query = structured_query
        elif keyword_fallback is not None:
            # Structured filters too strict — fall back to keywords
            query = base_query.where(keyword_fallback)
        else:
            query = structured_query
    elif keyword_fallback is not None:
        query = base_query.where(keyword_fallback)
    else:
        query = base_query

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = (
        query
        .order_by(Opportunity.deadline.asc().nulls_last())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    opportunities = result.scalars().all()

    return OpportunityListResponse(
        total=total, page=page, page_size=page_size, results=opportunities,
    )


@router.get("/{opportunity_id}", response_model=OpportunityRead)
async def get_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single opportunity by ID."""
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    await db.refresh(opp)
    return opp


@router.post("/run-pipeline", status_code=202)
async def trigger_pipeline(background_tasks: BackgroundTasks):
    """Manually trigger the scraping pipeline (runs in background)."""
    from app.pipeline.runner import run_pipeline
    background_tasks.add_task(run_pipeline)
    return {"message": "Pipeline started in background. Check logs for progress."}


@router.patch("/{opportunity_id}", response_model=OpportunityRead)
async def patch_opportunity(
    opportunity_id: str,
    data: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partially update an opportunity (admin use)."""
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(opp, field, value)

    await db.flush()
    await db.refresh(opp)
    return opp


@router.post("", response_model=OpportunityRead, status_code=201)
async def create_opportunity(
    data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
):
    """Manually create an opportunity (admin use)."""
    opp = Opportunity(**data.model_dump())
    db.add(opp)
    await db.flush()
    await db.refresh(opp)
    return opp
