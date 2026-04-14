from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database import get_db
from app.models.project import Project, ProjectVoC
from app.models.employee import Employee, EmployeeProject, EmployeeSkill
from app.models.skill import Skill

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("")
async def list_projects(
    code: Optional[str] = Query(None),
    code_type: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    em: Optional[str] = Query(None),
    ep: Optional[str] = Query(None),
    competency: Optional[str] = Query(None),
    gpn: Optional[str] = Query(None),
    employee_name: Optional[str] = Query(None),
    employee_competency: Optional[str] = Query(None),
    skill: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    EmAlias = Employee.__table__.alias("em_alias")
    EpAlias = Employee.__table__.alias("ep_alias")

    query = (
        select(Project)
        .options(
            selectinload(Project.em),
            selectinload(Project.ep),
            selectinload(Project.employee_projects)
                .selectinload(EmployeeProject.employee)
                .selectinload(Employee.employee_skills)
                .selectinload(EmployeeSkill.skill),
        )
    )

    if code:
        query = query.where(Project.code.ilike(f"%{code}%"))
    if code_type:
        query = query.where(Project.code_type == code_type)
    if name:
        query = query.where(Project.name.ilike(f"%{name}%"))
    if competency:
        query = query.where(Project.competency == competency)
    if status:
        query = query.where(Project.status == status)

    # EM/EP 姓名筛选
    if em:
        em_subq = select(Employee.id).where(Employee.name.ilike(f"%{em}%"))
        query = query.where(Project.em_id.in_(em_subq))
    if ep:
        ep_subq = select(Employee.id).where(Employee.name.ilike(f"%{ep}%"))
        query = query.where(Project.ep_id.in_(ep_subq))

    # 员工筛选（GPN / 姓名 / Competency / 技能）
    if gpn or employee_name or employee_competency or skill:
        emp_subq = select(EmployeeProject.project_id)
        emp_filter = select(Employee.id)
        if gpn:
            emp_filter = emp_filter.where(Employee.gpn.ilike(f"%{gpn}%"))
        if employee_name:
            emp_filter = emp_filter.where(
                or_(Employee.name.ilike(f"%{employee_name}%"),
                    Employee.name_en.ilike(f"%{employee_name}%"))
            )
        if employee_competency:
            emp_filter = emp_filter.where(Employee.competency == employee_competency)
        if skill:
            skill_emp_ids = (
                select(EmployeeSkill.employee_id)
                .join(Skill, EmployeeSkill.skill_id == Skill.id)
                .where(Skill.name.ilike(f"%{skill}%"))
            )
            emp_filter = emp_filter.where(Employee.id.in_(skill_emp_ids))

        emp_subq = emp_subq.where(
            EmployeeProject.employee_id.in_(emp_filter),
            EmployeeProject.is_current == True,
        )
        query = query.where(Project.id.in_(emp_subq))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    projects = result.scalars().all()

    items = []
    for p in projects:
        members = [ep for ep in p.employee_projects if ep.is_current]
        items.append({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "code_type": p.code_type,
            "competency": p.competency,
            "status": p.status,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "hours": p.hours,
            "progress": p.progress,
            "em_name": p.em.name if p.em else None,
            "ep_name": p.ep.name if p.ep else None,
            "member_count": len(members),
        })

    return {"total": total, "items": items}


@router.get("/filter-options")
async def get_filter_options(db: AsyncSession = Depends(get_db)):
    code_types = await db.execute(
        select(Project.code_type).distinct().where(Project.code_type.isnot(None))
    )
    competencies = await db.execute(
        select(Project.competency).distinct().where(Project.competency.isnot(None))
    )
    emp_competencies = await db.execute(
        select(Employee.competency).distinct().where(Employee.competency.isnot(None), Employee.is_active == True)
    )
    skills = await db.execute(select(Skill.name).order_by(Skill.name))
    return {
        "code_types": [r[0] for r in code_types.all()],
        "competencies": [r[0] for r in competencies.all()],
        "employee_competencies": sorted([r[0] for r in emp_competencies.all()]),
        "skills": [r[0] for r in skills.all()],
        "statuses": ["active", "completed", "pending"],
    }


@router.get("/{project_id}")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.em),
            selectinload(Project.ep),
            selectinload(Project.voc_list),
            selectinload(Project.employee_projects)
                .selectinload(EmployeeProject.employee)
                .selectinload(Employee.counsellor),
            selectinload(Project.employee_projects)
                .selectinload(EmployeeProject.employee)
                .selectinload(Employee.employee_skills)
                .selectinload(EmployeeSkill.skill),
        )
        .where(Project.id == project_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")

    members = []
    for ep in p.employee_projects:
        if not ep.employee or not ep.employee.is_active:
            continue
        emp = ep.employee
        skills = [
            {"name": es.skill.name, "category": es.skill.category}
            for es in emp.employee_skills if es.skill
        ]
        members.append({
            "id": emp.id,
            "name": emp.name,
            "name_en": emp.name_en,
            "gpn": emp.gpn,
            "ytd_ut": emp.ytd_ut,
            "skills": skills,
            "industry": emp.industry,
            "team_name": ep.team_name,
            "role": ep.role,
            "counsellor_name": emp.counsellor.name if emp.counsellor else None,
            "is_current": ep.is_current,
        })

    voc_list = [
        {
            "id": v.id,
            "client_name": v.client_name,
            "rating": v.rating,
            "comment": v.comment,
            "voc_date": v.voc_date.isoformat() if v.voc_date else None,
        }
        for v in sorted(p.voc_list, key=lambda x: x.voc_date or x.created_at, reverse=True)
    ]

    return {
        "id": p.id,
        "name": p.name,
        "code": p.code,
        "code_type": p.code_type,
        "competency": p.competency,
        "client": p.client,
        "status": p.status,
        "start_date": p.start_date.isoformat() if p.start_date else None,
        "end_date": p.end_date.isoformat() if p.end_date else None,
        "hours": p.hours,
        "progress": p.progress,
        "em_name": p.em.name if p.em else None,
        "ep_name": p.ep.name if p.ep else None,
        "members": members,
        "voc_list": voc_list,
    }
