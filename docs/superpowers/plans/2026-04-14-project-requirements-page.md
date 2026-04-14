# 项目需求页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现项目需求页，包含筛选栏 + 需求列表，支持跨项目查看、筛选和删除需求记录。

**Architecture:** 新建 `requirements.py` 后端路由处理所有需求相关 API，更新 `project.py` 模型添加新字段和关联表，前端新建 `requirements.js` API 封装并完整实现 `ProjectRequirements.vue` 页面。

**Tech Stack:** Python 3.13 / FastAPI / SQLAlchemy 2.0 async / asyncpg / PostgreSQL / Vue 3 Composition API / Element Plus / Axios

**Spec:** `docs/superpowers/specs/2026-04-14-project-requirements-page-design.md`

---

## 文件清单

| 操作 | 文件路径 |
|------|----------|
| 修改 | `backend/app/models/project.py` |
| 新建 | `backend/app/routers/requirements.py` |
| 修改 | `backend/app/main.py` |
| 新建 | `frontend/src/api/requirements.js` |
| 修改 | `frontend/src/views/ProjectRequirements.vue` |

---

## Task 1：数据库迁移（手动 SQL）

**Files:**
- 无代码文件，手动在 psql 执行

- [ ] **Step 1: 连接数据库**

在 PowerShell 执行：
```bash
psql -U postgres -d talent_portrait
```

- [ ] **Step 2: 执行 ALTER TABLE**

在 psql 提示符下粘贴并执行：
```sql
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS fiscal_year VARCHAR(20);
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS location VARCHAR(100);
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS match_status VARCHAR(20);
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS requester VARCHAR(100);
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS job_content TEXT;
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS request_date DATE;
```

预期输出：每行 `ALTER TABLE`

- [ ] **Step 3: 验证字段已添加**

```sql
\d project_requirements
```

确认能看到 `fiscal_year`、`location`、`match_status`、`requester`、`job_content`、`request_date` 六个新字段。

- [ ] **Step 4: 退出 psql**

```sql
\q
```

---

## Task 2：更新后端模型

**Files:**
- 修改: `backend/app/models/project.py`

- [ ] **Step 1: 给 ProjectRequirement 添加新字段和关联**

打开 `backend/app/models/project.py`，在 `ProjectRequirement` 类中：

在 `description` 字段后、`created_at` 字段前添加以下字段：
```python
    fiscal_year = Column(String(20), nullable=True, comment="财年，如 FY2025")
    location = Column(String(100), nullable=True, comment="工作地点")
    match_status = Column(String(20), nullable=True, comment="匹配状态：匹配中/已匹配/部分匹配")
    requester = Column(String(100), nullable=True, comment="需求提出者")
    job_content = Column(Text, nullable=True, comment="工作内容")
    request_date = Column(Date, nullable=True, comment="需求提出日期")
```

在 `project = relationship(...)` 后添加：
```python
    consultants = relationship("RequirementConsultant", back_populates="requirement", cascade="all, delete-orphan")
```

- [ ] **Step 2: 在同文件末尾添加 RequirementConsultant 模型**

在 `ProjectVoC` 类之后追加：
```python
class RequirementConsultant(Base):
    __tablename__ = "requirement_consultants"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("project_requirements.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    requirement = relationship("ProjectRequirement", back_populates="consultants")
    employee = relationship("Employee")
```

- [ ] **Step 3: 验证模型语法**

在 `backend/` 目录下：
```bash
python -c "from app.models.project import ProjectRequirement, RequirementConsultant; print('OK')"
```

预期输出：`OK`

- [ ] **Step 4: 重启后端，确认 requirement_consultants 表自动创建**

```bash
uvicorn app.main:app --reload --port 8000
```

在 psql 执行 `\dt` 确认 `requirement_consultants` 表已存在。

---

## Task 3：新建后端路由

**Files:**
- 新建: `backend/app/routers/requirements.py`

- [ ] **Step 1: 创建文件，写入完整路由代码**

新建 `backend/app/routers/requirements.py`，内容如下：

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional

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
    skill: Optional[str] = Query(None),
    headcount_range: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    match_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    # 先构建不含 selectinload 的基础查询用于 count（selectinload 不能被序列化为 subquery）
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
        base_query = base_query.where(ProjectRequirement.required_skills.ilike(f"%{skill}%"))
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

    # 分页查询时再加 selectinload 预加载关联数据
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
```

- [ ] **Step 2: 验证文件语法**

```bash
python -c "from app.routers.requirements import router; print('OK')"
```

预期输出：`OK`

---

## Task 4：注册路由到 main.py

**Files:**
- 修改: `backend/app/main.py`

- [ ] **Step 1: 在 main.py 添加 import 和 include_router**

打开 `backend/app/main.py`，在：
```python
from app.routers import employees, projects
```
改为：
```python
from app.routers import employees, projects, requirements
```

在：
```python
app.include_router(employees.router)
app.include_router(projects.router)
```
后添加：
```python
app.include_router(requirements.router)
```

- [ ] **Step 2: 重启后端验证路由注册成功**

```bash
uvicorn app.main:app --reload --port 8000
```

启动成功后，浏览器访问：
- `http://localhost:8000/api/requirements/filter-options` → 应返回 JSON 对象
- `http://localhost:8000/api/requirements` → 应返回 `{"total": 0, "items": []}` 或有数据

---

## Task 5：新建前端 API 文件

**Files:**
- 新建: `frontend/src/api/requirements.js`

- [ ] **Step 1: 创建文件**

新建 `frontend/src/api/requirements.js`，内容如下：

```js
import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export const requirementApi = {
  list(params) {
    return http.get('/requirements', { params })
  },
  getFilterOptions() {
    return http.get('/requirements/filter-options')
  },
  remove(id) {
    return http.delete(`/requirements/${id}`)
  },
}
```

---

## Task 6：实现前端页面

**Files:**
- 修改: `frontend/src/views/ProjectRequirements.vue`

- [ ] **Step 1: 替换占位符，写入完整页面代码**

将 `frontend/src/views/ProjectRequirements.vue` 全部内容替换为：

```vue
<template>
  <div class="requirements-page">
    <h2 class="page-title">项目需求</h2>

    <div class="list-card">

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-select
          v-model="filters.fiscal_year"
          placeholder="财年"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option v-for="y in filterOptions.fiscal_years" :key="y" :label="y" :value="y" />
        </el-select>

        <el-select
          v-model="filters.competency"
          placeholder="Competency"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option v-for="c in filterOptions.competencies" :key="c" :label="c" :value="c" />
        </el-select>

        <el-select
          v-model="filters.project_type"
          placeholder="所有机会"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option v-for="t in filterOptions.project_types" :key="t" :label="t" :value="t" />
        </el-select>

        <el-select
          v-model="filters.skill"
          placeholder="技能"
          clearable
          filterable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option v-for="s in filterOptions.skills" :key="s" :label="s" :value="s" />
        </el-select>

        <el-select
          v-model="filters.headcount_range"
          placeholder="人数"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="1-5人" value="1-5" />
          <el-option label="6-10人" value="6-10" />
          <el-option label="11-20人" value="11-20" />
          <el-option label="20人以上" value="20+" />
        </el-select>

        <el-select
          v-model="filters.location"
          placeholder="Location"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option v-for="l in filterOptions.locations" :key="l" :label="l" :value="l" />
        </el-select>

        <el-select
          v-model="filters.match_status"
          placeholder="匹配状态"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option v-for="m in filterOptions.match_statuses" :key="m" :label="m" :value="m" />
        </el-select>

        <el-button class="refresh-btn" @click="loadData">
          <el-icon><RefreshRight /></el-icon>
          刷新
        </el-button>

        <el-button type="primary" size="small" class="add-btn">
          <el-icon><Plus /></el-icon>
          新增需求
        </el-button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <el-table
          :data="tableData"
          v-loading="loading"
          class="requirements-table"
          row-class-name="table-row"
          :element-loading-background="'rgba(10,22,40,0.8)'"
          style="min-width: 1800px"
        >
          <el-table-column prop="request_date" label="需求提出日期" width="130" />
          <el-table-column prop="requester" label="需求提出者" width="110" />
          <el-table-column prop="competency" label="Competency" width="120" />
          <el-table-column prop="project_type" label="项目类型" width="100" />
          <el-table-column prop="project_name" label="项目名字" min-width="160" />
          <el-table-column prop="ep_name" label="EP" width="100" />
          <el-table-column prop="em_name" label="EM" width="100" />

          <el-table-column label="项目时间" width="200">
            <template #default="{ row }">
              <span v-if="row.project_start_date || row.project_end_date">
                {{ row.project_start_date || '?' }} ~ {{ row.project_end_date || '?' }}
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="技能" min-width="160">
            <template #default="{ row }">
              <div class="tag-list" v-if="row.required_skills">
                <el-tag
                  v-for="skill in row.required_skills.split(',')"
                  :key="skill"
                  size="small"
                  class="skill-tag"
                  effect="plain"
                >{{ skill.trim() }}</el-tag>
              </div>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="headcount" label="人数" width="70" />

          <el-table-column prop="description" label="详细要求" min-width="140" show-overflow-tooltip />

          <el-table-column prop="location" label="工作地点" width="100" />

          <el-table-column prop="job_content" label="工作内容" min-width="140" show-overflow-tooltip />

          <el-table-column label="匹配状态" width="110">
            <template #default="{ row }">
              <el-tag
                v-if="row.match_status"
                :type="getMatchStatusType(row.match_status)"
                size="small"
                effect="plain"
                class="status-tag"
              >{{ row.match_status }}</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="推荐顾问名单" min-width="160">
            <template #default="{ row }">
              <div class="tag-list" v-if="row.consultants && row.consultants.length">
                <el-tag
                  v-for="c in row.consultants"
                  :key="c.id"
                  size="small"
                  class="consultant-tag"
                  effect="plain"
                >{{ c.name }}</el-tag>
              </div>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <div class="action-cell">
                <div class="action-row">
                  <el-button size="small" type="primary" link>详情</el-button>
                  <el-button size="small" type="primary" link class="delete-btn" @click="deleteRow(row)">删除</el-button>
                </div>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-bar">
        <span class="total-text">共 {{ total }} 条记录</span>
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="prev, pager, next, sizes"
          @current-change="loadData"
          @size-change="handleSizeChange"
        />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { requirementApi } from '@/api/requirements'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const filters = reactive({
  fiscal_year: '',
  competency: '',
  project_type: '',
  skill: '',
  headcount_range: '',
  location: '',
  match_status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
})

const filterOptions = reactive({
  fiscal_years: [],
  competencies: [],
  project_types: [],
  locations: [],
  match_statuses: [],
  skills: [],
})

function getMatchStatusType(status) {
  const map = { '已匹配': 'success', '匹配中': '', '部分匹配': 'warning' }
  return map[status] ?? 'info'
}

function handleFilter() {
  pagination.page = 1
  loadData()
}

function handleSizeChange() {
  pagination.page = 1
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...(filters.fiscal_year && { fiscal_year: filters.fiscal_year }),
      ...(filters.competency && { competency: filters.competency }),
      ...(filters.project_type && { project_type: filters.project_type }),
      ...(filters.skill && { skill: filters.skill }),
      ...(filters.headcount_range && { headcount_range: filters.headcount_range }),
      ...(filters.location && { location: filters.location }),
      ...(filters.match_status && { match_status: filters.match_status }),
    }
    const res = await requirementApi.list(params)
    tableData.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function loadFilterOptions() {
  try {
    const res = await requirementApi.getFilterOptions()
    Object.assign(filterOptions, res.data)
  } catch (e) {
    console.error(e)
  }
}

async function deleteRow(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除该需求记录？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await requirementApi.remove(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadFilterOptions()
  loadData()
})
</script>

<style scoped>
.requirements-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--accent-cyan);
  letter-spacing: 0.5px;
}

.list-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
}

.filter-select {
  width: 130px;
}

.refresh-btn {
  border-color: var(--border-color) !important;
  color: var(--text-secondary) !important;
  background-color: transparent !important;
}

.refresh-btn:hover {
  border-color: var(--accent-cyan) !important;
  color: var(--accent-cyan) !important;
}

.add-btn {
  margin-left: auto;
}

.table-wrapper {
  overflow: auto;
  flex: 1;
}

.requirements-table {
  width: 100%;
}

:deep(.table-row) {
  background-color: transparent !important;
}

:deep(.el-table__row:hover > td) {
  background-color: var(--bg-hover) !important;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.skill-tag {
  background-color: rgba(0, 170, 204, 0.1) !important;
  border-color: var(--accent-cyan-dim) !important;
  color: var(--accent-cyan) !important;
  font-size: 11px;
}

.consultant-tag {
  background-color: rgba(139, 195, 74, 0.1) !important;
  border-color: rgba(139, 195, 74, 0.4) !important;
  color: #8bc34a !important;
  font-size: 11px;
}

:deep(.status-tag.el-tag--plain) {
  border-radius: 4px;
  font-size: 12px;
}

:deep(.el-tag--plain) {
  background-color: rgba(0, 188, 212, 0.1) !important;
  border-color: var(--accent-cyan-dim) !important;
  color: var(--accent-cyan) !important;
}

:deep(.el-tag--success.el-tag--plain) {
  background-color: rgba(102, 187, 106, 0.1) !important;
  border-color: rgba(102, 187, 106, 0.5) !important;
  color: #66bb6a !important;
}

:deep(.el-tag--warning.el-tag--plain) {
  background-color: rgba(255, 167, 38, 0.1) !important;
  border-color: rgba(255, 167, 38, 0.5) !important;
  color: #ffa726 !important;
}

.text-muted {
  color: var(--text-muted);
}

.action-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 2px 0;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.delete-btn {
  color: var(--accent-red) !important;
}

.delete-btn:hover {
  color: #ff6b6b !important;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.total-text {
  color: var(--text-muted);
  font-size: 13px;
  white-space: nowrap;
}
</style>
```

- [ ] **Step 2: 在浏览器验证页面**

确保后端和前端都在运行，访问 `http://localhost:5173/project-requirements`。

预期：
- 页面显示"项目需求"标题
- 筛选栏显示 7 个下拉 + 刷新 + 新增需求按钮
- 表格显示所有列（数据库暂无数据时显示空表）
- 无 console 报错

- [ ] **Step 3: 验证删除功能**

如有数据，点击删除按钮：
- 弹出确认对话框
- 确认后记录消失，显示"删除成功"提示

---

## 验收标准

- [ ] `http://localhost:8000/api/requirements/filter-options` 正常返回 JSON
- [ ] `http://localhost:8000/api/requirements` 正常返回分页数据
- [ ] `http://localhost:5173/project-requirements` 页面正常加载，无报错
- [ ] 筛选项变化触发重新查询
- [ ] 删除功能有二次确认，删除后列表刷新
- [ ] 页面风格与员工列表一致（深色主题）
