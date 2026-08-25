# Agent Instructions — Subscription Tracker & Renewal Dashboard

**Time budget: 50 minutes total.** Optimize for a working, gradable app — not polish. Read `reference.md` for exact schemas/formulas before writing code; do not re-derive them.

## Hard Constraints (graded)
1. **All business logic, calculations, validation, and computation run server-side.** Frontend only renders and captures input. Never compute burn rate, normalized cost, or days-until-renewal in JS.
2. **In-memory store only** — a Python list/dict on the server. No database, no localStorage, no ORM setup. Speed over persistence.
3. **Commit incrementally and meaningfully** after each step below. Do not do one giant commit at the end — commit history is graded.
4. Repo must be public on GitHub, pushed before **09:30 PM today**. Stop coding with enough buffer to `git push` and submit the link on Unstop.

## Stack (fastest reliable path)
- Backend: **FastAPI** + Pydantic (matches reference.md models exactly) + Uvicorn.
- Frontend: **single static HTML/JS file** (vanilla JS, fetch calls to the API). No build step, no framework — a React/Vite setup burns time you don't have. Skip animated count-ups, skip localStorage.
- Serve frontend via FastAPI static mount or open the HTML file directly against `http://localhost:8000`.

## Build Order (commit after each step)
1. **Models + in-memory store + CRUD routes** (`GET/POST/PUT/DELETE /api/v1/subscriptions`, `PATCH /toggle`) — no logic yet, just scaffolding. → commit: "scaffold: models and CRUD routes"
2. **Engines**: `calculate_normalized_monthly_cost()` and `evaluate_renewal_urgency()` per reference.md formulas, wired into GET responses and `/metrics`. → commit: "feat: cost normalization and renewal urgency engines"
3. **Frontend skeleton**: entry form (4 fields) + subscription table, fetching from the API, rendering plain (no styling). → commit: "feat: frontend form and table wired to API"
4. **Toggle + Vibe Check**: wire toggle switch → `PATCH /toggle` → refetch → apply `.row-paused` class + amber "Renewing Soon" badge. → commit: "feat: active/paused toggle with live metric recalculation"
5. **Styling pass**: apply CSS tokens from reference.md (dark theme, badge, paused row, toggle switch). Keep it minimal — correctness over glow effects. → commit: "style: dashboard theme and badges"
6. **Quick sanity check** against the Edge Cases table in reference.md (overdue, same-day, boundary at 7 days, decimal rounding). Fix anything broken. → commit: "fix: edge case corrections" (only if needed)
7. `git push`, confirm repo is public, submit link.

## Explicitly skip (do not spend time on)
- Database/persistence across restarts
- Auth, multi-user support
- Animated UI transitions, glassmorphism blur effects, glow gradients
- Comprehensive test suite — write 3-4 quick assertions against the edge-case table if time allows, otherwise skip
- README beyond a few lines (how to run backend + open frontend)

If time runs short, prioritize in this order: working CRUD + engines > toggle/Vibe Check working correctly > amber badge > styling.