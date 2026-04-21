# Employee Profile Page — Design Spec
Date: 2026-04-21

## Overview
开发员工画像页面（EmployeeProfile.vue），从员工列表操作列「查看」按钮进入，路由 `/employees/:id`。
页面分为顶部信息卡片和下方 4 个 Tab 面板。

---

## 1. 数据加载策略

| 内容 | 加载时机 | 接口 |
|------|---------|------|
| 基本信息卡片 + 技能列表 | 页面打开 | `GET /api/employees/{id}` |
| 项目经历 Tab | 首次切换时，之后缓存前端变量 | `GET /api/employees/{id}/projects` |
| 培训记录 Tab | 首次切换时，之后缓存前端变量 | `GET /api/employees/{id}/trainings` |
| 绩效考评 Tab | 首次切换时，之后缓存前端变量 | `GET /api/employees/{id}/performances` |

---

## 2. 后端变更

### 2.1 数据库新增字段
```sql
ALTER TABLE employees ADD COLUMN IF NOT EXISTS phone VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS effective_ut FLOAT;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);
```
注：`name_en` 已存在于 Employee 模型，无需新增。

### 2.2 employee_skills.level 迁移
从 1-5 改为 0-100（步长 10）的整数，迁移公式：`new_level = old_level * 20`。
执行前先做预检，确认无异常数据：
```sql
-- 预检：应返回 0 行，否则需人工处理
SELECT COUNT(*) FROM employee_skills WHERE level NOT BETWEEN 1 AND 5;
-- 迁移
UPDATE employee_skills SET level = level * 20 WHERE level BETWEEN 1 AND 5;
```
同步更新 `EmployeeSkill` 模型注释：`comment="技能等级 0-100，步长10"`

### 2.3 接口清单

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/employees/{id}` | 扩展现有接口，返回字段见 2.4 |
| PUT | `/api/employees/{id}` | 扩展，支持修改 phone / email / location |
| POST | `/api/employees/{id}/avatar` | 上传头像，返回 avatar_url |
| PUT | `/api/employees/{id}/skills` | 批量保存技能列表（全量替换） |
| GET | `/api/employees/{id}/projects` | 返回项目经历列表 |
| GET | `/api/employees/{id}/trainings` | 返回培训记录列表 |
| GET | `/api/employees/{id}/performances` | 返回绩效考评列表 |

### 2.4 GET /api/employees/{id} 返回字段

**EmployeeDetail schema 新增字段：**
- `name_en`: str | None
- `phone`: str | None
- `effective_ut`: float | None（只读）
- `avatar_url`: str | None
- `counsellor_name_en`: str | None
- `counsellor_grade`: str | None
- `counsellor_email`: str | None

`skills[].level` 值域从 1-5 改为 0-100（步长 10）。

**EmployeeUpdate schema 新增字段（可写）：**
- `phone`: str | None
- `location` 已存在
- `email` 已存在

注：`effective_ut` / `avatar_url` 不通过 PUT 更新，分别由外部数据源和专用 avatar 接口管理。

### 2.5 头像上传
- 文件存储路径：`backend/uploads/avatars/{employee_id}_{timestamp}.{ext}`
- 支持格式：image/jpeg、image/png、image/webp
- 最大文件大小：2MB
- 返回：`{ "avatar_url": "/uploads/avatars/{filename}" }`
- `main.py` 需挂载静态目录，并在 startup 时自动创建目录：
  ```python
  import os
  from fastapi.staticfiles import StaticFiles
  os.makedirs("uploads/avatars", exist_ok=True)
  app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
  ```

### 2.6 Tab 接口响应字段

**GET /api/employees/{id}/projects：**
```
[ { id, project_name, project_code, role, team_name, start_date, end_date, is_current } ]
```

**GET /api/employees/{id}/trainings：**
```
[ { id, training_name, training_type, hours, start_date, completed_date, status } ]
```
注：`description` 字段不返回（本次范围外）。

**GET /api/employees/{id}/performances：**
```
[ { id, year, quarter, rating, voc_score, comments } ]
```

---

## 3. 前端页面结构

### 3.1 信息卡片布局
```
┌─────────────────────────────────────────────────────────────┐
│  [头像]     姓名（中文）  英文名                    [编辑按钮] │
│  [上传]     ─────────────────────────────────────────────── │
│  [状态徽章]  Competency        │  GPN                       │
│             职级               │  Location                  │
│             邮箱               │  电话                      │
│             Counsellor [悬浮卡]│  入职日期                  │
│             当前项目           │  YTD UT  │  Effective UT   │
└─────────────────────────────────────────────────────────────┘
```

**编辑模式（卡片级别，单次切换所有可编辑字段）：**
- 点击编辑按钮：Location / 邮箱 / 电话 同时变为输入框，其余字段保持只读
- 右上角变为「取消」+ 「保存」按钮
- 只读字段：GPN、姓名、英文名、Competency、职级、Counsellor、入职日期、当前项目、YTD UT、Effective UT

### 3.2 Counsellor 悬浮卡
使用 `el-popover` trigger="hover"，展示：
- 首字母缩写头像（cyan 背景）
- 中文姓名 / 英文名
- 职级
- 邮箱

### 3.3 技能评估 Tab

**布局：** 左 50% 雷达图 + 右 50% 技能列表

**雷达图规则：**
- 轴 = 当前技能列表中的技能名（动态）
- 值 = 对应 level（0-100）
- 若技能数量为 0，显示空状态提示而非雷达图
- 最多展示 10 条技能维度；超过 10 条时雷达图只取前 10，其余仍在列表中显示
- 任意技能/等级变更 → 雷达图实时响应（computed 驱动）

**技能列表：**
- 每行：技能名称（el-select，从 skills 字典选择）+ 等级（el-select，选项：0% / 10% / 20% / ... / 100%）+ 删除按钮
- 底部：「+ 添加技能」按钮
- 独立「保存技能」按钮 → 调用 `PUT /api/employees/{id}/skills`（全量替换）
- 后端实现须 `await db.flush()` 删除旧记录后再插入新记录，避免唯一约束冲突

### 3.4 项目经历 Tab
表格列：项目名称 / 项目代码 / 角色 / 团队 / 开始日期 / 结束日期 / 是否当前（tag 标记）

### 3.5 培训记录 Tab
表格列：培训名称 / 类型 / 时长（小时）/ 开始日期 / 完成日期 / 状态（tag 标记）

### 3.6 绩效考评 Tab
表格列：年份 / 季度 / 评级 / VoC 评分 / 备注

---

## 4. 本次范围外
- 项目经历 / 培训记录 / 绩效考评的新增、编辑、删除
- 头像以外的文件上传
- 权限控制
