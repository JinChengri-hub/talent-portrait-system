from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.models.project import Project, ProjectRequirement, RequirementConsultant
from app.models.employee import Employee
from app.models.skill import Skill


class RequirementUpdate(BaseModel):
    project_name: Optional[str] = None
    competency: Optional[str] = None
    opportunity_type: Optional[str] = None
    ep_id: Optional[int] = None
    em_id: Optional[int] = None
    project_start_date: Optional[str] = None
    project_end_date: Optional[str] = None
    headcount: Optional[int] = None
    required_skills: Optional[str] = None
    fiscal_year: Optional[str] = None
    location: Optional[str] = None
    match_status: Optional[str] = None
    description: Optional[str] = None
    job_content: Optional[str] = None
    requester: Optional[str] = None
    request_date: Optional[str] = None
    consultant_ids: Optional[List[int]] = None


class RequirementCreate(BaseModel):
    project_name: str
    competency: Optional[str] = None
    opportunity_type: Optional[str] = None
    headcount: int
    required_skills: str
    fiscal_year: Optional[str] = None
    location: Optional[str] = None
    match_status: Optional[str] = None
    description: Optional[str] = None

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


@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project.id, Project.name, Project.competency, Project.code_type)
        .order_by(Project.name)
    )
    return [
        {"id": r[0], "name": r[1], "competency": r[2], "code_type": r[3]}
        for r in result.all()
    ]


@router.post("")
async def create_requirement(body: RequirementCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).where(Project.name == body.project_name)
    )
    project = result.scalar_one_or_none()
    if not project:
        project = Project(name=body.project_name, competency=body.competency, code_type=body.opportunity_type)
        db.add(project)
        await db.flush()
    else:
        if body.competency and not project.competency:
            project.competency = body.competency
        if body.opportunity_type and not project.code_type:
            project.code_type = body.opportunity_type
    req = ProjectRequirement(
        project_id=project.id,
        headcount=body.headcount,
        required_skills=body.required_skills,
        fiscal_year=body.fiscal_year,
        location=body.location,
        match_status=body.match_status,
        description=body.description,
        status="open",
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return {"id": req.id, "message": "created"}


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
            "project_type": p.project_type if p else None,
            "opportunity_type": p.code_type if p else None,
            "competency": p.competency if p else None,
            "ep_id": p.ep_id if p else None,
            "ep_name": p.ep.name if p and p.ep else None,
            "em_id": p.em_id if p else None,
            "em_name": p.em.name if p and p.em else None,
            "project_start_date": p.start_date.isoformat() if p and p.start_date else None,
            "project_end_date": p.end_date.isoformat() if p and p.end_date else None,
            "consultants": [
                {"id": c.employee.id, "name": c.employee.name}
                for c in r.consultants if c.employee
            ],
        })

    return {"total": total, "items": items}


@router.put("/{requirement_id}")
async def update_requirement(requirement_id: int, body: RequirementUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectRequirement).where(ProjectRequirement.id == requirement_id)
        .options(selectinload(ProjectRequirement.project))
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # 更新需求字段
    if body.headcount is not None:
        req.headcount = body.headcount
    if body.required_skills is not None:
        req.required_skills = body.required_skills
    if body.fiscal_year is not None:
        req.fiscal_year = body.fiscal_year
    if body.location is not None:
        req.location = body.location
    if body.match_status is not None:
        req.match_status = body.match_status
    if body.description is not None:
        req.description = body.description
    if body.job_content is not None:
        req.job_content = body.job_content
    if body.requester is not None:
        req.requester = body.requester
    if body.request_date is not None:
        from datetime import date
        req.request_date = date.fromisoformat(body.request_date) if body.request_date else None

    # 更新关联项目字段
    if req.project:
        if body.project_name:
            req.project.name = body.project_name
        if body.competency:
            req.project.competency = body.competency
        if body.opportunity_type:
            req.project.code_type = body.opportunity_type
        if body.ep_id is not None:
            req.project.ep_id = body.ep_id if body.ep_id != 0 else None
        if body.em_id is not None:
            req.project.em_id = body.em_id if body.em_id != 0 else None
        if body.project_start_date is not None:
            from datetime import date as date_type
            req.project.start_date = date_type.fromisoformat(body.project_start_date) if body.project_start_date else None
        if body.project_end_date is not None:
            from datetime import date as date_type
            req.project.end_date = date_type.fromisoformat(body.project_end_date) if body.project_end_date else None

    # 更新推荐顾问
    if body.consultant_ids is not None:
        existing = await db.execute(
            select(RequirementConsultant).where(RequirementConsultant.requirement_id == requirement_id)
        )
        for c in existing.scalars().all():
            await db.delete(c)
        await db.flush()
        for emp_id in body.consultant_ids:
            db.add(RequirementConsultant(requirement_id=requirement_id, employee_id=emp_id))

    await db.commit()
    return {"message": "updated"}


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
