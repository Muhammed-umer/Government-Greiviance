# API & AI Adapters Documentation

## Core API Endpoints

### Auth (Passwordless Mock OTP)
- `POST /auth/request-otp` - Request OTP code (returns `123456` in local dev mode).
- `POST /auth/verify-otp` - Verify OTP and receive JWT access token.
- `GET /auth/me` - Get current user profile and role details.

### Citizen Petitions
- `POST /petitions` - Submit a new grievance (Triggers AI auto-routing & duplicate deduplication).
- `GET /petitions/me` - List citizen's own petitions with linked shared incident progress.
- `GET /petitions/{id}` - Detailed petition view.
- `POST /petitions/{id}/attachments` - Upload image/pdf/audio evidence (MIME & size validated).
- `POST /petitions/{id}/feedback` - Submit 1-5 star satisfaction rating.
- `POST /petitions/{id}/appeal` - Reopen petition for supervisor review.

### Officer & Shared Incidents
- `GET /incidents` - Query deduplicated shared operational tickets.
- `GET /incidents/{id}` - Detailed view with anonymized citizen impact and linked count.
- `POST /incidents/{id}/priority-override` - Override priority score with mandatory reason saved to audit log.
- `POST /incidents/{id}/actions` - Log field verification, status update, or resolution.

### Officer & Human Triage
- `GET /officer/queue` - Officer dashboard metrics & queue.
- `GET /triage/tasks` - List tasks requiring human review (<0.75 AI confidence or candidate duplicate).
- `POST /triage/tasks/{id}/resolve` - Manually route, link, or split shared incident.

### Admin & Governance
- `GET /admin/departments` - List TN departments.
- `GET /admin/categories` - List grievance categories.
- `GET /admin/audit-events` - Searchable audit trail.
- `GET /admin/analytics/dashboard` - Backlog, SLA compliance, duplicate link rate, and AI confidence breakdown.

---

## AI Adapter System Architecture

1. **Speech to Text**: Sarvam Saaras v3 / Mock Adapter (`services/api/src/services/ai/stt.py`)
2. **Text to Speech**: Sarvam Bulbul v3 / Mock Adapter (`services/api/src/services/ai/tts.py`)
3. **Department Classifier**: IndicBERT / Keyword Mock Adapter (`services/api/src/services/ai/classifier.py`)
4. **Duplicate Deduplication**: Qwen Embedding + Reranker / Mock Vector Distance (`services/api/src/services/ai/duplicate.py`)
