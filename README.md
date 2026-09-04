# NeuroNexus — SIF Precursor Early Warning (Frontend)

Smart India Hackathon 2026 · Team **NeuroNexus**
Problem Statement: AI/NLP Engine to Detect Serious Injury & Fatality (SIF) Precursors in OIL's Unsafe-Act / Unsafe-Condition and Near-Miss Reports.

This repository contains the **frontend only** — the React/Tailwind dashboard and visualization layer owned by Dev Member 2 (Frontend & Visualization).

---

## 1. Project Overview

The system does not simply classify one safety report. It connects **multiple reports** across semantic similarity, site/location, activity, hazard, barrier failure, and temporal recurrence to surface **recurring SIF precursor patterns**, and produces an **explainable priority/alert** for HSE teams to review.

This frontend receives those results (from the FastAPI backend, or from local mock data during development) and visualizes them — it does **not** implement any of the underlying NLP/ML logic.

## 2. Core Innovation, Visualized

```
Safety Reports → Structured Signals → Cross-Report Relationships →
Recurring Pattern → SIF Precursor → Explainable Evidence → HSE Alert → Human Review
```

The **Precursor Detail** page is built specifically to make this obvious to a judge in 2–4 minutes: risk score → "why was this flagged?" → contributing reports → relationship graph & timeline → HSE review action.

## 3. Tech Stack

- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Router v6
- React Flow (`reactflow`) — relationship graph
- Recharts — single priority-distribution chart
- Lucide React — icons
- Fetch API (no Axios dependency needed)

No Redux, no auth, no analytics, no paid services.

## 4. Architecture

```
Backend (FastAPI) / Mock data
          ↓
services/api.ts  OR  services/mockApi.ts
          ↓
services/adapters.ts   (normalize* functions)
          ↓
Stable frontend model (types/index.ts)
          ↓
Pages (Dashboard, PrecursorDetail, ReportDetail)
          ↓
Reusable components
```

`services/dataService.ts` is the **single switch point** between mock and real data, controlled by `VITE_USE_MOCK_DATA`. No component ever branches on mock-vs-real — they only ever import from `dataService.ts` and consume the stable types.

## 5. Folder Structure

```
src/
├── components/
│   ├── layout/        AppShell, Header, Sidebar
│   ├── dashboard/      OverviewCards, PriorityPrecursor, PrecursorCard,
│   │                    PrecursorFilters, ReviewQueue, PriorityDistributionChart
│   ├── precursor/      PrecursorHeader, EvidencePanel, ContributingReports,
│   │                    Timeline, ReviewActions
│   ├── report/         ReportHeader, RawReport, SafetySignals, RelatedPrecursor
│   ├── graph/           RelationshipGraph (React Flow)
│   └── common/          Badge, PriorityBadge, StatusBadge, Button, Modal,
│                         EmptyState, ErrorState, LoadingSkeleton, DemoDataBadge
├── pages/               Dashboard.tsx, PrecursorDetail.tsx, ReportDetail.tsx
├── services/            api.ts, mockApi.ts, dataService.ts, adapters.ts
├── data/                mockData.ts   (PROTOTYPE / REPRESENTATIVE DATA)
├── types/               index.ts       (stable frontend domain model)
├── hooks/               useAsync.ts
├── lib/                 date.ts, display.ts
├── App.tsx, main.tsx, index.css
```

## 6. Installation

```bash
npm install
```

## 7. Running Locally

```bash
npm run dev
```

Opens at `http://localhost:5173`. Works fully offline in mock mode — no backend required.

## 8. Environment Variables

Copy `.env.example` to `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=true
```

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Base URL of the FastAPI backend (no trailing slash) |
| `VITE_USE_MOCK_DATA` | `true` = use local mock data. `false` = call the real API. |

## 9. Mock / Demo Mode

With `VITE_USE_MOCK_DATA=true` (default), the app runs entirely on `src/data/mockData.ts` via `src/services/mockApi.ts`, including simulated network latency and **in-memory persistence of review actions** for the session (Confirm/Dismiss/Investigate actually change state and reflect in the dashboard).

All demo values are clearly marked in the UI with a **"Prototype / Representative Data"** badge and are not implied to be real OIL statistics.

## 10. Backend API Integration

Set `VITE_USE_MOCK_DATA=false` and provide `VITE_API_BASE_URL`. The frontend expects:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/dashboard` | Overview + top precursor + precursor list + review queue |
| GET | `/api/precursors` | List precursors (supports query filters) |
| GET | `/api/precursors/:id` | Single precursor detail |
| GET | `/api/precursors/:id/relationships` | Relationship graph nodes/edges |
| GET | `/api/reports/:id` | Single report |
| GET | `/api/reports?ids=a,b,c` | Batch-fetch reports (contributing/related reports) |
| POST | `/api/precursors/:id/review` | Submit Confirm / Dismiss / Investigate |

These paths are centralized in `src/services/api.ts` — update them there if the backend team finalizes different routes.

### Expected JSON shapes (adapter-tolerant)

The adapter layer (`src/services/adapters.ts`) accepts both `camelCase` and `snake_case`, and tolerates missing fields. Example precursor payload:

```json
{
  "id": "P-001",
  "title": "Fall Protection Failure",
  "priority": "HIGH",
  "risk_score": 85,
  "status": "OPEN",
  "hazard": "Fall from height",
  "activity": "Working at height",
  "barrier_failure": "Missing fall protection",
  "site": "Duliajan Field Site A",
  "report_count": 4,
  "recurrence_window_days": 14,
  "short_explanation": "...",
  "evidence": {
    "semantic_similarity": 0.91,
    "hazard_match": true,
    "activity_match": true,
    "barrier_match": true,
    "site_match": true,
    "temporal_recurrence": "HIGH",
    "contributing_report_count": 4,
    "summary_points": ["..."]
  },
  "report_ids": ["R1024", "R1088"],
  "created_at": "2026-07-30",
  "updated_at": "2026-08-04",
  "review_history": []
}
```

Relationship graph payload:

```json
{
  "nodes": [{ "id": "R1024", "type": "report", "label": "Report #1024" }],
  "edges": [{ "source": "R1024", "target": "R1088", "relationship": "same_hazard", "strength": 0.91 }]
}
```

If the backend's field names differ, only `src/services/adapters.ts` needs to change.

## 11. Production Build
> Validation note: this source bundle is prepared for GitHub. In this environment the npm registry was not reachable, so dependencies could not be installed here and a production build could not be executed. Run `npm install`, then `npm run build` locally before merging.


```bash
npm run build
```

Type-checks (`tsc -b`) then bundles with Vite into `dist/`. Preview with:

```bash
npm run preview
```

## 12. Git / GitHub Instructions

```bash
git init
git add .
git commit -m "Build SIH SIF precursor frontend"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

`node_modules/`, `dist/`, and `.env` are excluded via `.gitignore`.

## 13. SIH Demo Flow (2–4 minutes)

1. Open `/dashboard` — judge sees reports analyzed, precursor patterns, high-priority count, review queue, and the top precursor spotlighted.
2. Click the high-priority precursor → risk score, recurrence, hazard, barrier failure, related report count.
3. Read **"Why was this alert generated?"** — explicit evidence, not a black-box claim.
4. Scroll to contributing reports and the relationship graph + timeline — cross-report relationships are visually obvious.
5. Click a contributing report → `/reports/:id` shows Raw Report → Extracted Signals → Related Reports → Precursor.
6. Return to the precursor, click **Investigate** → status updates live to **Under Investigation**.

---

**Remaining integration work (depends on teammates):** final FastAPI endpoint paths/schema from Backend Member 1; real relationship-graph and clustering output from AI/ML Member 2; real extracted-signal confidence values from AI/ML Member 1. Until then, `VITE_USE_MOCK_DATA=true` keeps this frontend fully demoable.


## Dependency note

This project uses ESLint 8.57.1 because the pinned TypeScript ESLint 7.x toolchain requires ESLint 8.x. `@types/node` is included for the Vite path alias configuration.

After extracting/cloning, run:

```bash
npm install
npm run build
npm run dev
```
