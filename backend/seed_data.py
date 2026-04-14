"""
测试数据种子脚本
运行方式：cd backend && python seed_data.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

# 直接使用数据库 URL，不依赖 .env 加载
DATABASE_URL = "postgresql+asyncpg://postgres:ey123456@localhost:5432/talent_portrait"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

from app.database import Base
from app.models.skill import Skill
from app.models.project import Project, ProjectRequirement, ProjectStatus
from app.models.employee import Employee, EmployeeProject, EmployeeSkill, EmployeeStatus
from app.models.performance import Performance
from app.models.training import TrainingCPE, TrainingStatus


async def clear_data(session: AsyncSession):
    """清空已有测试数据（按外键顺序）"""
    tables = [
        "training_cpe", "performance", "employee_skills",
        "employee_projects", "project_requirements",
        "employees", "projects", "skills"
    ]
    for table in tables:
        await session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
    await session.commit()
    print("已清空旧数据")


async def seed(session: AsyncSession):
    # ------------------------------------------------------------------ #
    # 1. 技能
    # ------------------------------------------------------------------ #
    skills_data = [
        # SAP 模块
        ("ABAP", "SAP", "SAP 开发语言"),
        ("SAP MM", "SAP", "物料管理模块"),
        ("SAP SD", "SAP", "销售与分销模块"),
        ("SAP FI/CO", "SAP", "财务与控制模块"),
        ("SAP PP", "SAP", "生产计划模块"),
        ("SAP WM/EWM", "SAP", "仓储管理模块"),
        ("SAP BTP", "SAP", "Business Technology Platform"),
        ("SAP S/4HANA", "SAP", "S/4HANA 实施与迁移"),
        # 前端
        ("Vue.js", "前端", "Vue 前端框架"),
        ("React", "前端", "React 前端框架"),
        # 后端
        ("Python", "后端", "Python 开发"),
        ("Java", "后端", "Java 开发"),
        # 数据
        ("SQL", "数据", "数据库查询"),
        ("Power BI", "数据", "数据可视化"),
        ("Python 数据分析", "数据", "pandas/numpy 数据分析"),
        # 管理
        ("项目管理", "管理", "PMP / 项目管理能力"),
        ("需求分析", "管理", "业务需求分析与文档"),
        ("变革管理", "管理", "OCM 组织变革管理"),
    ]
    skills = []
    for name, category, desc in skills_data:
        s = Skill(name=name, category=category, description=desc)
        session.add(s)
        skills.append(s)
    await session.flush()
    skill_map = {s.name: s for s in skills}
    print(f"  技能：{len(skills)} 条")

    # ------------------------------------------------------------------ #
    # 2. 项目
    # ------------------------------------------------------------------ #
    projects_data = [
        ("某央企 SAP S/4HANA 全国推广", "PRJ-2024-001", "某央企集团", ProjectStatus.active,
         date(2024, 3, 1), date(2025, 6, 30), "SAP S/4HANA 全国范围推广实施，覆盖 30+ 子公司"),
        ("某零售集团 SAP MM/WM 实施", "PRJ-2024-002", "某零售集团", ProjectStatus.active,
         date(2024, 6, 1), date(2025, 3, 31), "物料与仓储模块全新实施"),
        ("某制造企业 SAP PP 优化", "PRJ-2023-015", "某制造企业", ProjectStatus.completed,
         date(2023, 1, 1), date(2023, 12, 31), "生产计划模块性能优化与流程改造"),
        ("某金融机构数字化转型", "PRJ-2024-003", "某金融机构", ProjectStatus.active,
         date(2024, 9, 1), date(2026, 3, 31), "全行数字化转型战略咨询与实施"),
        ("某能源集团 ERP 预研", "PRJ-2025-001", "某能源集团", ProjectStatus.pending,
         date(2025, 4, 1), date(2025, 9, 30), "SAP S/4HANA 上云可行性评估"),
    ]
    projects = []
    for name, code, client, status, sd, ed, desc in projects_data:
        p = Project(name=name, code=code, client=client, status=status,
                    start_date=sd, end_date=ed, description=desc)
        session.add(p)
        projects.append(p)
    await session.flush()
    print(f"  项目：{len(projects)} 条")

    # 项目需求
    reqs_data = [
        (projects[0], "SAP ABAP 开发顾问", "S", 3, "ABAP,SAP S/4HANA", date(2024, 3, 1)),
        (projects[0], "SAP MM 功能顾问", "M", 2, "SAP MM,需求分析", date(2024, 3, 1)),
        (projects[0], "项目经理", "SM", 1, "项目管理,变革管理", date(2024, 3, 1)),
        (projects[1], "SAP WM/EWM 顾问", "S", 2, "SAP WM/EWM,SAP MM", date(2024, 6, 1)),
        (projects[3], "变革管理顾问", "M", 2, "变革管理,需求分析", date(2024, 9, 1)),
        (projects[4], "解决方案架构师", "SM", 1, "SAP S/4HANA,项目管理", date(2025, 4, 1)),
    ]
    for proj, role, grade, hc, skills_str, sd in reqs_data:
        r = ProjectRequirement(project_id=proj.id, role=role, grade_required=grade,
                               headcount=hc, required_skills=skills_str,
                               start_date=sd, status="open")
        session.add(r)
    await session.flush()

    # ------------------------------------------------------------------ #
    # 3. 员工（先建高级别作为 counsellor）
    # ------------------------------------------------------------------ #
    # 先创建 SM 级别作为上级
    mgr1 = Employee(
        gpn="GPN-SM-001", name="李明远", competency="DE",
        grade="SM", location="上海", status=EmployeeStatus.on_project,
        ytd_ut=92.5, email="lmy@example.com", join_date=date(2015, 7, 1)
    )
    mgr2 = Employee(
        gpn="GPN-SM-002", name="张晓华", competency="Platforms",
        grade="SM", location="北京", status=EmployeeStatus.on_project,
        ytd_ut=88.0, email="zxh@example.com", join_date=date(2016, 3, 15)
    )
    mgr3 = Employee(
        gpn="GPN-SM-003", name="王芳", competency="RC",
        grade="SM", location="深圳", status=EmployeeStatus.on_project,
        ytd_ut=85.5, email="wf@example.com", join_date=date(2017, 1, 10)
    )
    session.add_all([mgr1, mgr2, mgr3])
    await session.flush()

    # M 级别
    m_employees = [
        Employee(gpn="GPN-M-001", name="陈建国", competency="DE", grade="M",
                 location="上海", counsellor_id=mgr1.id, status=EmployeeStatus.on_project,
                 ytd_ut=95.0, email="cjg@example.com", join_date=date(2018, 9, 1)),
        Employee(gpn="GPN-M-002", name="刘思远", competency="DE", grade="M",
                 location="上海", counsellor_id=mgr1.id, status=EmployeeStatus.on_project,
                 ytd_ut=87.5, email="lsy@example.com", join_date=date(2019, 3, 1)),
        Employee(gpn="GPN-M-003", name="赵雨婷", competency="Platforms", grade="M",
                 location="北京", counsellor_id=mgr2.id, status=EmployeeStatus.bench,
                 ytd_ut=62.0, email="zyt@example.com", join_date=date(2019, 6, 15)),
        Employee(gpn="GPN-M-004", name="孙浩然", competency="RC", grade="M",
                 location="深圳", counsellor_id=mgr3.id, status=EmployeeStatus.on_project,
                 ytd_ut=91.0, email="shr@example.com", join_date=date(2018, 1, 8)),
    ]
    session.add_all(m_employees)
    await session.flush()

    # S 级别
    s_employees = [
        Employee(gpn="GPN-S-001", name="周文博", competency="DE", grade="S",
                 location="上海", counsellor_id=m_employees[0].id, status=EmployeeStatus.on_project,
                 ytd_ut=98.0, email="zwb@example.com", join_date=date(2021, 7, 1)),
        Employee(gpn="GPN-S-002", name="吴晓敏", competency="DE", grade="S",
                 location="上海", counsellor_id=m_employees[0].id, status=EmployeeStatus.on_project,
                 ytd_ut=89.0, email="wxm@example.com", join_date=date(2021, 9, 15)),
        Employee(gpn="GPN-S-003", name="郑凯", competency="DE", grade="S",
                 location="北京", counsellor_id=m_employees[1].id, status=EmployeeStatus.bench,
                 ytd_ut=55.0, email="zk@example.com", join_date=date(2022, 3, 1)),
        Employee(gpn="GPN-S-004", name="冯丽", competency="Platforms", grade="S",
                 location="北京", counsellor_id=m_employees[2].id, status=EmployeeStatus.on_project,
                 ytd_ut=93.0, email="fl@example.com", join_date=date(2021, 12, 1)),
        Employee(gpn="GPN-S-005", name="黄志强", competency="RC", grade="S",
                 location="深圳", counsellor_id=m_employees[3].id, status=EmployeeStatus.on_project,
                 ytd_ut=82.0, email="hzq@example.com", join_date=date(2022, 6, 1)),
        Employee(gpn="GPN-S-006", name="杨梅", competency="RC", grade="S",
                 location="成都", counsellor_id=m_employees[3].id, status=EmployeeStatus.leave,
                 ytd_ut=40.0, email="ym@example.com", join_date=date(2022, 9, 1)),
    ]
    session.add_all(s_employees)
    await session.flush()

    # C 级别
    c_employees = [
        Employee(gpn="GPN-C-001", name="林晨", competency="DE", grade="C",
                 location="上海", counsellor_id=s_employees[0].id, status=EmployeeStatus.on_project,
                 ytd_ut=100.0, email="lc@example.com", join_date=date(2023, 7, 1)),
        Employee(gpn="GPN-C-002", name="徐佳佳", competency="DE", grade="C",
                 location="上海", counsellor_id=s_employees[1].id, status=EmployeeStatus.on_project,
                 ytd_ut=96.0, email="xjj@example.com", join_date=date(2023, 9, 1)),
        Employee(gpn="GPN-C-003", name="谢宇", competency="Platforms", grade="C",
                 location="北京", counsellor_id=s_employees[3].id, status=EmployeeStatus.bench,
                 ytd_ut=45.0, email="xy@example.com", join_date=date(2024, 3, 1)),
        Employee(gpn="GPN-C-004", name="蒋雪", competency="RC", grade="C",
                 location="深圳", counsellor_id=s_employees[4].id, status=EmployeeStatus.on_project,
                 ytd_ut=88.0, email="jx@example.com", join_date=date(2023, 12, 1)),
        Employee(gpn="GPN-C-005", name="何俊杰", competency="DE", grade="C",
                 location="上海", counsellor_id=s_employees[0].id, status=EmployeeStatus.bench,
                 ytd_ut=30.0, email="hjj@example.com", join_date=date(2024, 7, 1)),
    ]
    session.add_all(c_employees)
    await session.flush()

    all_employees = [mgr1, mgr2, mgr3] + m_employees + s_employees + c_employees
    print(f"  员工：{len(all_employees)} 条")

    # ------------------------------------------------------------------ #
    # 4. 员工-项目 关联
    # ------------------------------------------------------------------ #
    ep_data = [
        # 项目0：央企 S/4HANA
        (mgr1, projects[0], "项目经理", date(2024, 3, 1), None, True),
        (m_employees[0], projects[0], "MM 功能顾问", date(2024, 3, 1), None, True),
        (s_employees[0], projects[0], "ABAP 开发顾问", date(2024, 3, 1), None, True),
        (s_employees[1], projects[0], "ABAP 开发顾问", date(2024, 3, 1), None, True),
        (c_employees[0], projects[0], "初级开发顾问", date(2024, 3, 1), None, True),
        (c_employees[1], projects[0], "初级功能顾问", date(2024, 3, 1), None, True),
        # 项目1：零售 MM/WM
        (mgr2, projects[1], "项目经理", date(2024, 6, 1), None, True),
        (s_employees[3], projects[1], "WM/EWM 顾问", date(2024, 6, 1), None, True),
        (c_employees[2], projects[1], "初级顾问", date(2024, 6, 1), None, True),
        # 项目2：制造企业 PP（已完成）
        (mgr1, projects[2], "项目经理", date(2023, 1, 1), date(2023, 12, 31), False),
        (m_employees[1], projects[2], "PP 顾问", date(2023, 1, 1), date(2023, 12, 31), False),
        (s_employees[2], projects[2], "PP 顾问", date(2023, 1, 1), date(2023, 12, 31), False),
        # 项目3：金融数字化
        (mgr3, projects[3], "变革管理主管", date(2024, 9, 1), None, True),
        (m_employees[3], projects[3], "变革管理顾问", date(2024, 9, 1), None, True),
        (s_employees[4], projects[3], "业务分析师", date(2024, 9, 1), None, True),
        (c_employees[3], projects[3], "初级顾问", date(2024, 9, 1), None, True),
    ]
    for emp, proj, role, sd, ed, is_cur in ep_data:
        ep = EmployeeProject(employee_id=emp.id, project_id=proj.id,
                             role=role, start_date=sd, end_date=ed, is_current=is_cur)
        session.add(ep)
    await session.flush()
    print(f"  员工-项目关联：{len(ep_data)} 条")

    # ------------------------------------------------------------------ #
    # 5. 员工技能
    # ------------------------------------------------------------------ #
    es_data = [
        # mgr1 李明远
        (mgr1, "SAP S/4HANA", 5), (mgr1, "SAP MM", 5), (mgr1, "项目管理", 5), (mgr1, "变革管理", 4),
        # mgr2 张晓华
        (mgr2, "SAP WM/EWM", 5), (mgr2, "SAP MM", 4), (mgr2, "项目管理", 5),
        # mgr3 王芳
        (mgr3, "变革管理", 5), (mgr3, "需求分析", 5), (mgr3, "项目管理", 4),
        # m_employees[0] 陈建国
        (m_employees[0], "SAP MM", 5), (m_employees[0], "SAP S/4HANA", 4), (m_employees[0], "需求分析", 4),
        # m_employees[1] 刘思远
        (m_employees[1], "SAP PP", 5), (m_employees[1], "SAP MM", 3), (m_employees[1], "需求分析", 4),
        # m_employees[2] 赵雨婷
        (m_employees[2], "SAP BTP", 4), (m_employees[2], "Python", 3), (m_employees[2], "SQL", 4),
        # m_employees[3] 孙浩然
        (m_employees[3], "变革管理", 4), (m_employees[3], "需求分析", 5), (m_employees[3], "项目管理", 3),
        # s_employees[0] 周文博
        (s_employees[0], "ABAP", 5), (s_employees[0], "SAP S/4HANA", 4), (s_employees[0], "SAP MM", 3),
        # s_employees[1] 吴晓敏
        (s_employees[1], "ABAP", 4), (s_employees[1], "SAP FI/CO", 3), (s_employees[1], "Python", 3),
        # s_employees[2] 郑凯
        (s_employees[2], "SAP PP", 4), (s_employees[2], "ABAP", 3),
        # s_employees[3] 冯丽
        (s_employees[3], "SAP WM/EWM", 4), (s_employees[3], "SAP MM", 4), (s_employees[3], "SQL", 3),
        # s_employees[4] 黄志强
        (s_employees[4], "需求分析", 4), (s_employees[4], "变革管理", 3), (s_employees[4], "Power BI", 3),
        # s_employees[5] 杨梅
        (s_employees[5], "需求分析", 3), (s_employees[5], "变革管理", 3),
        # c_employees
        (c_employees[0], "ABAP", 3), (c_employees[0], "SAP S/4HANA", 2),
        (c_employees[1], "SAP MM", 3), (c_employees[1], "SAP SD", 2),
        (c_employees[2], "SAP BTP", 2), (c_employees[2], "Python", 2), (c_employees[2], "SQL", 3),
        (c_employees[3], "需求分析", 3), (c_employees[3], "Power BI", 2),
        (c_employees[4], "ABAP", 2), (c_employees[4], "SAP S/4HANA", 1),
    ]
    for emp, skill_name, level in es_data:
        sk = skill_map.get(skill_name)
        if sk:
            es = EmployeeSkill(employee_id=emp.id, skill_id=sk.id, level=level)
            session.add(es)
    await session.flush()
    print(f"  员工技能：{len(es_data)} 条")

    # ------------------------------------------------------------------ #
    # 6. 绩效记录
    # ------------------------------------------------------------------ #
    perf_data = [
        # 2024 年度
        (mgr1, 2024, None, "EX", 4.8, "全年带领团队超额完成 UT 目标"),
        (mgr2, 2024, None, "ME", 4.5, "项目交付质量高"),
        (mgr3, 2024, None, "ME", 4.6, "客户满意度优秀"),
        (m_employees[0], 2024, None, "EX", 4.9, "技术能力突出，客户好评"),
        (m_employees[1], 2024, None, "ME", 4.3, "交付稳定"),
        (m_employees[2], 2024, None, "NI", 3.8, "bench 时间较长，需提升业务拓展能力"),
        (m_employees[3], 2024, None, "ME", 4.7, "变革管理方向领先"),
        (s_employees[0], 2024, None, "EX", 4.9, "ABAP 能力出色，利用率 top"),
        (s_employees[1], 2024, None, "ME", 4.4, "稳定交付"),
        (s_employees[2], 2024, None, "NI", 3.5, "bench 超过 2 个月"),
        (s_employees[3], 2024, None, "ME", 4.6, "WM 方向专业"),
        (s_employees[4], 2024, None, "ME", 4.5, "客户反馈良好"),
        (c_employees[0], 2024, None, "EX", 4.8, "入职第一年 UT 100%，表现优异"),
        (c_employees[1], 2024, None, "ME", 4.5, "快速上手，融入团队"),
        (c_employees[2], 2024, None, "NI", 3.7, "能力有待提升"),
        # 2023 年度
        (mgr1, 2023, None, "EX", 4.7, "项目 PP 顺利交付"),
        (m_employees[1], 2023, None, "EX", 4.8, "PP 项目技术负责人"),
        (s_employees[2], 2023, None, "ME", 4.2, "首次独立带模块"),
    ]
    for i, (emp, year, quarter, rating, voc, comment) in enumerate(perf_data):
        reviewer = mgr1 if emp != mgr1 else mgr2
        p = Performance(employee_id=emp.id, year=year, quarter=quarter,
                        rating=rating, voc_score=voc, comments=comment,
                        reviewer_id=reviewer.id)
        session.add(p)
    await session.flush()
    print(f"  绩效记录：{len(perf_data)} 条")

    # ------------------------------------------------------------------ #
    # 7. 培训 / CPE
    # ------------------------------------------------------------------ #
    training_data = [
        (mgr1, "SAP S/4HANA 2023 新特性", "CPE", 8.0,
         date(2024, 1, 15), date(2024, 1, 15), TrainingStatus.completed),
        (mgr2, "EWM 高级配置培训", "certification", 16.0,
         date(2024, 2, 1), date(2024, 2, 2), TrainingStatus.completed),
        (mgr3, "OCM 变革管理认证", "certification", 24.0,
         date(2023, 11, 1), date(2023, 11, 3), TrainingStatus.completed),
        (m_employees[0], "SAP S/4HANA MM 深度培训", "CPE", 16.0,
         date(2024, 3, 10), date(2024, 3, 11), TrainingStatus.completed),
        (m_employees[2], "SAP BTP 开发者认证", "certification", 40.0,
         date(2024, 5, 1), date(2024, 5, 5), TrainingStatus.completed),
        (m_employees[2], "Python 数据分析进阶", "internal", 8.0,
         date(2024, 8, 1), None, TrainingStatus.in_progress),
        (s_employees[0], "ABAP OO 高级编程", "CPE", 8.0,
         date(2024, 4, 20), date(2024, 4, 20), TrainingStatus.completed),
        (s_employees[2], "SAP PP 认证", "certification", 32.0,
         date(2024, 10, 1), date(2024, 10, 4), TrainingStatus.completed),
        (s_employees[3], "SAP EWM 认证备考", "certification", 24.0,
         date(2025, 3, 1), None, TrainingStatus.planned),
        (c_employees[0], "新人入职培训 SAP 基础", "internal", 40.0,
         date(2023, 7, 1), date(2023, 7, 5), TrainingStatus.completed),
        (c_employees[0], "ABAP 初级培训", "CPE", 16.0,
         date(2023, 9, 1), date(2023, 9, 2), TrainingStatus.completed),
        (c_employees[1], "新人入职培训 SAP 基础", "internal", 40.0,
         date(2023, 9, 1), date(2023, 9, 5), TrainingStatus.completed),
        (c_employees[2], "BTP 入门培训", "internal", 8.0,
         date(2024, 4, 1), date(2024, 4, 1), TrainingStatus.completed),
        (c_employees[4], "SAP S/4HANA 基础培训", "internal", 16.0,
         date(2024, 8, 1), date(2024, 8, 2), TrainingStatus.completed),
        (c_employees[4], "ABAP 初级认证", "certification", 24.0,
         date(2025, 5, 1), None, TrainingStatus.planned),
    ]
    for emp, tname, ttype, hours, sd, cd, status in training_data:
        t = TrainingCPE(employee_id=emp.id, training_name=tname, training_type=ttype,
                        hours=hours, start_date=sd, completed_date=cd, status=status)
        session.add(t)
    await session.flush()
    print(f"  培训记录：{len(training_data)} 条")

    await session.commit()
    print("\n✅ 测试数据写入完成！")


async def main():
    # 先建表
    async with engine.begin() as conn:
        # 导入所有模型确保注册
        from app.models import employee, project, skill, performance, training
        await conn.run_sync(Base.metadata.create_all)
        print("数据库表已就绪")

    async with AsyncSessionLocal() as session:
        print("\n开始写入测试数据...")
        await clear_data(session)
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
