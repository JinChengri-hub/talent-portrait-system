# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

人才画像系统（Talent Portrait System）— an internal HR management system for tracking employees, projects, skills, performance, and training. Built for a consulting firm context where "competency" means department (TC-/BC-/RC- prefixed), "grade" means seniority (SM/M/S/C), and "YTD UT" means year-to-date utilization rate.

## Commands

### Start both services (Windows — run in bash/Git Bash)
```bash
bash start.sh
```

### Backend (FastAPI) — Windows PowerShell
```bash
cd "C:\Users\Ze Yu Wang\Desktop\talent-portrait-system\talent-portrait-system\backend"
uvicorn app.main:app --reload
```

### Frontend (Vue)
```bash
cd frontend
npm run dev       # dev server at http://localhost:5173
npm run build
```

### Database
- Connection string (in `backend/.env`): `postgresql+asyncpg://postgres:ey123456@localhost:5432/talent_portrait`
- psql access: `psql -U postgres -d talent_portrait`
- For SQL files containing Chinese characters on Windows, always use: `psql -U postgres -d talent_portrait --set=client_encoding=UTF8 -f <file>`
- For Chinese strings with encoding-problematic characters (e.g. 开发), use PostgreSQL Unicode escapes: `U&'\5F00\53D1'`
- No Alembic — schema changes require manual `ALTER TABLE` or raw SQL

## Architecture

### Backend (`backend/`)
- **Framework**: FastAPI with async SQLAlchemy 2.0 (all DB calls are `async/await`)
- **Pattern**: `models/` → `schemas/` → `routers/` — each router file maps to a domain
- **Registered routers** in `main.py`: `employees`, `projects`, `requirements`
- Tables are auto-created on startup via `Base.metadata.create_all`
- `Performance` model has two FKs to `employees` — always use explicit `foreign_keys=` on relationships to avoid SQLAlchemy ambiguity

### Frontend (`frontend/src/`)
- **Framework**: Vue 3 (Composition API + `<script setup>`), Vite, Pinia, Vue Router, Element Plus
- **Global dark theme**: overrides in `src/assets/styles/global.css`. Component-level tweaks go in `<style scoped>`
- **All Element Plus icons are globally registered** in `main.js` — no per-component imports needed
- **API proxy**: Vite proxies `/api/*` → `http://localhost:8000`; axios base URL is `/api`
- **State**: `src/stores/layout.js` (Pinia) holds sidebar collapsed state
- **Layout**: `AppLayout.vue` wraps every page with `AppSidebar` + `AppHeader` + `<router-view>`

### Key domain models
| Model | Table | Notes |
|-------|-------|-------|
| Employee | employees | GPN = unique ID; counsellor_id = self-referential FK |
| EmployeeProject | employee_projects | junction; `is_current` flags active assignment |
| EmployeeSkill | employee_skills | skill level 1–5 |
| Performance | performance | rating: EX/ME/NI |
| Project | projects | `code_type` = 所有机会 (BD/已赢); `project_type` = 项目类型 (实施/运维等); `competency` = department |
| ProjectRequirement | project_requirements | `fiscal_year` format: FY21–FY26; `required_skills` = comma-separated string |
| RequirementConsultant | requirement_consultants | junction with UniqueConstraint(requirement_id, employee_id) |
| Skill | skills | category: SAP/前端/后端/数据/管理 |

### Known patterns & gotchas
- **Array params**: FastAPI needs `skill=a&skill=b` (not `skill[0]=a`). Frontend uses a custom `serializeParams()` with `URLSearchParams` in `src/api/requirements.js`
- **Count queries**: `selectinload` cannot be used in subqueries for count — build the base query without it, then add `.options(selectinload(...))` only on the data-fetch query
- **Scoped CSS + teleported dialogs**: `el-dialog` teleports to `<body>` by default, breaking `:deep()` selectors. Use `:teleported="false"` on dialogs that need scoped style overrides
- **Consultant updates**: always `await db.flush()` after deleting `RequirementConsultant` records before re-inserting, to avoid unique constraint violations within the same transaction
- **Competency options**: 13 fixed options (TC-/BC-/RC- prefixes) — hardcoded in frontend, not read from DB
- **匹配状态 options**: 7 fixed options — hardcoded in frontend
