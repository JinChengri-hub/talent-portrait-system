# 项目需求页设计文档

**日期：** 2026-04-14
**状态：** 已审批

---

## 概述

为人才画像系统新增**项目需求页**（ProjectRequirements），用于跨项目查看、筛选和管理人员需求，支持后续的顾问推荐与匹配功能。

---

## 数据库变更

### 1. `project_requirements` 表新增字段

> **重要：** 系统使用 `create_all` 启动，只会创建不存在的表，不会修改已存在的表。
> 启动后端前必须手动执行以下 SQL：

```sql
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS fiscal_year VARCHAR(20);
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS location VARCHAR(100);
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS match_status VARCHAR(20);
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS requester VARCHAR(100);
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS job_content TEXT;
ALTER TABLE project_requirements ADD COLUMN IF NOT EXISTS request_date DATE;
```

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `fiscal_year` | VARCHAR(20) | 财年，如 FY2025 |
| `location` | VARCHAR(100) | 工作地点 |
| `match_status` | VARCHAR(20) | 匹配状态：匹配中 / 已匹配 / 部分匹配（VARCHAR，无枚举约束） |
| `requester` | VARCHAR(100) | 需求提出者（文本） |
| `job_content` | TEXT | 工作内容 |
| `request_date` | DATE | 需求提出日期 |

**现有字段保留：**
- `role`、`grade_required`、`headcount`（人数）、`required_skills`（技能，逗号分隔字符串）
- `start_date`、`status`（open/filled/cancelled）、`description`（详细要求）

### 2. 新建 `requirement_consultants` 表

推荐顾问与需求的多对多关联表，随 `create_all` 自动创建。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | SERIAL PK | |
| `requirement_id` | INTEGER FK → project_requirements.id | `ondelete="CASCADE"` |
| `employee_id` | INTEGER FK → employees.id | `ondelete="CASCADE"`（员工被删除时自动移除推荐关联） |
| `created_at` | TIMESTAMP WITH TIME ZONE | 默认 now() |

### 3. 模型文件位置

- `RequirementConsultant` 模型定义在 `backend/app/models/project.py`，与 `ProjectRequirement` 放在同一文件
- `ProjectRequirement` 需添加关系：
  ```python
  consultants = relationship("RequirementConsultant", back_populates="requirement", cascade="all, delete-orphan")
  ```
- `RequirementConsultant` 需添加关系：
  ```python
  requirement = relationship("ProjectRequirement", back_populates="consultants")
  employee = relationship("Employee")
  ```

---

## 后端 API

### 新建文件：`backend/app/routers/requirements.py`

注册至 `backend/app/main.py`：
```python
from app.routers import requirements
app.include_router(requirements.router)
```

### 接口列表

> **注意：** `/filter-options` 路由必须在 `/{id}` 路由之前声明，避免 FastAPI 将 "filter-options" 误解析为整型 id。

#### `GET /api/requirements/filter-options`（必须第一个声明）

返回各筛选项的可选值（从现有数据动态提取）：
```json
{
  "fiscal_years": ["FY2022", "FY2023", "FY2024", "FY2025"],
  "competencies": ["DE", "Platforms", "RC"],
  "project_types": ["BD", "已赢"],
  "locations": ["大连", "上海", "北京"],
  "match_statuses": ["匹配中", "已匹配", "部分匹配"],
  "skills": ["Python", "FastAPI", "Vue", "SAP"]
}
```

`skills` 从 `skills` 表动态获取，与 `employees.py` / `projects.py` 一致。

#### `GET /api/requirements`

分页查询需求列表，支持以下筛选参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `fiscal_year` | str | 财年精确匹配 |
| `competency` | str | 关联项目 competency 精确匹配 |
| `project_type` | str | 关联项目 code_type 精确匹配 |
| `skill` | str | 技能关键词，模糊匹配 `required_skills` 字段 |
| `headcount_range` | str | 人数范围，解析规则：`1-5` → BETWEEN 1 AND 5，`6-10` → BETWEEN 6 AND 10，`11-20` → BETWEEN 11 AND 20，`20+` → > 20 |
| `location` | str | 工作地点精确匹配 |
| `match_status` | str | 匹配状态精确匹配 |
| `page` | int | 页码，默认 1 |
| `page_size` | int | 每页条数，默认 10 |

**查询实现要点：**
- 通过 `selectinload(ProjectRequirement.project).selectinload(Project.em)` 和 `.selectinload(Project.ep)` 两级预加载获取 EP/EM 姓名，避免 N+1
- 通过 `selectinload(ProjectRequirement.consultants).selectinload(RequirementConsultant.employee)` 预加载推荐顾问

**返回结构：**
```json
{
  "total": 100,
  "items": [
    {
      "id": 1,
      "request_date": "2025-01-15",
      "requester": "张三",
      "fiscal_year": "FY2025",
      "location": "上海",
      "match_status": "匹配中",
      "headcount": 2,
      "required_skills": "Python,FastAPI",
      "description": "详细要求文本",
      "job_content": "工作内容文本",
      "project_id": 5,
      "project_name": "某项目",
      "project_type": "已赢",
      "competency": "DE",
      "ep_name": "李四",
      "em_name": "王五",
      "project_start_date": "2025-02-01",
      "project_end_date": "2025-12-31",
      "consultants": [
        {"id": 3, "name": "赵六"}
      ]
    }
  ]
}
```

#### `DELETE /api/requirements/{id}`

删除指定需求。`cascade="all, delete-orphan"` 确保关联的 `requirement_consultants` 记录自动删除。返回 `{"message": "deleted"}`，不存在则返回 404。

---

## 前端

### 文件变更

| 文件 | 操作 |
|------|------|
| `frontend/src/views/ProjectRequirements.vue` | 替换占位符，完整实现 |
| `frontend/src/api/requirements.js` | 新建，封装 API 调用 |

### `api/requirements.js` 接口定义

```js
export const requirementApi = {
  list(params)         // GET /api/requirements
  getFilterOptions()   // GET /api/requirements/filter-options
  remove(id)           // DELETE /api/requirements/{id}
}
```

### 页面结构

```
ProjectRequirements.vue
├── 页面标题：项目需求
└── list-card（深色卡片，与 Employees.vue 风格一致）
    ├── filter-bar（筛选栏）
    │   ├── 财年（el-select）
    │   ├── Competency（el-select）
    │   ├── 所有机会（el-select：BD / 已赢）
    │   ├── 技能（el-select multiple + filterable，从 filter-options.skills 加载）
    │   ├── 人数（el-select：1-5人 / 6-10人 / 11-20人 / 20人以上）
    │   ├── Location（el-select）
    │   ├── 匹配状态（el-select）
    │   ├── 刷新按钮
    │   └── 新增需求按钮（占位，暂无点击事件）
    ├── el-table（表格）
    └── pagination-bar（分页栏）
```

### 表格列定义

| 列名 | 数据字段 | 渲染方式 |
|------|----------|----------|
| 需求提出日期 | `request_date` | 文本 |
| 需求提出者 | `requester` | 文本 |
| Competency | `competency` | 文本 |
| 项目类型 | `project_type` | 文本 |
| 项目名字 | `project_name` | 文本 |
| EP | `ep_name` | 文本 |
| EM | `em_name` | 文本 |
| 项目时间 | `project_start_date` ~ `project_end_date` | 文本拼接 |
| 技能 | `required_skills`（逗号分割） | el-tag 列表 |
| 人数 | `headcount` | 文本 |
| 详细要求 | `description` | 超长省略（show-overflow-tooltip） |
| 工作地点 | `location` | 文本 |
| 工作内容 | `job_content` | 超长省略（show-overflow-tooltip） |
| 匹配状态 | `match_status` | 彩色 el-tag：匹配中=蓝 / 已匹配=绿 / 部分匹配=橙 |
| 推荐顾问名单 | `consultants[].name` | el-tag 列表 |
| 操作 | — | 详情按钮（占位）+ 删除按钮（二次确认） |

### 交互说明

- 任意筛选项变化触发 `handleFilter()`，重置页码为 1 后重新加载
- 删除：`ElMessageBox.confirm` 二次确认，成功后刷新列表
- 分页：支持切换页码和每页条数（10 / 20 / 50）
- 整体样式、配色、组件用法与 `Employees.vue` 保持一致

---

## 已知限制

- **技能筛选精度：** `skill` 参数对 `required_skills`（逗号分隔的自由文本）做模糊匹配，而 `filter-options.skills` 来自规范化的 `skills` 表。两者数据可能不完全一致（如 "Python3" vs "Python"），属已知限制，可接受。
- **列表响应不含 `role` / `grade_required`：** 这两个字段不在列表页展示，不包含在 GET /api/requirements 的返回结构中。

## 不在本次范围内

- 新增需求弹窗（按钮占位，后续实现）
- 需求详情子页面（按钮占位，后续实现）
- 推荐顾问的手动添加/删除功能（后续实现）
- 匹配算法（后续实现）
