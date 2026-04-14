from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List

from app.database import get_db
from app.models.project import Project, ProjectRequirement, RequirementConsultant
from app.models.employee import Employee
from app.models.skill import Skill

router = APIRouter(prefix="/api/requirements", tags=["requirements"])


@router.get("/filter-options")
async def get_filter_options(db: AsyncSession = Depends(get_db)):
    fiscal_years = await db.execute(
        select(ProjectRequirement.fiscal_year).distinct()
        .where(ProjectRequirement.fiscal_year.isnot(None))
        .order_by(ProjectRequirement.fiscal_year.desc())
    )
    competencies = await db.execute(
        select(Project.competency).distinct()
        .where(Project.competency.isnot(None))
    )
    project_types = await db.execute(
        select(Project.code_type).distinct()
        .where(Project.code_type.isnot(None))
    )
    locations = await db.execute(
        select(ProjectRequirement.location).distinct()
        .where(ProjectRequirement.location.isnot(None))
    )
    match_statuses = await db.execute(
        select(ProjectRequirement.match_status).distinct()
        .where(ProjectRequirement.match_status.isnot(None))
    )
    skills = await db.execute(select(Skill.name).order_by(Skill.name))

    return {
        "fiscal_years": [r[0] for r in fiscal_years.all()],
        "competencies": sorted([r[0] for r in competencies.all()]),
        "project_types": [r[0] for r in project_types.all()],
        "locations": sorted([r[0] for r in locations.all()]),
        "match_statuses": [r[0] for r in match_statuses.all()],
        "skills": [r[0] for r in skills.all()],
    }


@router.get("")
async def list_requirements(
    fiscal_year: Optional[str] = Query(None),
    competency: Optional[str] = Query(None),
    project_type: Optional[str] = Query(None),
    skill: Optional[List[str]] = Query(None),
    headcount_range: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    match_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    # Build base query without selectinload (selectinload cannot be serialized into subquery for count)
    base_query = (
        select(ProjectRequirement)
        .join(ProjectRequirement.project)
    )

    if fiscal_year:
        base_query = base_query.where(ProjectRequirement.fiscal_year == fiscal_year)
    if location:
        base_query = base_query.where(ProjectRequirement.location == location)
    if match_status:
        base_query = base_query.where(ProjectRequirement.match_status == match_status)
    if skill:
        base_query = base_query.where(
            or_(*[ProjectRequirement.required_skills.ilike(f"%{s}%") for s in skill])
        )
    if competency:
        base_query = base_query.where(Project.competency == competency)
    if project_type:
        base_query = base_query.where(Project.code_type == project_type)
    if headcount_range:
        if headcount_range == "1-5":
            base_query = base_query.where(ProjectRequirement.headcount.between(1, 5))
        elif headcount_range == "6-10":
            base_query = base_query.where(ProjectRequirement.headcount.between(6, 10))
        elif headcount_range == "11-20":
            base_query = base_query.where(ProjectRequirement.headcount.between(11, 20))
        elif headcount_range == "20+":
            base_query = base_query.where(ProjectRequirement.headcount > 20)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Add selectinload options for data fetch (separate from count query)
    query = base_query.options(
        selectinload(ProjectRequirement.project)
            .selectinload(Project.em),
        selectinload(ProjectRequirement.project)
            .selectinload(Project.ep),
        selectinload(ProjectRequirement.consultants)
            .selectinload(RequirementConsultant.employee),
    ).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    reqs = result.scalars().all()

    items = []
    for r in reqs:
        p = r.project
        items.append({
            "id": r.id,
            "request_date": r.request_date.isoformat() if r.request_date else None,
            "requester": r.requester,
            "fiscal_year": r.fiscal_year,
            "location": r.location,
            "match_status": r.match_status,
            "headcount": r.headcount,
            "required_skills": r.required_skills,
            "description": r.description,
            "job_content": r.job_content,
            "project_id": p.id if p else None,
            "project_name": p.name if p else None,
            "project_type": p.code_type if p else None,
            "competency": p.competency if p else None,
            "ep_name": p.ep.name if p and p.ep else None,
            "em_name": p.em.name if p and p.em else None,
            "project_start_date": p.start_date.isoformat() if p and p.start_date else None,
            "project_end_date": p.end_date.isoformat() if p and p.end_date else None,
            "consultants": [
                {"id": c.employee.id, "name": c.employee.name}
                for c in r.consultants if c.employee
            ],
        })

    return {"total": total, "items": items}


@router.delete("/{requirement_id}")
async def delete_requirement(requirement_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectRequirement).where(ProjectRequirement.id == requirement_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    await db.delete(req)
    await db.commit()
    return {"message": "deleted"}
