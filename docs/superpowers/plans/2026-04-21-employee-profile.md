# Employee Profile Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现员工画像页面，包含信息卡片（含头像上传、编辑）、技能评估雷达图、以及项目经历/培训记录/绩效考评懒加载 Tab。

**Architecture:** 后端扩展现有 employees 路由，新增 avatar/skills/projects/trainings/performances 五个子端点；前端 EmployeeProfile.vue 全量重写，技能 Tab 随页面加载，其余 Tab 首次点击时按需请求并缓存。

**Tech Stack:** FastAPI + async SQLAlchemy 2.0, PostgreSQL, Vue 3 Composition API, Element Plus, vue-echarts, axios

**Spec:** `docs/superpowers/specs/2026-04-21-employee-profile-design.md`

---

## 文件清单

| 操作 | 文件 | 说明 |
|------|------|------|
| Modify | `backend/app/models/employee.py` | 新增 phone/effective_ut/avatar_url 字段；更新 level 注释 |
| Modify | `backend/app/schemas/employee.py` | 扩展 EmployeeDetail/EmployeeUpdate；新增 Tab 响应 schema |
| Modify | `backend/app/routers/employees.py` | 扩展 get_employee；新增 6 个端点（含 GET /api/skills） |
| Modify | `backend/app/main.py` | 挂载 /uploads 静态目录；新增 CORS 5200 |
| Modify | `frontend/src/api/employees.js` | 新增 6 个 API 方法（含 getSkillOptions） |
| Rewrite | `frontend/src/views/EmployeeProfile.vue` | 全量实现员工画像页面 |

---

## Task 1: 数据库迁移

**Files:**
- 无文件修改，直接执行 SQL

- [ ] **Step 1: 预检 level 异常数据**

```powershell
$env:PGPASSWORD = "ey123456"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d talent_portrait -c "SELECT COUNT(*) FROM employee_skills WHERE level NOT BETWEEN 1 AND 5;"
```
预期：返回 `0`，若非 0 需人工检查。

- [ ] **Step 2: 执行迁移 SQL**

```powershell
$env:PGPASSWORD = "ey123456"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d talent_portrait -c "
ALTER TABLE employees ADD COLUMN IF NOT EXISTS phone VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS effective_ut FLOAT;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);
UPDATE employee_skills SET level = level * 20 WHERE level BETWEEN 1 AND 5;
"
```
预期：`ALTER TABLE`, `ALTER TABLE`, `ALTER TABLE`, `UPDATE N`

- [ ] **Step 3: 验证**

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d talent_portrait -c "SELECT column_name FROM information_schema.columns WHERE table_name='employees' AND column_name IN ('phone','effective_ut','avatar_url');"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d talent_portrait -c "SELECT MIN(level), MAX(level) FROM employee_skills;"
```
预期：3 个字段均出现；level 范围在 0-100 之间。

---

## Task 2: 后端 Model 更新

**Files:**
- Modify: `backend/app/models/employee.py`

- [ ] **Step 1: 在 Employee 类中新增三个字段**

在 `backend/app/models/employee.py` 的 `Employee` 类中，在 `email` 字段后面添加：

```python
phone = Column(String(50), nullable=True, comment="联系电话")
effective_ut = Column(Float, nullable=True, comment="Effective UT，来自外部数据源")
avatar_url = Column(String(500), nullable=True, comment="头像图片路径")
```

- [ ] **Step 2: 更新 EmployeeSkill.level 注释**

将 `EmployeeSkill` 类中：
```python
level = Column(Integer, default=1, comment="技能等级 1-5")
```
改为：
```python
level = Column(Integer, default=0, comment="技能等级 0-100，步长10")
```

- [ ] **Step 3: 重启后端，验证无报错**

```bash
# 在后端进程的输出中确认 Application startup complete
curl --noproxy "*" http://127.0.0.1:8000/health
```
预期：`{"status":"ok"}`

---

## Task 3: 后端 Schema 扩展

**Files:**
- Modify: `backend/app/schemas/employee.py`

- [ ] **Step 1: 扩展 EmployeeDetail，新增字段**

在 `EmployeeDetail` 类中补充以下字段（在 `created_at` 前添加）：

```python
name_en: Optional[str] = None
phone: Optional[str] = None
effective_ut: Optional[float] = None
avatar_url: Optional[str] = None
counsellor_name_en: Optional[str] = None
counsellor_grade: Optional[str] = None
counsellor_email: Optional[str] = None
```

- [ ] **Step 2: 扩展 EmployeeUpdate，新增 phone 字段**

在 `EmployeeUpdate` 类中添加：
```python
phone: Optional[str] = None
```

- [ ] **Step 3: 在文件末尾新增 Tab 响应 Schema**

```python
class ProjectHistoryItem(BaseModel):
    id: int
    project_name: str
    project_code: Optional[str] = None
    role: Optional[str] = None
    team_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False

    class Config:
        from_attributes = True


class TrainingItem(BaseModel):
    id: int
    training_name: str
    training_type: Optional[str] = None
    hours: Optional[float] = None
    start_date: Optional[date] = None
    completed_date: Optional[date] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class PerformanceItem(BaseModel):
    id: int
    year: int
    quarter: Optional[int] = None
    rating: Optional[str] = None
    voc_score: Optional[float] = None
    comments: Optional[str] = None

    class Config:
        from_attributes = True
```

---

## Task 4: 后端 - 扩展 get_employee 接口

**Files:**
- Modify: `backend/app/routers/employees.py`

- [ ] **Step 1: 更新 get_employee handler 的返回值**

找到 `@router.get("/{employee_id}")` 下的 `return EmployeeDetail(...)` 语句，替换为：

```python
return EmployeeDetail(
    id=emp.id, gpn=emp.gpn, name=emp.name, name_en=emp.name_en,
    competency=emp.competency, grade=emp.grade, location=emp.location,
    counsellor_name=emp.counsellor.name if emp.counsellor else None,
    counsellor_name_en=emp.counsellor.name_en if emp.counsellor else None,
    counsellor_grade=emp.counsellor.grade if emp.counsellor else None,
    counsellor_email=emp.counsellor.email if emp.counsellor else None,
    counsellor_id=emp.counsellor_id,
    status=emp.status, ytd_ut=emp.ytd_ut,
    phone=emp.phone, effective_ut=emp.effective_ut, avatar_url=emp.avatar_url,
    email=emp.email, join_date=emp.join_date, skills=skills,
    current_project=current_project, created_at=emp.created_at,
)
```

- [ ] **Step 2: 验证接口返回新字段**

```bash
curl --noproxy "*" "http://127.0.0.1:8000/api/employees/1" | python -m json.tool | grep -E "phone|effective_ut|avatar_url|counsellor_grade"
```
预期：4 个字段出现在 JSON 中（值可为 null）。

---

## Task 5: 后端 - 头像上传 + 静态文件

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/routers/employees.py`

- [ ] **Step 1: 在 main.py 挂载静态目录 + 新增 CORS 5200**

在 `backend/app/main.py` 顶部 import 区域添加：
```python
import os
from fastapi.staticfiles import StaticFiles
```

`allow_origins` 列表新增 `"http://localhost:5200"`：
```python
allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5200"],
```

在所有 `app.include_router(...)` 之后（文件末尾 startup 事件之前）添加：
```python
os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

注意：`app.mount` 必须在所有 `include_router` 之后，否则会优先匹配 /uploads 路径干扰路由。

- [ ] **Step 2: 在 employees.py 中新增头像上传端点**

在文件顶部 import 区域添加（若未有）：
```python
import os, time
from fastapi import File, UploadFile
```

在 `router.delete` 端点之后添加：

```python
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB

@router.post("/{employee_id}/avatar")
async def upload_avatar(
    employee_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/webp 格式")
    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 2MB")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{employee_id}_{int(time.time())}.{ext}"
    save_path = os.path.join("uploads", "avatars", filename)
    with open(save_path, "wb") as f:
        f.write(content)

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.avatar_url = f"/uploads/avatars/{filename}"
    await db.commit()
    return {"avatar_url": emp.avatar_url}
```

- [ ] **Step 3: 重启后端，验证静态文件路由**

```bash
curl --noproxy "*" http://127.0.0.1:8000/uploads/
```
预期：返回 404（目录列表被禁用）而非 500，说明挂载成功。

---

## Task 6: 后端 - 技能批量保存端点

**Files:**
- Modify: `backend/app/routers/employees.py`
- Modify: `backend/app/schemas/employee.py`

- [ ] **Step 1: 在 schemas/employee.py 添加技能保存请求体**

```python
class SkillInput(BaseModel):
    skill_id: int
    level: int  # 0-100, step 10
```

- [ ] **Step 2: 在 employees.py 添加端点**

在头像上传端点之后添加：

```python
from app.schemas.employee import SkillInput

@router.put("/{employee_id}/skills")
async def update_skills(
    employee_id: int,
    skills: List[SkillInput],
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import delete as sa_delete
    await db.execute(
        sa_delete(EmployeeSkill).where(EmployeeSkill.employee_id == employee_id)
    )
    await db.flush()
    for s in skills:
        db.add(EmployeeSkill(employee_id=employee_id, skill_id=s.skill_id, level=s.level))
    await db.commit()
    return {"ok": True}
```

需要在文件顶部确认已 import `List`（来自 `typing`）。

- [ ] **Step 3: 验证端点存在**

```bash
curl --noproxy "*" -X PUT "http://127.0.0.1:8000/api/employees/1/skills" \
  -H "Content-Type: application/json" -d "[]"
```
预期：`{"ok":true}`（清空技能，不报错）。

---

## Task 6b: 后端 - GET /api/skills 技能字典端点

**Files:**
- Modify: `backend/app/routers/employees.py`

前端技能下拉需要 skill_id + skill_name，filter-options 只返回名称，需独立接口。

- [ ] **Step 1: 在 employees.py 中新增技能列表端点**

在文件顶部已有 `from app.models.skill import Skill`，追加端点：

```python
@router.get("/skill-options")
async def get_skill_options(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill.id, Skill.name, Skill.category).order_by(Skill.name))
    return [{"id": r[0], "name": r[1], "category": r[2]} for r in result.all()]
```

注意：此端点路径为 `/api/employees/skill-options`，必须在 `/{employee_id}` 路由之前注册（FastAPI 按声明顺序匹配），已有的 `/filter-options` 端点在前，只需追加在它附近即可。

- [ ] **Step 2: 验证**

```bash
curl --noproxy "*" "http://127.0.0.1:8000/api/employees/skill-options"
```
预期：返回 `[{"id":1,"name":"...","category":"..."},...]` 数组。

---

## Task 7: 后端 - Tab 懒加载端点

**Files:**
- Modify: `backend/app/routers/employees.py`

在 schema import 行添加新 schema：
```python
from app.schemas.employee import ..., ProjectHistoryItem, TrainingItem, PerformanceItem
```

- [ ] **Step 1: 新增项目经历端点**

```python
from app.models.training import TrainingCPE
from app.models.performance import Performance

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
```

- [ ] **Step 2: 新增培训记录端点**

```python
@router.get("/{employee_id}/trainings", response_model=List[TrainingItem])
async def get_employee_trainings(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TrainingCPE)
        .where(TrainingCPE.employee_id == employee_id)
        .order_by(TrainingCPE.start_date.desc())
    )
    return result.scalars().all()
```

- [ ] **Step 3: 新增绩效考评端点**

```python
@router.get("/{employee_id}/performances", response_model=List[PerformanceItem])
async def get_employee_performances(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Performance)
        .where(Performance.employee_id == employee_id)
        .order_by(Performance.year.desc(), Performance.quarter.desc())
    )
    return result.scalars().all()
```

- [ ] **Step 4: 验证三个端点**

```bash
curl --noproxy "*" "http://127.0.0.1:8000/api/employees/1/projects"
curl --noproxy "*" "http://127.0.0.1:8000/api/employees/1/trainings"
curl --noproxy "*" "http://127.0.0.1:8000/api/employees/1/performances"
```
预期：三个接口均返回 JSON 数组（可为空数组 `[]`）。

---

## Task 8: 前端 API 层扩展

**Files:**
- Modify: `frontend/src/api/employees.js`

- [ ] **Step 1: 在 employeeApi 对象中追加 6 个方法**

```javascript
getSkillOptions() {
  return http.get('/employees/skill-options')
},
uploadAvatar(id, file) {
  const form = new FormData()
  form.append('file', file)
  return http.post(`/employees/${id}/avatar`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
},
updateSkills(id, skills) {
  return http.put(`/employees/${id}/skills`, skills)
},
getProjects(id) {
  return http.get(`/employees/${id}/projects`)
},
getTrainings(id) {
  return http.get(`/employees/${id}/trainings`)
},
getPerformances(id) {
  return http.get(`/employees/${id}/performances`)
},
```

---

## Task 9: 前端 EmployeeProfile.vue - 信息卡片

**Files:**
- Rewrite: `frontend/src/views/EmployeeProfile.vue`

- [ ] **Step 1: 写页面骨架 + 信息卡片**

用以下内容完整替换 `EmployeeProfile.vue`（分步实现，先完成信息卡片部分）：

```vue
<template>
  <div class="profile-page">
    <!-- 信息卡片 -->
    <div class="info-card" v-loading="loading">
      <div class="card-left">
        <!-- 头像 -->
        <div class="avatar-wrap" @click="editing ? triggerUpload() : null">
          <img v-if="emp.avatar_url" :src="emp.avatar_url" class="avatar-img" />
          <div v-else class="avatar-placeholder">{{ emp.name?.charAt(0) }}</div>
          <div v-if="editing" class="avatar-overlay"><el-icon><Camera /></el-icon></div>
        </div>
        <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp"
          style="display:none" @change="handleAvatarUpload" />
        <el-tag :type="statusType" class="status-tag">{{ emp.status }}</el-tag>
      </div>

      <div class="card-body">
        <div class="card-header-row">
          <div class="name-block">
            <span class="name-cn">{{ emp.name }}</span>
            <span class="name-en">{{ emp.name_en || '—' }}</span>
          </div>
          <div class="card-actions">
            <template v-if="!editing">
              <el-button size="small" @click="startEdit">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="cancelEdit">取消</el-button>
              <el-button size="small" type="primary" :loading="saving" @click="saveEdit">保存</el-button>
            </template>
          </div>
        </div>

        <div class="field-grid">
          <div class="field-item">
            <span class="field-label">Competency</span>
            <span class="field-value">{{ emp.competency || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">GPN</span>
            <span class="field-value">{{ emp.gpn }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">职级</span>
            <span class="field-value">{{ emp.grade || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">Location</span>
            <span v-if="!editing" class="field-value">{{ emp.location || '—' }}</span>
            <el-input v-else v-model="editForm.location" size="small" />
          </div>
          <div class="field-item">
            <span class="field-label">邮箱</span>
            <span v-if="!editing" class="field-value">{{ emp.email || '—' }}</span>
            <el-input v-else v-model="editForm.email" size="small" />
          </div>
          <div class="field-item">
            <span class="field-label">电话</span>
            <span v-if="!editing" class="field-value">{{ emp.phone || '—' }}</span>
            <el-input v-else v-model="editForm.phone" size="small" />
          </div>
          <div class="field-item">
            <span class="field-label">Counsellor</span>
            <el-popover
              v-if="emp.counsellor_name"
              placement="top" trigger="hover" :width="220"
              popper-class="counsellor-popover"
            >
              <template #default>
                <div class="counsellor-card">
                  <div class="counsellor-avatar">{{ emp.counsellor_name?.charAt(0) }}</div>
                  <div class="counsellor-info">
                    <div class="counsellor-name">{{ emp.counsellor_name }}
                      <span v-if="emp.counsellor_name_en"> / {{ emp.counsellor_name_en }}</span>
                    </div>
                    <div class="counsellor-grade">{{ emp.counsellor_grade || '—' }}</div>
                    <div class="counsellor-email">{{ emp.counsellor_email || '—' }}</div>
                  </div>
                </div>
              </template>
              <template #reference>
                <span class="field-value counsellor-link">{{ emp.counsellor_name }}</span>
              </template>
            </el-popover>
            <span v-else class="field-value">—</span>
          </div>
          <div class="field-item">
            <span class="field-label">入职日期</span>
            <span class="field-value">{{ emp.join_date || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">当前项目</span>
            <span class="field-value">{{ emp.current_project?.name || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">YTD UT</span>
            <span class="field-value">{{ emp.ytd_ut != null ? emp.ytd_ut + '%' : '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">Effective UT</span>
            <span class="field-value">{{ emp.effective_ut != null ? emp.effective_ut + '%' : '—' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 面板 -->
    <div class="tab-panel">
      <el-tabs v-model="activeTab" @tab-click="onTabClick">
        <el-tab-pane label="技能评估" name="skills">
          <!-- Task 10 实现 -->
        </el-tab-pane>
        <el-tab-pane label="项目经历" name="projects">
          <!-- Task 11 实现 -->
        </el-tab-pane>
        <el-tab-pane label="培训记录" name="trainings">
          <!-- Task 11 实现 -->
        </el-tab-pane>
        <el-tab-pane label="绩效考评" name="performances">
          <!-- Task 11 实现 -->
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { employeeApi } from '@/api/employees'

const route = useRoute()
const employeeId = computed(() => Number(route.params.id))

const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const emp = ref({})
const editForm = reactive({ location: '', email: '', phone: '' })
const fileInput = ref(null)
const activeTab = ref('skills')

const statusType = computed(() => {
  const map = { '在项': 'success', 'bench': 'warning', '休假': 'info' }
  return map[emp.value.status] || 'info'
})

async function loadEmployee() {
  loading.value = true
  try {
    const res = await employeeApi.getById(employeeId.value)
    emp.value = res.data
  } finally {
    loading.value = false
  }
}

function startEdit() {
  editForm.location = emp.value.location || ''
  editForm.email = emp.value.email || ''
  editForm.phone = emp.value.phone || ''
  editing.value = true
}

function cancelEdit() { editing.value = false }

async function saveEdit() {
  saving.value = true
  try {
    const res = await employeeApi.update(employeeId.value, {
      location: editForm.location,
      email: editForm.email,
      phone: editForm.phone,
    })
    emp.value = res.data
    editing.value = false
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function triggerUpload() { fileInput.value?.click() }

async function handleAvatarUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  try {
    const res = await employeeApi.uploadAvatar(employeeId.value, file)
    emp.value.avatar_url = res.data.avatar_url
    ElMessage.success('头像上传成功')
  } catch {
    ElMessage.error('头像上传失败')
  }
  e.target.value = ''
}

onMounted(loadEmployee)
</script>

<style scoped>
.profile-page { padding: 20px; display: flex; flex-direction: column; gap: 20px; }

.info-card {
  background: var(--card-bg, #0d2137);
  border: 1px solid rgba(0,200,255,0.15);
  border-radius: 10px;
  padding: 24px;
  display: flex;
  gap: 24px;
}

.card-left { display: flex; flex-direction: column; align-items: center; gap: 12px; min-width: 100px; }

.avatar-wrap {
  position: relative; width: 80px; height: 80px; border-radius: 50%;
  border: 2px solid var(--accent-cyan, #00c8ff); overflow: hidden; cursor: pointer;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder {
  width: 100%; height: 100%; background: #1a3a5c;
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; color: var(--accent-cyan, #00c8ff); font-weight: bold;
}
.avatar-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 20px;
}
.status-tag { margin-top: 4px; }

.card-body { flex: 1; }
.card-header-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.name-cn { font-size: 20px; font-weight: bold; color: #fff; margin-right: 10px; }
.name-en { font-size: 14px; color: rgba(255,255,255,0.5); }

.field-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px 24px; }
.field-item { display: flex; flex-direction: column; gap: 2px; }
.field-label { font-size: 11px; color: rgba(255,255,255,0.4); text-transform: uppercase; }
.field-value { font-size: 13px; color: rgba(255,255,255,0.85); }
.counsellor-link { color: var(--accent-cyan, #00c8ff); cursor: pointer; text-decoration: underline; }

.tab-panel {
  background: var(--card-bg, #0d2137);
  border: 1px solid rgba(0,200,255,0.15);
  border-radius: 10px;
  padding: 20px;
}

.counsellor-card { display: flex; gap: 12px; align-items: center; }
.counsellor-avatar {
  width: 40px; height: 40px; border-radius: 50%; background: var(--accent-cyan, #00c8ff);
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; color: #000; font-size: 16px; flex-shrink: 0;
}
.counsellor-name { font-size: 13px; font-weight: bold; color: #fff; }
.counsellor-grade { font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 2px; }
.counsellor-email { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 2px; }
</style>
```

- [ ] **Step 2: 在浏览器验证信息卡片渲染**

打开 http://localhost:5200/employees，点击任意员工的「查看」按钮，确认：
- 顶部信息卡片正常显示员工信息
- 编辑按钮可点击，切换为输入框后可保存
- Counsellor 字段悬浮弹出卡片

---

## Task 10: 前端 - 技能评估 Tab

**Files:**
- Modify: `frontend/src/views/EmployeeProfile.vue`

- [ ] **Step 1: 添加依赖 import（script setup 顶部）**

vue-echarts 需要在使用前注册图表类型，RadarChart 与其他页面使用的 PieChart/BarChart 同级注册：

```javascript
import { use } from 'echarts/core'
import { RadarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, RadarComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
use([RadarChart, RadarComponent, TooltipComponent, LegendComponent, CanvasRenderer])
```

- [ ] **Step 2: 添加技能相关响应式数据和计算属性**

```javascript
// 技能相关
const skillList = ref([])        // 当前编辑中的技能列表 [{skill_id, skill_name, level}]
const allSkills = ref([])        // 技能字典 [{id, name, category}]
const skillSaving = ref(false)

const LEVEL_OPTIONS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

// 雷达图 option（computed，实时响应 skillList）
const radarOption = computed(() => {
  const list = skillList.value.slice(0, 10)
  if (list.length === 0) return null
  return {
    backgroundColor: 'transparent',
    radar: {
      indicator: list.map(s => ({ name: s.skill_name, max: 100 })),
      shape: 'polygon',
      axisLine: { lineStyle: { color: 'rgba(0,200,255,0.3)' } },
      splitLine: { lineStyle: { color: 'rgba(0,200,255,0.15)' } },
      name: { textStyle: { color: 'rgba(255,255,255,0.7)', fontSize: 12 } },
    },
    series: [{
      type: 'radar',
      data: [{ value: list.map(s => s.level), name: '技能' }],
      areaStyle: { color: 'rgba(0,200,255,0.15)' },
      lineStyle: { color: '#00c8ff' },
      itemStyle: { color: '#00c8ff' },
    }],
  }
})

// 加载技能字典（含 id，用于保存时传 skill_id）
async function loadAllSkills() {
  if (allSkills.value.length > 0) return
  const res = await employeeApi.getSkillOptions()
  allSkills.value = res.data  // [{id, name, category}]
}

// 初始化技能列表（从 emp.skills 转换）
function initSkillList() {
  skillList.value = (emp.value.skills || []).map(s => ({
    skill_id: s.id,
    skill_name: s.name,
    level: s.level,
  }))
}

function addSkill() {
  skillList.value.push({ skill_id: null, skill_name: '', level: 0 })
}

function removeSkill(index) {
  skillList.value.splice(index, 1)
}

function onSkillSelect(index, skillName) {
  const found = allSkills.value.find(s => s.name === skillName)
  skillList.value[index].skill_name = skillName
  skillList.value[index].skill_id = found?.id ?? null
}

async function saveSkills() {
  // 过滤无效项并去重（防止前端重复选同一技能触发唯一约束）
  const seen = new Set()
  const payload = skillList.value
    .filter(s => s.skill_id && !seen.has(s.skill_id) && seen.add(s.skill_id))
    .map(s => ({ skill_id: s.skill_id, level: s.level }))
  skillSaving.value = true
  try {
    await employeeApi.updateSkills(employeeId.value, payload)
    ElMessage.success('技能保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    skillSaving.value = false
  }
}
```

在 `loadEmployee` 函数中，数据加载完毕后调用 `initSkillList()`：
```javascript
async function loadEmployee() {
  loading.value = true
  try {
    const res = await employeeApi.getById(employeeId.value)
    emp.value = res.data
    initSkillList()
    await loadAllSkills()
  } finally {
    loading.value = false
  }
}
```

- [ ] **Step 3: 替换 Tab 面板中的技能评估内容**

将 `<!-- Task 10 实现 -->` 替换为：

```vue
<div class="skills-tab">
  <div class="radar-wrap" v-if="radarOption">
    <VChart :option="radarOption" autoresize style="width:100%;height:360px" />
  </div>
  <div class="radar-empty" v-else>
    <span>暂无技能数据，请在右侧添加技能</span>
  </div>
  <div class="skill-detail">
    <div class="skill-detail-header">
      <span class="skill-detail-title">技能详情</span>
      <el-button size="small" type="primary" :loading="skillSaving" @click="saveSkills">保存技能</el-button>
    </div>
    <div class="skill-rows">
      <div v-for="(s, i) in skillList" :key="i" class="skill-row">
        <el-select
          v-model="s.skill_name"
          placeholder="选择技能"
          filterable size="small"
          style="flex:1"
          @change="val => onSkillSelect(i, val)"
        >
          <el-option v-for="sk in allSkills" :key="sk.name" :label="sk.name" :value="sk.name" />
        </el-select>
        <el-select v-model="s.level" size="small" style="width:90px">
          <el-option v-for="lv in LEVEL_OPTIONS" :key="lv" :label="lv + '%'" :value="lv" />
        </el-select>
        <el-button size="small" type="danger" link @click="removeSkill(i)">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>
    <el-button size="small" @click="addSkill" style="margin-top:8px">
      <el-icon><Plus /></el-icon> 添加技能
    </el-button>
  </div>
</div>
```

- [ ] **Step 4: 新增技能 Tab 样式**

在 `<style scoped>` 中追加：

```css
.skills-tab { display: flex; gap: 20px; min-height: 380px; }
.radar-wrap { flex: 1; }
.radar-empty { flex: 1; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.3); font-size: 13px; }
.skill-detail { width: 280px; display: flex; flex-direction: column; }
.skill-detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.skill-detail-title { font-size: 14px; color: #fff; font-weight: 500; }
.skill-rows { display: flex; flex-direction: column; gap: 8px; overflow-y: auto; max-height: 320px; }
.skill-row { display: flex; align-items: center; gap: 8px; }
```

- [ ] **Step 5: 验证技能评估 Tab**

刷新页面，切换到技能评估 Tab，确认：
- 有技能的员工显示雷达图，无技能显示空状态
- 修改等级后雷达图实时更新
- 点击「添加技能」后新增一行
- 保存成功后刷新页面数据保持

---

## Task 11: 前端 - 懒加载 Tab（项目/培训/绩效）

**Files:**
- Modify: `frontend/src/views/EmployeeProfile.vue`

- [ ] **Step 1: 添加 Tab 数据和加载逻辑**

在 `script setup` 中追加：

```javascript
const projectList = ref(null)   // null = 未加载
const trainingList = ref(null)
const performanceList = ref(null)
const tabLoading = ref(false)

async function onTabClick(tab) {
  const name = tab.paneName
  if (name === 'projects' && projectList.value === null) {
    tabLoading.value = true
    try { projectList.value = (await employeeApi.getProjects(employeeId.value)).data }
    finally { tabLoading.value = false }
  } else if (name === 'trainings' && trainingList.value === null) {
    tabLoading.value = true
    try { trainingList.value = (await employeeApi.getTrainings(employeeId.value)).data }
    finally { tabLoading.value = false }
  } else if (name === 'performances' && performanceList.value === null) {
    tabLoading.value = true
    try { performanceList.value = (await employeeApi.getPerformances(employeeId.value)).data }
    finally { tabLoading.value = false }
  }
}
```

- [ ] **Step 2: 替换三个 Tab 内容**

将 `<!-- Task 11 实现 -->` 分别替换为：

**项目经历 Tab：**
```vue
<div v-loading="tabLoading">
  <el-table :data="projectList || []" style="width:100%">
    <el-table-column prop="project_name" label="项目名称" min-width="180" />
    <el-table-column prop="project_code" label="项目代码" width="130" />
    <el-table-column prop="role" label="角色" width="120" />
    <el-table-column prop="team_name" label="团队" width="140" />
    <el-table-column prop="start_date" label="开始日期" width="110" />
    <el-table-column prop="end_date" label="结束日期" width="110" />
    <el-table-column label="状态" width="90">
      <template #default="{ row }">
        <el-tag v-if="row.is_current" type="success" size="small">当前</el-tag>
        <el-tag v-else type="info" size="small">历史</el-tag>
      </template>
    </el-table-column>
  </el-table>
</div>
```

**培训记录 Tab：**
```vue
<div v-loading="tabLoading">
  <el-table :data="trainingList || []" style="width:100%">
    <el-table-column prop="training_name" label="培训名称" min-width="180" />
    <el-table-column prop="training_type" label="类型" width="120" />
    <el-table-column prop="hours" label="时长(h)" width="90" />
    <el-table-column prop="start_date" label="开始日期" width="110" />
    <el-table-column prop="completed_date" label="完成日期" width="110" />
    <el-table-column label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="{ completed:'success', in_progress:'warning', planned:'info', cancelled:'danger' }[row.status] || 'info'" size="small">
          {{ { completed:'已完成', in_progress:'进行中', planned:'计划中', cancelled:'已取消' }[row.status] || row.status }}
        </el-tag>
      </template>
    </el-table-column>
  </el-table>
</div>
```

**绩效考评 Tab：**
```vue
<div v-loading="tabLoading">
  <el-table :data="performanceList || []" style="width:100%">
    <el-table-column prop="year" label="年份" width="90" />
    <el-table-column prop="quarter" label="季度" width="80">
      <template #default="{ row }">{{ row.quarter ? `Q${row.quarter}` : '年度' }}</template>
    </el-table-column>
    <el-table-column prop="rating" label="评级" width="90">
      <template #default="{ row }">
        <el-tag :type="{ EX:'success', ME:'warning', NI:'danger' }[row.rating] || 'info'" size="small">
          {{ row.rating || '—' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="voc_score" label="VoC评分" width="100" />
    <el-table-column prop="comments" label="备注" min-width="160" show-overflow-tooltip />
  </el-table>
</div>
```

- [ ] **Step 3: 端到端验证**

在浏览器中：
1. 打开任意员工画像页面
2. 依次点击「项目经历」「培训记录」「绩效考评」Tab
3. 确认每个 Tab 只在首次点击时发送网络请求（F12 Network 观察）
4. 切回已加载的 Tab 不重复请求

- [ ] **Step 4: 提交代码**

```bash
git add backend/app/models/employee.py \
        backend/app/schemas/employee.py \
        backend/app/routers/employees.py \
        backend/app/main.py \
        frontend/src/api/employees.js \
        frontend/src/views/EmployeeProfile.vue
git commit -m "feat: 实现员工画像页面（信息卡片、技能评估、懒加载Tab）"
```

---

## 验收标准

- [ ] 信息卡片正确展示所有字段，Counsellor 悬浮卡正常显示
- [ ] 编辑模式仅 Location / 邮箱 / 电话 可输入，保存成功
- [ ] 头像可上传（jpg/png/webp，≤2MB），上传后立即刷新显示
- [ ] 技能雷达图随技能列表实时更新，0 条时显示空状态
- [ ] 技能列表可增删，保存后刷新页面数据持久化
- [ ] 项目/培训/绩效 Tab 懒加载，首次点击发请求，切回不重复请求
