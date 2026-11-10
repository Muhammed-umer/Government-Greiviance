## Your Role

You are a principal full-stack software engineer and AI systems architect with experience building secure, high-scale government digital services.

You are responsible for delivering a working, production-ready application—not diagrams, generic advice, or mock-only screens.

You have expertise in:

- Next.js, TypeScript, responsive PWA development, and accessible bilingual interfaces
- Python FastAPI, PostgreSQL, PostGIS, pgvector, Redis, Celery, Docker, and REST APIs
- Secure role-based access control, audit logs, file uploads, OTP authentication, and privacy-by-design
- Tamil, English, and Tanglish AI workflows for speech-to-text, text-to-speech, department classification, and duplicate grievance matching
- Test-driven development, database migrations, Docker Compose, CI-ready code, and production deployment practices

Work as an implementation owner. Make sensible technical decisions, implement the complete vertical slice first, test every important workflow, and report only completed work and genuine limitations.

Build a production-ready, full-stack **Tamil Nadu Government Grievance Portal** in this workspace. Work code-first: do not spend time creating architecture diagrams, ER diagrams, slide decks, or long design documents. Implement the application, tests, Docker setup, migrations, and a concise README.

## Goal

Create a bilingual, mobile-first grievance portal where citizens can submit a complaint by typing or recording their voice in Tamil, English, or Tanglish. The system must suggest the correct department, find similar active civic issues, and prevent officers from handling the same real-world issue as many separate tickets.

The core principle is:

> One real-world issue can have many private citizen petitions, but officers work from one shared incident.

## Required stack

Use this stack:

```text
Frontend:     Next.js (App Router) + TypeScript + Tailwind CSS
Backend:      Python 3.12 + FastAPI + SQLAlchemy 2 + Alembic
Database:     PostgreSQL + PostGIS + pgvector
Async jobs:   Redis + Celery
File storage: MinIO / S3-compatible storage
Auth:         OTP-ready mock authentication for local development; role-based access control
Testing:      Vitest/Playwright for frontend; pytest for backend
Deployment:   Docker Compose for local development
```

Use a monorepo structure:

```text
apps/
  web/                 # Next.js citizen and officer portal
services/
  api/                 # FastAPI API and business rules
  worker/              # Celery tasks
infra/
  docker-compose.yml
docs/                  # concise setup and API notes only
```

## Product rules

### Petition and incident model

Never replace every citizen's complaint with one token.

- Create a unique private **Petition ID** for every citizen submission.
- Create a **Shared Incident ID** for the real-world operational issue.
- Link multiple petitions to one Shared Incident when they concern the same issue.
- A citizen can only view their own petitions.
- Authorised officers can view the Shared Incident, linked-petition count, priority, SLA, work history, and anonymised impact information.
- Do not expose citizen phone numbers, names, or exact private addresses in the shared incident view.

### Roles

Implement these roles and protect routes/API actions appropriately:

- `citizen`
- `operator` - call-centre / CSC assisted filing
- `officer`
- `supervisor`
- `admin`
- `auditor`

### Citizen features

Implement:

- Tamil and English UI, with language switcher
- Login screen using a local-development OTP mock flow
- New grievance form
- Text complaint input
- Voice-recording UI using browser microphone APIs
- Location input: current location where permitted, address/landmark input, and map-point fallback
- Attachment upload for images, PDFs, and audio
- Review screen before submission
- Personal Petition ID confirmation page
- "My petitions" list, status timeline, linked shared-incident status without exposing other citizens
- Feedback form
- One appeal/reopen request flow
- Responsive PWA-friendly UI

### Officer features

Implement:

- Officer dashboard with open/high-priority/SLA-at-risk metrics
- Department queue with filters: status, priority, category, location, SLA risk
- Shared Incident detail screen
- Linked petition count and anonymised aggregate impact
- Petition evidence view only for authorised users
- Assignment, reassignment, field-visit update, resolution update, and closure workflow
- Officer priority override with mandatory reason
- Human triage queue for uncertain department routing and duplicate matching

### Supervisor/admin features

Implement:

- Department/service/category management
- SLA policy management
- Routing rule management
- Officer assignment management
- Dashboard for backlog, SLA performance, category volume, duplicate-link rate, and AI confidence distribution
- Audit log search

## Priority logic

Implement priority as an explainable rules engine, not a black-box AI score.

```text
Safety severity:        0-40
Verified public impact: 0-25
Critical location:      0-15
SLA risk:               0-10
Recurrence:             0-10
Total:                  0-100
```

- `high`: 70-100
- `medium`: 40-69
- `low`: 0-39
- Any life-safety issue, such as fire, live electrical wire, open manhole, severe flooding, or similar configured rule: high immediately.
- Count distinct verified reporters, not raw repeated submissions.
- Officers can override priority only with a mandatory explanation saved to the audit log.

## AI integration design

Implement an AI service abstraction with provider interfaces, deterministic local mock providers, and environment-variable configuration. The app must run locally without paid API keys.

Create interfaces and adapters for:

1. **Speech to text**
   - Production adapter target: Sarvam Saaras v3
   - Local/mock adapter: return controlled transcript fixtures
   - Citizen must review/edit the transcript before submitting.

2. **Text to speech**
   - Production adapter target: Sarvam Bulbul v3
   - Local/mock adapter: return a local placeholder audio URL or no-op response
   - Use only approved templated status messages; never let TTS invent decisions.

3. **Department/category routing**
   - Production adapter target: fine-tuned IndicBERT
   - Mock adapter: keyword/rule classifier with confidence score
   - Return category, department, issue type, extracted landmark/location hints, confidence, and explanation.
   - If confidence is below `0.75`, create a human-triage task instead of automatic routing.

4. **Duplicate retrieval and verification**
   - Production targets: Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B
   - Local/mock adapter: deterministic similarity based on category, normalised keywords, and distance.
   - Search only relevant active/recent incidents.
   - Require category compatibility, location/asset match, time-window check, and similarity score.
   - Suggested thresholds:
     - `>= 0.85`: auto-link for low-risk civic cases, while allowing citizen disagreement
     - `0.65-0.84`: create triage task / require officer confirmation
     - `< 0.65`: create a new Shared Incident
   - Never auto-link sensitive categories: abuse, corruption allegation, domestic violence, or individual entitlement/benefit disputes.

Persist AI inference input metadata, output, confidence, provider/model version, final decision, human override, and timestamp for auditability.

## Database and migrations

Create Alembic migrations and SQLAlchemy models for at least:

- users, roles, user_roles, otp_sessions
- departments, offices, services, grievance_categories, routing_rules
- petitions, petition_attachments, petition_status_history
- shared_incidents, incident_locations, incident_status_history
- incident_petition_links
- assignments, officer_actions, field_verifications
- sla_policies, sla_events
- priority_assessments, priority_overrides
- ai_inferences, triage_tasks, model_feedback
- notifications, feedback, appeals
- audit_events

Use UUID primary keys, timestamps, soft deletion where appropriate, foreign keys, proper indexes, and PostGIS geometry/geography columns for locations. Enable pgvector and include an embedding column/index for Shared Incidents.

Seed realistic local demo data for departments such as Municipal Corporation, Public Works, Water Supply, Electricity, Sanitation, Traffic Police, Revenue, and Health.

## API requirements

Build clean FastAPI endpoints with Pydantic validation, OpenAPI documentation, error handling, pagination, filtering, RBAC, and tests.

At minimum implement endpoints for:

```text
POST   /auth/request-otp
POST   /auth/verify-otp
GET    /auth/me

POST   /petitions
GET    /petitions/me
GET    /petitions/{petition_id}
POST   /petitions/{petition_id}/attachments
POST   /petitions/{petition_id}/feedback
POST   /petitions/{petition_id}/appeal

GET    /incidents
GET    /incidents/{incident_id}
PATCH  /incidents/{incident_id}
POST   /incidents/{incident_id}/assign
POST   /incidents/{incident_id}/actions
POST   /incidents/{incident_id}/priority-override

GET    /officer/queue
GET    /triage/tasks
POST   /triage/tasks/{task_id}/resolve

GET/POST/PATCH /admin/departments
GET/POST/PATCH /admin/categories
GET/POST/PATCH /admin/sla-policies
GET    /admin/audit-events
GET    /admin/analytics/dashboard
```

## Security and privacy requirements

Implement practical safeguards:

- Role-based authorisation on every endpoint
- Secure passwordless mock OTP handling for local development
- Rate limiting for authentication and complaint submission
- File validation: allow-list MIME types, size limits, checksum, safe object-storage names
- Signed URL pattern for private evidence
- Avoid PII in logs
- PII redaction in shared incident lists and analytics responses
- Audit every state-changing action and every AI decision/override
- CSRF/origin protections as appropriate for the chosen auth flow
- Environment variables for secrets; provide `.env.example`, never hardcode keys

## Implementation expectations

1. First inspect the workspace. Preserve unrelated files.
2. Create the monorepo and implement a functional vertical slice first: citizen submits a complaint -> system routes it -> system either creates or links an incident -> officer sees it and updates status -> citizen tracks the result.
3. Use mocked AI providers by default so `docker compose up --build` works without external credentials.
4. Make production AI provider adapters configurable but disabled by default.
5. Add realistic Tamil/English/Tanglish demo complaints and matching scenarios.
6. Use clear, accessible UI; do not make a generic admin template.
7. Do not create placeholder-only screens. Every key screen must call a functioning API.
8. Add database migrations, seed command, test data, tests, linting, and a concise README with exact commands.

## Completion checklist

Before declaring completion:

- Run frontend lint and tests.
- Run backend tests.
- Run migrations against the Docker Compose PostgreSQL container.
- Seed demo data.
- Verify the vertical slice using the UI/API.
- Verify unauthorised users cannot access other citizens' petitions or protected officer/admin routes.
- Verify duplicate scenarios: high-confidence link, medium-confidence triage, low-confidence new incident, sensitive-case no auto-link.
- Verify priority calculation and officer override audit record.
- Report the files created/changed, commands run, test results, and any deliberate limitations.

Start implementing now. Do not return diagrams or a high-level proposal before writing code.  