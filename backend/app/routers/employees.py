from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from typing import Optional
import io
import openpyxl

from app.database import get_db
from app.models.employee import Employee, EmployeeProject, EmployeeSkill
from app.models.project import Project
from app.models.skill import Skill
from app.schemas.employee import EmployeeListResponse, EmployeeListItem, EmployeeDetail, EmployeeCreate, EmployeeUpdate, ProjectBrief, SkillBrief

router = APIRouter(prefix="/api/employees", tags=["employees"])


async def _build_list_item(emp: Employee) -> EmployeeListItem:
    current_project = None
    for ep in emp.employee_projects:
        if ep.is_current and ep.project:
            current_project = ProjectBrief(id=ep.project.id, name=ep.project.name, code=ep.project.code)
            break

    return EmployeeListItem(
        id=emp.id,
        gpn=emp.gpn,
        name=emp.name,
        competency=emp.competency,
        grade=emp.grade,
        location=emp.location,
        counsellor_name=emp.counsellor.name if emp.counsellor else None,
        counsellor_id=emp.counsellor_id,
        status=emp.status,
        ytd_ut=emp.ytd_ut,
        current_project=current_project,
    )


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    keyword: Optional[str] = Query(None, description="姓名或GPN模糊搜索"),
    competency: Optional[str] = Query(None, description="部门筛选"),
    grade: Optional[str] = Query(None, description="职级筛选"),
    skill: Optional[str] = Query(None, description="技能筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Employee)
        .options(
            selectinload(Employee.counsellor),
            selectinload(Employee.employee_projects).selectinload(EmployeeProject.project),
            selectinload(Employee.employee_skills).selectinload(EmployeeSkill.skill),
        )
        .where(Employee.is_active == True)
    )

    if keyword:
        query = query.where(or_(Employee.name.ilike(f"%{keyword}%"), Employee.gpn.ilike(f"%{keyword}%")))
    if competency:
        query = query.where(Employee.competency == competency)
    if grade:
        query = query.where(Employee.grade == grade)
    if status:
        query = query.where(Employee.status == status)
    if skill:
        skill_subq = (
            select(EmployeeSkill.employee_id)
            .join(Skill, EmployeeSkill.skill_id == Skill.id)
            .where(Skill.name.ilike(f"%{skill}%"))
        )
        query = query.where(Employee.id.in_(skill_subq))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    employees = result.scalars().all()

    items = [await _build_list_item(emp) for emp in employees]
    return EmployeeListResponse(total=total, items=items)


@router.get("/filter-options")
async def get_filter_options(db: AsyncSession = Depends(get_db)):
    """返回筛选下拉选项：部门、职级、技能列表"""
    from app.models.project import Project
    projects = await db.execute(
        select(Project.id, Project.name).where(Project.status == "active").order_by(Project.name)
    )
    competencies = await db.execute(
        select(Employee.competency).distinct().where(Employee.competency.isnot(None), Employee.is_active == True)
    )
    grades = await db.execute(
        select(Employee.grade).distinct().where(Employee.grade.isnot(None), Employee.is_active == True)
    )
    locations = await db.execute(
        select(Employee.location).distinct().where(Employee.location.isnot(None), Employee.is_active == True)
    )
    skills = await db.execute(select(Skill.name).order_by(Skill.name))

    return {
        "competencies": sorted([r[0] for r in competencies.all()]),
        "grades": sorted([r[0] for r in grades.all()]),
        "locations": sorted([r[0] for r in locations.all()]),
        "skills": [r[0] for r in skills.all()],
        "statuses": ["在项", "bench", "休假"],
        "projects": [{"id": r[0], "name": r[1]} for r in projects.all()],
    }


@router.get("/export")
async def export_employees(
    keyword: Optional[str] = Query(None),
    competency: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    skill: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """导出员工列表为 Excel（管理员权限，权限校验待接入）"""
    query = (
        select(Employee)
        .options(
            selectinload(Employee.counsellor),
            selectinload(Employee.employee_projects).selectinload(EmployeeProject.project),
        )
        .where(Employee.is_active == True)
    )
    if keyword:
        query = query.where(or_(Employee.name.ilike(f"%{keyword}%"), Employee.gpn.ilike(f"%{keyword}%")))
    if competency:
        query = query.where(Employee.competency == competency)
    if grade:
        query = query.where(Employee.grade == grade)
    if status:
        query = query.where(Employee.status == status)

    result = await db.execute(query)
    employees = result.scalars().all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "员工列表"
    headers = ["GPN", "姓名", "Competency", "职级", "Location", "Counsellor", "状态", "YTD UT%", "当前项目"]
    ws.append(headers)

    for emp in employees:
        current_project = ""
        for ep in emp.employee_projects:
            if ep.is_current and ep.project:
                current_project = ep.project.name
                break
        ws.append([
            emp.gpn, emp.name, emp.competency, emp.grade, emp.location,
            emp.counsellor.name if emp.counsellor else "",
            emp.status.value if emp.status else "",
            f"{emp.ytd_ut:.1f}%" if emp.ytd_ut is not None else "",
            current_project,
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=employees.xlsx"},
    )


@router.get("/{employee_id}", response_model=EmployeeDetail)
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.counsellor),
            selectinload(Employee.employee_projects).selectinload(EmployeeProject.project),
            selectinload(Employee.employee_skills).selectinload(EmployeeSkill.skill),
        )
        .where(Employee.id == employee_id, Employee.is_active == True)
    )
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    current_project = None
    for ep in emp.employee_projects:
        if ep.is_current and ep.project:
            current_project = ProjectBrief(id=ep.project.id, name=ep.project.name, code=ep.project.code)
            break

    skills = [
        SkillBrief(id=es.skill.id, name=es.skill.name, category=es.skill.category, level=es.level)
        for es in emp.employee_skills if es.skill
    ]

    return EmployeeDetail(
        id=emp.id, gpn=emp.gpn, name=emp.name, competency=emp.competency,
        grade=emp.grade, location=emp.location,
        counsellor_name=emp.counsellor.name if emp.counsellor else None,
        counsellor_id=emp.counsellor_id,
        status=emp.status, ytd_ut=emp.ytd_ut, email=emp.email,
        join_date=emp.join_date, skills=skills,
        current_project=current_project, created_at=emp.created_at,
    )


@router.post("", response_model=EmployeeDetail, status_code=201)
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    emp = Employee(**data.model_dump())
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return await get_employee(emp.id, db)


@router.put("/{employee_id}", response_model=EmployeeDetail)
async def update_employee(employee_id: int, data: EmployeeUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)
    await db.commit()
    return await get_employee(employee_id, db)


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_active = False
    await db.commit()
