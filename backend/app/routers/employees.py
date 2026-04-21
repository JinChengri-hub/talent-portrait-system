import os
import time
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List
import io
import openpyxl

from app.database import get_db
from app.models.employee import Employee, EmployeeProject, EmployeeSkill
from app.models.project import Project
from app.models.skill import Skill
from app.models.training import TrainingCPE
from app.models.performance import Performance
from app.schemas.employee import (
    EmployeeListResponse, EmployeeListItem, EmployeeDetail, EmployeeCreate,
    EmployeeUpdate, ProjectBrief, SkillBrief, SkillInput, SkillOption,
    ProjectHistoryItem, TrainingItem, PerformanceItem,
)

router = APIRouter(prefix="/api/employees", tags=["employees"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB


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

    query = query.order_by(Employee.gpn)

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


@router.get("/skill-options", response_model=List[SkillOption])
async def get_skill_options(db: AsyncSession = Depends(get_db)):
    """返回技能字典，用于技能选择下拉框"""
    result = await db.execute(select(Skill).order_by(Skill.category, Skill.name))
    skills = result.scalars().all()
    return [SkillOption(id=s.id, name=s.name, category=s.category) for s in skills]


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

    counsellor = emp.counsellor
    return EmployeeDetail(
        id=emp.id, gpn=emp.gpn, name=emp.name, name_en=emp.name_en,
        competency=emp.competency, grade=emp.grade, location=emp.location,
        counsellor_name=counsellor.name if counsellor else None,
        counsellor_id=emp.counsellor_id,
        counsellor_name_en=counsellor.name_en if counsellor else None,
        counsellor_grade=counsellor.grade if counsellor else None,
        counsellor_email=counsellor.email if counsellor else None,
        status=emp.status, ytd_ut=emp.ytd_ut, effective_ut=emp.effective_ut,
        email=emp.email, phone=emp.phone, avatar_url=emp.avatar_url,
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


@router.post("/{employee_id}/avatar")
async def upload_avatar(
    employee_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WebP images are allowed")

    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="File size must not exceed 2MB")

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{employee_id}_{int(time.time())}.{ext}"
    save_path = os.path.join("uploads", "avatars", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(content)

    avatar_url = f"/uploads/avatars/{filename}"
    emp.avatar_url = avatar_url
    await db.commit()
    return {"avatar_url": avatar_url}


@router.put("/{employee_id}/skills")
async def update_skills(
    employee_id: int,
    skills: List[SkillInput],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # deduplicate by skill_id, last one wins
    seen = {}
    for s in skills:
        seen[s.skill_id] = s
    unique_skills = list(seen.values())

    await db.execute(
        delete(EmployeeSkill).where(EmployeeSkill.employee_id == employee_id)
    )
    await db.flush()

    for s in unique_skills:
        db.add(EmployeeSkill(employee_id=employee_id, skill_id=s.skill_id, level=s.level))

    await db.commit()
    return {"message": "Skills updated"}


@router.get("/{employee_id}/projects", response_model=List[ProjectHistoryItem])
async def get_employee_projects(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EmployeeProject)
        .options(selectinload(EmployeeProject.project))
        .where(EmployeeProject.employee_id == employee_id)
        .order_by(EmployeeProject.is_current.desc(), EmployeeProject.start_date.desc())
    )
    eps = result.scalars().all()
    return [
        ProjectHistoryItem(
            id=ep.id,
            project_name=ep.project.name if ep.project else "",
            project_code=ep.project.code if ep.project else None,
            role=ep.role,
            team_name=ep.team_name,
            start_date=ep.start_date,
            end_date=ep.end_date,
            is_current=ep.is_current or False,
        )
        for ep in eps
    ]


@router.get("/{employee_id}/trainings", response_model=List[TrainingItem])
async def get_employee_trainings(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TrainingCPE)
        .where(TrainingCPE.employee_id == employee_id)
        .order_by(TrainingCPE.start_date.desc())
    )
    trainings = result.scalars().all()
    return [
        TrainingItem(
            id=t.id,
            training_name=t.training_name,
            training_type=t.training_type,
            hours=t.hours,
            start_date=t.start_date,
            completed_date=t.completed_date,
            status=t.status.value if t.status else None,
        )
        for t in trainings
    ]


@router.get("/{employee_id}/performances", response_model=List[PerformanceItem])
async def get_employee_performances(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Performance)
        .where(Performance.employee_id == employee_id)
        .order_by(Performance.year.desc(), Performance.quarter.desc())
    )
    performances = result.scalars().all()
    return [
        PerformanceItem(
            id=p.id,
            year=p.year,
            quarter=p.quarter,
            rating=p.rating,
            voc_score=p.voc_score,
            comments=p.comments,
        )
        for p in performances
    ]
