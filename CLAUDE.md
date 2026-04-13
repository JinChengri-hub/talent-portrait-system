# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

人才画像系统（Talent Portrait System）— an internal HR management system for tracking employees, projects, skills, performance, and training. Built for a consulting firm context where "competency" means department (DE/Platforms/RC), "grade" means seniority (SM/M/S/C), and "YTD UT" means year-to-date utilization rate.

## Commands

### Start both services
```bash
bash start.sh
```

### Backend (FastAPI)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Frontend (Vue)
```bash
cd frontend
npm run dev       # dev server at http://localhost:5173
npm run build     # production build
```

### Seed test data
```bash
cd backend
venv/bin/python seed_data.py
```

### Database (PostgreSQL via Postgres.app)
```bash
psql -U jinchengri -d talent_portrait
```

## Architecture

### Backend (`backend/`)
- **Framework**: FastAPI with async SQLAlchemy 2.0 (all DB calls are `async/await`)
- **DB**: PostgreSQL via `asyncpg` driver; URL in `backend/.env`
- **Pattern**: `models/` → `schemas/` → `routers/` — each router file maps to a domain
- **Currently only `routers/employees.py` is registered** in `main.py`. Other routers need to be added to `app.include_router(...)` when implemented.
- `Performance` model has two FKs to `employees` (`employee_id` and `reviewer_id`) — always use `foreign_keys="Performance.employee_id"` / `"Performance.reviewer_id"` on relationships to avoid SQLAlchemy ambiguity errors.

### Frontend (`frontend/src/`)
- **Framework**: Vue 3 (Composition API + `<script setup>`), Vite, Pinia, Vue Router, Element Plus
- **Global dark theme**: all Element Plus component overrides live in `src/assets/styles/global.css`. Component-level style tweaks go in `<style scoped>` of each `.vue` file.
- **All Element Plus icons are globally registered** in `main.js` — no per-component imports needed.
- **API proxy**: Vite proxies `/api/*` → `http://localhost:8000`, so `axios` base URL is just `/api`.
- **State**: `src/stores/layout.js` (Pinia) holds sidebar collapsed state shared between `AppSidebar.vue` and `AppHeader.vue`.
- **Layout**: `AppLayout.vue` wraps every authenticated page with `AppSidebar` + `AppHeader` + `<router-view>`.

### Key domain models
| Model | Table | Notes |
|-------|-------|-------|
| Employee | employees | GPN = unique ID; counsellor_id = self-referential FK |
| EmployeeProject | employee_projects | junction; `is_current` flags active assignment |
| EmployeeSkill | employee_skills | skill level 1–5 |
| Performance | performance | rating: EX/ME/NI; voc_score: float |
| TrainingCPE | training_cpe | training_type: CPE/certification/internal/external |
| Project | projects | status: active/completed/pending |
| Skill | skills | category: SAP/前端/后端/数据/管理 |

## Database
- Connection: `postgresql+asyncpg://jinchengri@localhost:5432/talent_portrait` (no password, local)
- Tables are auto-created on startup via `Base.metadata.create_all`
- No Alembic migrations are configured yet — schema changes require manual table recreation or raw SQL
