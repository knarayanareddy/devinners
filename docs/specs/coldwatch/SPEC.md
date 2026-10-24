# ColdWatch — implementation-ready specification

**Project ID:** `coldwatch`<br>
**Track / family:** Independent agent products / 08<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [2026-10-23-coldwatch-spec.md](../2026-10-23-coldwatch-spec.md) (historical context only)<br>
**Primary audience:** A neighborhood incident captain and volunteers running an opt-in synthetic severe-cold drill

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

During dangerous cold, a small team needs to know who consented to contact, who responded, and which needs or nonresponses still require a person—without broadcasting resident information.

**Product promise:** turn a configured official alert into a captain-approved, consent-filtered outreach plan, bound attempts and classifications, escalate all urgent/unclear/no-answer cases, and coordinate human volunteer tasks without promising response or replacing emergency services.

**Tagline:** Consent-aware cold-weather check-ins with a human captain at every meaningful exception.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Incident captain | Activates/pauses incident, approves exact roster/contact plan, owns escalation, corrections, assignments, and closure. |
| Volunteer | Sees only assigned minimal task details and records verified completion; cannot browse full roster. |
| Resident participant | Synthetic opt-in person with channel/window/language/accessibility preferences and revocation control. |
| Agent service | Runs a short fixed check-in dialogue and proposes response classification; cannot activate, assign, lower severity, or close tasks. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Parse one configured synthetic official alert type and require captain activation bound to alert/roster/contact plan.
- Maintain explicit per-resident channel/time/language/accessibility consent and immediate suppression/revocation.
- Queue sandbox check-ins with per-resident caps, local-time windows, correlation IDs, and cost/channel counters.
- Classify ok/need/urgent/unclear/no-answer with deterministic red-flag backstop and monotonic severity.
- Create captain decisions and minimal volunteer tasks; require resident confirmation/evidence before closure.
- Support pause, resident suppression, classification correction, post-incident export, audit, and restart/idempotency.

### 1.4 Explicit non-goals

- No emergency-service contact, medical advice, injury-prevention claim, or promise that help is on the way.
- No inferred consent from roster presence, public/group disclosure, or treating no answer as safe.
- No real calls/SMS in default build and no autonomous resource allocation or volunteer assignment.
- No open-ended conversation outside the approved short check-in script.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Use one fictional `Severe Cold Drill` alert, 12 synthetic residents, 3 volunteers, Europe/Amsterdam timezone, and a sandbox channel adapter.
- Contact window is 09:00–18:00 local; maximum 2 attempts per resident/incident, 15 minutes apart; no answer after cap creates captain task.
- Raw transcripts are not retained by default; store redacted classification evidence and hashes. Live mode has no configured recipients and must refuse.
- Captain approval expires on any alert, roster/consent, script, or contact-plan change; pause blocks all new outbound effects immediately.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. The alert adapter verifies fixture/source signature, type, geography, and validity; unknown alerts cannot activate.
2. The consent gate computes an eligible roster and exclusions without contacting anyone; captain reviews counts and exact plan hash.
3. Captain activates; transactional outbox queues only currently consented residents in allowed local windows.
4. The sandbox adapter performs one idempotent scripted attempt, records correlation/outcome/cost, and never marks voicemail/no answer OK.
5. The agent classifies the bounded response; deterministic danger-phrase/protocol backstops may raise but never lower severity.
6. Captain handles every need, urgent, unclear, and exhausted no-answer case and may assign a minimal volunteer task.
7. Volunteer records action evidence; resident/captain confirmation closes the task without claiming emergency resolution.
8. Captain can pause/suppress/correct at any point and exports a redacted post-incident report with open/unknown outcomes.

### 2.2 Lifecycle and transition authority

```text
ALERT_RECEIVED → PROFILE_GATE → CAPTAIN_ACTIVATION → OUTREACH_QUEUED → CONTACT_ATTEMPTED → RESPONSE_CLASSIFIED → (OK → FOLLOWUP_SCHEDULED | NEED/URGENT/UNCLEAR/NO_ANSWER → CAPTAIN_DECISION) → VOLUNTEER_TASK → RESIDENT_CONFIRMATION → CLOSED; PAUSED/SUPPRESSED block new contact and preserve open tasks
```

Transition contract:

1. Every resource has an integer `version`, initialized to 1. Mutations require `If-Match` or `expected_version`; successful mutation increments it atomically.
2. The application service loads current state, checks actor and preconditions, invokes pure domain logic, commits the new state plus audit/outbox records in one transaction, then returns the persisted projection.
3. `UNKNOWN`, malformed output, timeout, stale evidence, or provider outage never maps to success. It creates or preserves a visible `NEEDS_REVIEW`/`FAILED_RETRYABLE` state with safe next actions.
4. Retrying a command with the same idempotency key returns the original outcome. A concurrent stale command returns `409 VERSION_CONFLICT`; no last-write-wins updates are allowed.
5. Destructive cancellation is a new audited state, not deletion of history. User-facing deletion/retention behavior is handled by the privacy contract in §9.

### 2.3 Exception journeys

- **Empty/new workspace:** explain the first useful action and offer the committed seed loader; never show fabricated activity.
- **Partial/incomplete input:** save safe draft fields, identify exactly which fields/evidence are missing, and prevent downstream approval until resolved.
- **Agent/provider failure:** keep the durable job and evidence, show `analysis incomplete`, and permit bounded retry or manual review without replaying external effects.
- **Stale approval:** return to review with a field-level diff and require a fresh digest-bound decision; do not silently approve only the delta.
- **Denied action:** explain the policy boundary in neutral language and preserve user work. Provide the authorized human route where one exists.

## 3. Functional requirements

The following capabilities are binding. Acceptance IDs in §13 provide their verification contract.

1. Parse one configured synthetic official alert type and require captain activation bound to alert/roster/contact plan.
2. Maintain explicit per-resident channel/time/language/accessibility consent and immediate suppression/revocation.
3. Queue sandbox check-ins with per-resident caps, local-time windows, correlation IDs, and cost/channel counters.
4. Classify ok/need/urgent/unclear/no-answer with deterministic red-flag backstop and monotonic severity.
5. Create captain decisions and minimal volunteer tasks; require resident confirmation/evidence before closure.
6. Support pause, resident suppression, classification correction, post-incident export, audit, and restart/idempotency.

Cross-cutting functional requirements:

- **FR-C01:** Every list supports cursor pagination, deterministic sorting, URL-persisted filters, an empty state, and an error state. Do not use unbounded offset exports or unbounded agent result sets.
- **FR-C02:** Every asynchronous run exposes queued/running/succeeded/failed/cancelled state, safe progress messages, trace ID, and idempotent retry. Browser refresh or process restart cannot erase it.
- **FR-C03:** Every material output links to its source record/version and policy/model versions. Generated prose is a proposal until the stated human or deterministic gate accepts it.
- **FR-C04:** Search/filter inputs are parameterized; imports and agent content are untrusted. No user content becomes executable code, SQL, shell, templates, or authorization policy.
- **FR-C05:** Exports are immutable derived artifacts with source/approval hashes, schema version, generation time, and read-back validation. A failed export is never represented as complete.
- **FR-C06:** The seeded demo includes one successful path, one refusal/hold, one stale/concurrent action, and one recovered retry using the real product path rather than a separate demo-only controller.

## 4. Domain model and persistence

### 4.1 Project aggregates

Field names are normative; physical types may use the ORM equivalents. IDs are UUIDs, hashes are lowercase SHA-256 hex, and references are foreign keys unless explicitly denormalized for immutable evidence.

| Entity / value object | Required fields | Invariants |
| --- | --- | --- |
| Alert / Incident | `alert_id`, `source`, `external_id`, `type`, `valid_from/to`, `body_hash`; incident `alert_version`, `state`, `captain_id`, `activation_hash` | Unique external alert; exact supported type/geography/current validity; pause/suppress state checked at effect time. |
| Resident / ContactConsent | `resident_id`, `pseudonym`, `language`, `accessibility`, `channel`, `local_timezone`, `suppressed`; consent `scope`, `window`, `granted_at`, `revoked_at`, `version` | Roster presence≠consent; current explicit consent/channel/window required; revocation immediate. |
| OutreachPlan / Activation | `incident_id`, `roster_version`, `resident_ids`, `script_version`, `attempt_policy`, `plan_hash`; approval actor/time | Exact alert/roster/script/plan bound; any change invalidates and stops unstarted queue items. |
| ContactAttempt | `attempt_id`, `resident_id`, `incident_id`, `correlation_id`, `sequence`, `state`, `channel_outcome`, `cost_cents`, `next_allowed_at` | Unique incident/resident/sequence and correlation key; max 2; unknown outcome reconciles before retry. |
| ResponseClassification | `attempt_id`, `model_class`, `backstop_class`, `final_class`, `danger_rule_ids`, `redacted_evidence`, `version` | Final severity=max(model, deterministic backstop, protocol); no-answer/voicemail/unclear cannot be OK. |
| CaptainDecision / VolunteerTask | `decision`, `rationale`, `approved_by`; task `assignee`, `minimal_instructions`, `state`, `completion_evidence`, `resident_confirmation` | Only captain assigns/corrects/closes; volunteer projection excludes unrelated roster/sensitive data. |
| Actor / Session | `id`, `role`, `tenant_id`, `status`; secure HttpOnly session or OIDC identity | Every command derives actor/tenant server-side; client-supplied actor IDs are ignored. |
| ApprovalSnapshot | `id`, `resource_id`, `resource_version`, `content_sha256`, `actor_id`, `expires_at` | Optional where no approval exists; otherwise binds exact displayed payload, evidence, destination, and policy version. |
| AuditEvent | `sequence`, `event_id`, `actor`, `action`, `resource`, `version`, `trace_id`, `payload_hash`, `previous_hash` | Append-only, hash-linked, UTC timestamps; stores references/redacted metadata rather than secrets or raw private content. |
| IdempotencyRecord | `actor_id`, `key`, `request_hash`, `response_status`, `response_body`, `effect_state` | Unique actor/key; same key plus different payload is 409; unknown external effect requires reconciliation. |
| JobRun / OutboxItem | `id`, `type`, `state`, `attempt`, `available_at`, `lease_owner`, `input_hash`, `last_error` | Durable queued/running/succeeded/failed/cancelled states; leasing and heartbeat make retries visible and safe. |

### 4.2 Persistence rules

- Use PostgreSQL 16 for the reference deployment and SQLite WAL only for the documented single-process local demo. Domain tests run against both where behavior differs; never claim multi-worker SQLite safety.
- Use SQLAlchemy 2 + Alembic. Every table has `created_at`; mutable aggregates have `updated_at` and `version`. Add foreign keys, check constraints, tenant/resource indexes, and uniqueness constraints for external IDs and idempotency.
- Store files outside the database in private content-addressed storage (`sha256` key), with original/derived lineage. Local storage is default; S3-compatible storage is an adapter. Database commit and object upload use a resumable two-phase intake state.
- Raw evidence is immutable. Corrections create new versions or annotations. Derived artifacts record code/model/parser versions and input hashes so they can be regenerated or invalidated.
- Approval and audit records contain hashes and minimum necessary metadata, not secrets, access tokens, raw private notes, or unnecessary media/transcripts.

## 5. Technical architecture

### 5.1 Reference topology

```text
React browser (accessible presentation; no secrets or authority)
        │ HTTPS / JSON / secure session
FastAPI application ── pure deterministic domain kernel
        │                   ├── PostgreSQL/SQLite + Alembic
        │                   ├── private object store
        │                   ├── transactional outbox/job worker
        │                   └── append-only audit/hash verifier
        ├── typed agent runtime → schema validation → read-only/proposal tools
        └── allowlisted adapters → sandbox by default; opt-in live provider/MCP
```

The domain kernel is importable without FastAPI, a browser, a model, or network. The agent cannot import privileged mutation services. External writes, when allowed, pass through application commands that re-check current state, actor, approval digest, policy version, idempotency, and adapter outcome.

### 5.2 Required stack and repository layout

| Layer | Required default | Implementation notes |
| --- | --- | --- |
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic | Generate OpenAPI 3.1 from the running app; use uv with a committed lockfile. |
| Agent | Strands Agents SDK with a scripted `Model` implementation offline and an explicitly configured provider for opt-in live smoke | Pin the actually installed SDK; inspect its signatures. No invented hook/interrupt APIs. |
| Frontend | Node 22, React, TypeScript, Vite, React Router, TanStack Query | Use pnpm lockfile; server state remains query cache, forms use accessible controlled components. |
| Styling | CSS custom-property tokens + CSS Modules; system font stack | No remote font dependency. Charts require text/table equivalents and accessible names. |
| Testing | pytest, Hypothesis, Vitest, Testing Library, Playwright, axe-core, Ruff, mypy | Zero collected tests or collection errors fail CI; coverage alone is not correctness. |
| Local services | Makefile + optional Docker Compose | Clean offline setup uses committed fixtures and sandbox adapters; cloud credentials are never required for `make verify`. |

```text
coldwatch/
├── Makefile                 # setup, verify, demo-e2e, eval, live-smoke, clean
├── pyproject.toml / uv.lock
├── package.json / pnpm-lock.yaml / pnpm-workspace.yaml
├── docker-compose.yml       # optional reference services; no secret files
├── apps/api/app/
│   ├── domain/              # pure entities, policies, state machines, calculations
│   ├── application/         # actor-checked commands, queries, approvals, idempotency
│   ├── agent/               # runtime, schemas, bounded tools, scripted provider
│   ├── adapters/            # storage, providers/MCP, clock, ID generation
│   ├── api/                 # routers, OpenAPI errors, dependencies, projections
│   └── workers/             # leased jobs, retries, outbox, reconciliation
├── apps/web/src/
│   ├── routes/ components/ features/ api/ styles/ accessibility/
├── packages/contracts/      # generated OpenAPI client; no hand-divergent copies
├── tests/{unit,integration,security,e2e,accessibility}/
├── evals/{cases,expected,baselines}/  # independent labels and versioned corpus
├── fixtures/                # synthetic/licensed evidence and sandbox responses
└── docs/{acceptance-matrix.md,architecture.md,runbook.md,decisions,eval}/
```

### 5.3 Project integration and processing design

No external provider is required for the core offline build. Live inference is optional and separately evidenced.

A live model is not a completion dependency; if configured, `make live-smoke` must identify provider/model/region, enforce a hard item/dollar cap, and never run in default CI.

Background processing uses durable jobs with bounded exponential backoff and jitter, a maximum attempt count, lease expiry, and dead-letter visibility. Only idempotent read/analysis jobs retry automatically. External effects with unknown outcomes enter `RECONCILIATION_REQUIRED`; never blind-retry them. The API returns `202` with a job URI for work exceeding the normal request budget.

### 5.4 HTTP API contract

The paths below are the minimum product API. Generate the final schema from FastAPI and generate the TypeScript client. Request bodies use explicit typed fields; examples and all error variants belong in OpenAPI.

| Method and path | Actor | Behavior |
| --- | --- | --- |
| POST `/api/v1/alerts/fixtures` / GET `/api/v1/incidents/{id}` | Alert worker/Captain | Ingest supported fixture alert and read activation/roster/queue status. |
| GET `/api/v1/incidents/{id}/activation-preview` | Captain | Return eligible/suppressed counts, plan/roster/script hashes, and contact caps. |
| POST `/api/v1/incidents/{id}/activation` / `/pause` | Captain | Approve exact plan or pause all new effects with idempotency/version checks. |
| PUT `/api/v1/residents/{id}/consent` / POST `/api/v1/residents/{id}/suppress` | Authorized consent manager/Captain | Grant/revoke/suppress; queued attempts revalidate immediately before effect. |
| POST `/api/v1/attempts/{id}/sandbox-outcome` | Sandbox adapter | Record signed scripted outcome and enqueue bounded classification; duplicate-safe. |
| GET `/api/v1/incidents/{id}/captain-queue` | Captain | List need/urgent/unclear/no-answer/capacity cases with redacted evidence. |
| POST `/api/v1/cases/{id}/decision` / POST `/api/v1/tasks` | Captain | Correct classification, assign volunteer, schedule follow-up, or hold with rationale. |
| POST `/api/v1/tasks/{id}/completion` / GET `/api/v1/incidents/{id}/report` | Assigned volunteer/Captain | Record evidence/confirmation and export redacted post-incident outcomes. |
| GET `/api/v1/health/live` | anonymous | Process liveness only; no dependency or sensitive details. |
| GET `/api/v1/health/ready` | anonymous | Checks database/migrations and required local services; never performs paid model calls. |
| GET `/api/v1/audit?resource_id=…` | authorized auditor/owner | Cursor-paginated, redacted, resource-scoped audit projection. |
| GET `/api/v1/jobs/{id}` | owner/authorized operator | Returns durable progress, failure category, trace ID, and safe retry availability. |

Common API semantics:

- `POST` creation returns `201`; asynchronous analysis returns `202`; successful reads/updates return `200`; deactivation/deletion returns `204` where appropriate. Writes accept `Idempotency-Key` and `expected_version` where relevant.
- Error envelope: `{"status": 409, "code": "VERSION_CONFLICT", "detail": "Safe human-readable message", "trace_id": "…", "fields": {}}`. Use `400` malformed syntax, `401` unauthenticated, `403` forbidden action, `404` absent/other tenant, `409` state/version/idempotency conflict, `422` semantically invalid content, `429` bounded rate limit, and `503` unavailable required dependency.
- List responses are `{"items": [], "next_cursor": null}`; cursors are opaque and tenant-bound. Maximum page size is 100. Upload limits, allowed media types, and timeouts are server-enforced.
- Approval payloads contain the exact `content_hash`, evidence hashes, policy/rule version, destination, and expected resource version. Any mutation invalidates the approval before effects occur.

## 6. Agent, model, and tool boundary

### 6.1 Allowed tools

All tool inputs/outputs are Pydantic schemas with maximum sizes. Read tools return minimal scoped projections, not raw database access. Proposal tools create no authoritative state.

| Tool | Kind | Contract and guard |
| --- | --- | --- |
| get_approved_checkin_script | read | Returns current script/version/localized approved prompts only; no free-form outreach policy. |
| get_attempt_response | read | Returns current bounded redacted sandbox response and protocol outcome. |
| propose_response_classification | proposal | Returns enum and cited response spans; deterministic backstop computes final severity. |
| get_captain_task_summary | read | Returns existing decisions/tasks; no assignment, emergency, or outbound mutation tool. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

At every dequeue, re-check incident active, alert valid, plan/activation hash current, resident not suppressed, consent current, channel allowed, local time 09:00–18:00, attempt count<2, next_allowed_at, and global/channel/resident caps. Commit a leased attempt/outbox key before adapter invocation. Adapter success is not resident safety: `no_answer`, `voicemail`, `timeout`, `unknown`, and malformed response map to captain review.

Define severity order `OK < FOLLOWUP < NEED < URGENT`. Deterministic rules inspect normalized explicit danger phrases and protocol states and return at least `UNCLEAR` for missing/ambiguous content. `final = max(model_proposal, phrase_backstop, protocol_backstop)`; model output can never lower it. No-answer attempts follow bounded retry schedule then create a captain task. Closure requires a verified task outcome plus resident/captain confirmation appropriate to the task.

| Policy area | Normative rule |
| --- | --- |
| Activation/consent | Only known alert + exact captain approval + current resident consent/channel/window can produce an attempt; each condition tested independently and together. |
| No false promises | Fixed scripts and output scanners prohibit arrival promises, medical claims, or claims that volunteers/emergency services were contacted unless verified event fields support the statement. |
| Privacy | Captain sees minimum necessary case data; volunteers see assigned task only; group/public projections contain no resident identifiers or sensitive responses. |
| Pause/recovery | Pause/suppression invalidates unstarted outbox items; duplicate alerts/webhooks/restarts cannot double-call/assign or lose acknowledged decisions. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** A high-clarity incident console with deep navy surfaces, amber attention states, large queue counters, and resident privacy emphasized over dramatic emergency styling. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #8a4b12; --color-accent-ink: #ffffff;
  --color-success: #16734a; --color-warning: #8a5300; --color-danger: #b42318;
  --color-info: #175cd3; --color-focus: #7c3aed;
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px;
  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
  --shadow-card: 0 1px 2px rgb(16 24 40 / .06), 0 4px 16px rgb(16 24 40 / .05);
  --font-body: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Consolas, monospace;
}
```

Do not download Inter; the system fallback is the default offline rendering. Body text is 16px/1.5 minimum, metadata 14px/1.45 minimum, page titles `clamp(1.75rem, 3vw, 2.5rem)`, and numeric/timecode data uses tabular numerals. Text contrast is at least 4.5:1, large text and meaningful graphics 3:1. Accent foreground/background combinations must be measured and adjusted rather than assumed from the token.

### 8.2 Information architecture and screens

Desktop uses a 240px navigation rail, a fluid content column capped at 1440px, and contextual detail panels. Mobile uses a top bar plus bottom-sheet/drawer navigation; primary workflows become one column. Do not put primary actions only in hover menus.

| Route | Screen | Required content and actions |
| --- | --- | --- |
| /incidents | Incident list | Current/paused/closed drills, alert validity, open captain tasks, contact caps, and New fixture drill. |
| /incidents/{id}/activation | Activation preview | Official alert evidence, eligible/excluded consent counts, script/plan hash, attempt policy, and captain approval. |
| /incidents/{id}/console | Captain console | Consent-filtered outreach states, urgent/unclear/no-answer queues, pause control, and cost/attempt counters. |
| /cases/{id} | Resident case | Minimal contact/consent state, redacted response evidence, severity backstop, retry state, and captain decision. |
| /tasks | My volunteer tasks | Only assigned minimal instructions, status, completion evidence, and help/escalation; no roster browser. |
| /incidents/{id}/report | Post-incident report | Reached/unresolved/unknown denominators, task outcomes, redacted audit, and export without deleting history. |
| /admin/policy | Drill policy | Official source/script versions, contact windows/caps, channel kill switch, retention, and sandbox/live label. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **ConsentGateSummary:** eligible and excluded counts with reason categories; never exposes excluded residents to unauthorized volunteers.
- **CaptainQueue:** severity text/icon, age, attempt state, redacted evidence, and explicit Decide action; no-answer never appears in OK.
- **AttemptTimeline:** correlation/sequence/channel outcome/cost/retry and uncertainty, with raw transcript absent by default.
- **IncidentKillSwitch:** always-visible Pause contact with scope/consequence confirmation and queued-effect count; resuming requires fresh approval.
- **EvidenceLink / SourceDrawer:** opens page/span/timecode/row/source version beside the current task; keyboard focus moves into the drawer and returns to the invoking link on close.
- **StatusBadge:** pairs icon and text (`Verified`, `Needs review`, `Unknown`, `Stale`, `Failed`), never color alone. Use `role=status` only for meaningful asynchronous changes, not every render.
- **ApprovalPanel:** shows actor, exact version, evidence/destination summary, changes since prior approval, and explicit approve/reject actions. Disable with an explanation while stale or invalid.
- **JobProgress:** exposes queued/running/failed states, trace ID, elapsed time, and safe retry. Progress is honest; use indeterminate progress when no denominator exists.
- **DataTable:** semantic table on desktop, labeled card/list representation only when it preserves relationships on narrow screens. Sort state is announced; filters are removable chips with a clear-all action.
- **Toast + persistent result:** toast confirms navigation-safe success but consequential errors and approvals also remain inline. Toasts never contain the only route to recovery.

### 8.4 Responsive, accessibility, and content requirements

- At 320 CSS px width there is no two-dimensional page scroll except genuinely tabular/media content, which gets an accessible labeled scroll region. At 200% and 400% zoom the primary journey remains operable.
- Minimum pointer target is 24×24 CSS px with adequate spacing; target 44×44 for primary mobile actions. Dragging, hover, waveform, color, or spatial reasoning always has an equivalent control.
- Use semantic landmarks, one `h1`, logical heading order, visible 2px focus indicator, skip link, labels/instructions, `autocomplete` where appropriate, and native buttons/inputs before ARIA. No positive `tabindex`.
- On async completion, announce a concise result and move focus only when the user initiated a route/dialog change. Errors are summarized at the top and linked to fields; focus goes to the summary after failed submit.
- Motion uses no autoplay decorative animation; honor `prefers-reduced-motion`. Media has captions/transcripts and audio-only evidence has textual alternatives. Pause/stop controls are keyboard accessible.
- Plain-language copy states what is known, what is uncertain, what happens next, and who has authority. Never use “AI verified”, “guaranteed”, “safe”, “compliant”, or “optimal” unless the deterministic contract actually proves that exact claim.
- Apply an **Impeccable / UI UX Pro Max-style design review lens** as a final craft pass: intentional hierarchy, consistent spacing, typography, purposeful color, realistic content, complete interaction states, responsive composition, accessibility, and concise copy. These are review lenses, not runtime dependencies or substitutes for WCAG 2.2 AA.

### 8.5 UI acceptance matrix

| State | Required design/behavior |
| --- | --- |
| Loading | Skeleton matches final geometry; controls that would be invalid are disabled with label; no fake percentages. |
| Empty | Explains the value and next action; seed demo is separate from real import/create. |
| Partial / unknown | Shows available facts and explicit missing evidence; unknown never inherits success styling. |
| Error / offline | Persistent plain-language message, trace ID, preserved input, retry/manual path; stale data is timestamped. |
| Success | Shows persisted/read-back result and source version, not merely a toast or optimistic assumption. |
| Approval / refusal | Exact payload/version and consequence; refusal explains the gate and authorized next step. |

## 9. Security, privacy, and abuse controls

- **Threat model:** cover unauthenticated access, IDOR/cross-tenant reads, privilege escalation, malicious uploads, stored/reflected XSS, CSRF, SSRF, prompt injection, tool abuse, replay/concurrency, webhook forgery, resource exhaustion, sensitive logs, and dependency compromise. Document STRIDE-style threats and mitigations in `docs/architecture.md`.
- **Session/API:** secure, HttpOnly, SameSite cookies; CSRF token for cookie-authenticated writes; strict CORS allowlist; TLS in deployment; server-side rate limits and body/time limits. Secrets come from the environment/secret manager and never appear in client bundles.
- **Uploads:** hash and sniff media type, enforce per-project extension/MIME/codec/page/duration/pixel limits, generate random storage keys, strip unnecessary metadata, scan where appropriate, and serve downloads with `nosniff` and safe disposition. Never execute imports or render active HTML/SVG inline.
- **Agent isolation:** use separate credentials and minimal scopes for every adapter. Egress allowlists and request schemas prevent arbitrary URLs. Web/search/log/document content cannot alter system instructions or select new tools.
- **Privacy:** Raw transcripts/audio are disabled; redacted response evidence deletes 7 days after incident closure. Contact details delete 30 days after closure; minimal audit/action hashes remain 90 days. Exports contain aggregate/pseudonymous outcomes only.
- **Audit:** hash-chain verification runs at startup and on demand. The chain detects accidental/tampered application records; it is not represented as protection against an attacker who controls both database and signing keys. Production hardening should anchor/sign checkpoints externally.
- **Security gates:** no open critical/high findings; dependency and secret scans enabled; tests prove cross-tenant `404`, CSRF/replay rejection, injection containment, upload limits, and redaction. A mock authorization test alone is insufficient.

## 10. Non-functional requirements and observability

### 10.1 Measurable budgets

| Dimension | Required target for the seeded reference environment |
| --- | --- |
| API interactivity | At 20 requests/second for 5 minutes, p95 reads <400 ms and p95 synchronous writes <800 ms, excluding declared model/media jobs; error rate <1% with no correctness errors. |
| Web experience | Production build on throttled mobile: LCP ≤2.5 s, CLS ≤0.1, INP ≤200 ms for primary navigation; lazy-load media and detail panels. |
| Reliability | Kill/restart API and worker during each job phase; no lost accepted state, duplicate effect, or success-shaped incomplete result. |
| Capacity | The committed seed and eval corpora run within 4 GB RAM locally; all queries/jobs have page, row, time, attempt, and byte limits. |
| Accessibility | WCAG 2.2 AA manual checklist; zero critical/serious axe violations on every route; complete keyboard and screen-reader primary journey. |

These are engineering regression budgets, not internet-scale claims. Record hardware, dataset, command, and percentiles. If a target cannot be measured in the environment, report it unmeasured rather than passing it by assertion.

### 10.2 Telemetry and operations

- Structured logs include `trace_id`, `job_id`, actor/tenant pseudonymous IDs, route, status, duration, adapter/model versions, and safe outcome category. Never include raw evidence, session secrets, contact details, or full prompts.
- Metrics cover request rate/errors/latency, queue depth/age, job retries/failures, stale evidence, approval invalidations, adapter outcome/cost, and project-specific quality counters. Add tracing across API → domain → agent/tool → adapter.
- `/health/live` is shallow; `/health/ready` verifies migrations and required local dependencies. A provider outage degrades only dependent analysis and leaves review/history available.
- Runbook documents setup, seed/reset, backup/restore, migration/rollback, retention deletion, hash-chain verification, kill switch, spend cap, provider disable, incident triage, and recovery from unknown effects.
- Backups are encrypted and restore-tested. Rollback preserves audit evidence and disables external writes before reverting code. Demo reset is explicit and impossible in production mode.

## 11. Seed data, evaluation, and demonstration

### 11.1 Committed dataset and licenses

Commit 12 synthetic resident personas and at least 100 drill cases: explicit/understated urgent, benign controls, nonresponse/voicemail, multilingual responses, consent revoked between queue/dequeue, wrong local time, duplicate alert/webhook, pause/restart, script injection, false promises, unknown adapter outcome, and volunteer privacy canaries. Run each urgent persona 20 times and preserve every trial.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Escalation recall | 100% urgent and no-answer cases reach captain across all trials; report phrase/backstop/model contributions and false alarms separately. |
| Consent/activation | Zero attempts without every current precondition; zero effects after pause/revocation; all stale activation hashes refused. |
| Language/promises | Zero unverified arrival/contact/medical claims in outbound scripts/classifications/reports across adversarial corpus. |
| Privacy/recovery | Zero roster/canary leaks by role; duplicate/restart tests produce one attempt/task and preserve acknowledged decisions. |
| Classification quality | Report per-language precision/recall, understated-red-flag misses, unclear abstention, and 20-run trial counts; no real-world safety claim. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Ingest the supported cold-alert fixture and reject an unknown alert type.
2. Preview the consent-filtered roster, activate the exact plan, and show a revoked resident skipped at dequeue.
3. Run a no-answer attempt through retry cap and show it held for captain, never marked safe.
4. Classify an understated urgent response and show deterministic backstop severity precedence.
5. Captain assigns one minimal volunteer task; volunteer completes it without accessing the full roster.
6. Pause the incident, verify no new sandbox effects, and export the redacted report/audit with unresolved counts.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Alert/source contract, consent roster, pure activation/contact policy, fixture channel, and negative tests.
2. Incident/outreach state machines, durable outbox/caps/pause/revocation, and restart/reconciliation tests.
3. Strands fixed-dialogue/classifier path, deterministic severity backstop, multilingual/adversarial eval.
4. Captain decisions/volunteer tasks/privacy projections/report and accessible console.
5. 100-case/20-run eval, channel kill-switch and cost proof, deployment/runbook, and scripted drill.

Before each slice, update `docs/acceptance-matrix.md` with criterion → module/symbol → automated/manual test → expected result → evidence path → status. `not implemented`, `blocked`, and `failed` are distinct; no blank status counts as passed.

Implementation agent deliverables:

- Source, lockfiles, migrations, container/local setup, generated OpenAPI/client, seed manifest, licenses, tests, eval corpus/report, accessibility notes, and working browser build.
- Architecture/ADR records for any deviation, data-flow and threat model, API/state diagrams, operations/backup/rollback runbook, and `.env.example` with non-secret placeholders.
- A data/feature truth matrix marking each path `implemented-scripted`, `implemented-live`, `simulated`, `blocked-external`, or `not implemented`; include exact source revision and command output.
- No real account creation, contact, payment, filing, publication, or production data without separate explicit authorization. Do not ask for credentials in chat or commit them.

## 13. Verification and acceptance traceability

### 13.1 Required commands

| Command | Truthful contract |
| --- | --- |
| `make setup` | Installs exact locked dependencies and local services/fixtures without cloud credentials; fails nonzero on setup errors. |
| `make verify` | Runs formatting/lint, strict types, unit/domain/property, API/integration, security, UI, production build, migration, and accessibility checks; zero tests or collection failure fails. |
| `make demo-e2e` | Runs §11.3 through the real application and agent/tool/policy path using sandbox effects; produces Playwright trace and audit assertion. |
| `make eval` | Regenerates §11.2 from versioned cases; exits nonzero on safety-threshold failure or missing/unlabeled cases. |
| `make live-smoke` | Opt-in only; refuses without explicit enable flag, isolated configuration, hard item/dollar cap, and kill switch. Never part of default CI. |

### 13.2 Source acceptance criteria — all required

“Core” is required for offline completion. “Integration” may be externally blocked during development but is required before claiming full/integrated completion; it can never be replaced by a screenshot or fixture presented as live.

| ID | Requirement | Verification / retained evidence | Lane |
| --- | --- | --- | --- |
| CW-01 | no contact without current resident consent, allowed local time, valid channel, and active incident; test each condition independently and in combination. | API authorization/privacy integration tests with two tenants/actors and canary values; inspect model prompts, responses, exports, caches, and logs. | Core |
| CW-02 | an unknown alert type or profile event cannot activate an incident; captain approval is bound to the alert, roster version, and contact plan. | State-machine and API negative tests for wrong actor, stale digest/version, replay, and concurrent requests; assert zero external side effects. | Core |
| CW-03 | no answer/voicemail/ambiguous response never becomes `OK`; retry cap and explicit captain task are deterministic. | Unit/property tests with hand-calculated and boundary fixtures, plus API round-trip tests; failures must be fail-first and reproducible. | Core |
| CW-04 | deterministic red-flag backstop may raise but never lower model severity; missed phrases and false alarms are separately counted. | Unit/property tests with hand-calculated and boundary fixtures, plus API round-trip tests; failures must be fail-first and reproducible. | Core |
| CW-05 | outbound text/voice cannot promise an arrival time or claim a volunteer/emergency service was contacted unless a verified event proves it. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| CW-06 | roster data is per-role; public/group messages contain no resident name, address, health condition, or sensitive response. Logs redact transcript content by default. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| CW-07 | duplicate alert/webhook or restart cannot double-call, double-assign, lose an acknowledged decision, or close a task without response evidence. | Concurrency and integration tests deliver exact duplicates, legitimate near-duplicates, reordered events, and retries; assert one intended effect and no lost positive control. | Core |
| CW-08 | test and live adapters have separate hard caps, kill switches, rate limits, and visible cost counters. Live mode requires an explicit environment flag plus partner configuration. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| CW-09 | use synthetic residents, scripted adversarial content, nonresponse, language variants, understated red flags, and benign controls. Report recall and precision with misses; no safety claim from a simulator alone. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| CW-10 | scripted drill shows alert, consent-filtered queue, a no-answer held for captain, one approved volunteer task, and the append-only trace. No real calls/messages occur. | API authorization/privacy integration tests with two tenants/actors and canary values; inspect model prompts, responses, exports, caches, and logs. | Core |
| CW-11 | captain can pause the incident, suppress a resident, correct a classification, and export a post-incident report without deleting history. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |

### 13.3 Additional global gates

| Gate | Pass condition |
| --- | --- |
| G-01 Traceability | All 11 source criteria plus FR-C01…C06 map to implementation and retained evidence; no orphan or unverified criterion. |
| G-02 Authorization | Automated two-actor/two-tenant matrix covers every endpoint and tool; no cross-tenant data, side effect, cache key collision, or agent context leak. |
| G-03 Failure honesty | Fault injection covers malformed model output, timeout, outage, stale data, duplicate/reordered events, worker kill, and unknown effect; all fail visibly and closed. |
| G-04 UI quality | Every route/component in §8 exists with all states; keyboard/mobile/screen-reader/zoom journey passes and design-review checklist has no unresolved serious issue. |
| G-05 Reproducibility | Two clean offline runs from the same revision produce equivalent domain/eval artifacts; differences in stochastic/provider lanes are separately reported. |
| G-06 Truthful delivery | README and demo distinguish synthetic/simulated/live; no unsupported impact, compliance, safety, or production claims; external blockers remain explicit. |

## 14. Completion rubric and definition of done

### 14.1 Weighted score (100 points)

| Category | Weight | Full-credit evidence |
| --- | --- | --- |
| Product workflow and scope | 15 | All §1 scope and §2 journeys work end to end; non-goals are not substituted for the core workflow. |
| Domain correctness and provenance | 20 | Entities/invariants, deterministic policy, source links, calculations/matching, migrations, and failure precedence pass all tests. |
| Agent and integration boundary | 15 | Real agent loop with scoped tools, structured proposals, adversarial containment, truthful sandbox/live lanes, and required adapter evidence. |
| UI/UX and accessibility | 15 | All routes, responsive states, evidence/approval interactions, WCAG 2.2 AA checks, and polished design-review pass. |
| Security, privacy, and abuse resistance | 15 | Authorization matrix, upload/egress controls, retention/deletion, audit integrity, redaction, and security suites pass with no high/critical issue. |
| Verification and evaluation | 10 | Traceable acceptance matrix, meaningful fail-first tests, reproducible eval report with denominators/misses, and clean-clone repeatability. |
| Operations and handoff | 10 | Setup/demo/runbook/backup/rollback/kill switch, observability, performance evidence, licenses, and truthful feature matrix are complete. |

**Score rule:** award 0 / 50% / 100% of each category only from retained evidence (no partial fractions otherwise). Full completion requires **≥90/100, no category below 80% of its weight, every hard gate below, and every applicable §13 criterion passed**. A rubric score cannot compensate for a hard-gate failure. The optional live-model lane is reported separately and is not required for offline completion; its absence must not be hidden or simulated.

### 14.2 Non-compensable hard gates

- No unauthorized external effect, approval bypass, cross-tenant disclosure, hard-constraint override, or fabricated source/evidence in any test.
- No safety-critical corpus false-positive where §11 or the source criterion requires zero; every miss remains visible and blocking.
- No credentials in source/logs, no real private data in fixtures, no hidden network/paid calls in `make verify` or `make demo-e2e`.
- `make setup`, `make verify`, `make demo-e2e`, and `make eval` work from a clean clone; missing tests/eval cases cannot produce a green result.
- The main workflow is usable by keyboard and screen reader at mobile/desktop widths; status and uncertainty are honest and perceivable.
- No live/integrated claim without actual provider/deployment evidence. An external blocker limits the completion label rather than licensing a fake adapter claim.

### 14.3 Final handoff checklist

- [ ] Exact revision, lockfiles, migrations, seed/eval manifest hashes, and generated API schema archived.
- [ ] Command logs, JUnit/results, Playwright traces, eval report, accessibility manual checklist, and performance environment archived.
- [ ] Acceptance matrix has no blank status; failures and external blockers are listed in the README.
- [ ] Demo displays one success and one consequential refusal/hold, plus evidence and audit provenance.
- [ ] Threat model, privacy/retention tests, restore/rollback drill, kill switch, and spend controls verified.
- [ ] Product copy and report avoid legal/medical/safety/impact claims beyond demonstrated evidence.

## 15. Pilot boundary and change control

The standalone build is complete only against the synthetic/sandbox contract above. A real deployment requires a named partner, approved sources and policies, participant consent, retention schedule, staffed human escalation, security review, and rehearsed disable/restore procedure. These are pilot gates, not excuses to leave the specified demo workflow unfinished.

Pre-pilot partner decisions for this project:

- Name local alert authority, incident captain/on-call coverage, language reviewers, and volunteer liability/policy owner.
- Obtain explicit resident consent, approved contact windows/channels/scripts, retention, and staffed manual emergency guidance.
- Separately authorize live channels with hard caps, allowlists, kill switch, reconciliation, and a partner drill before any real outreach.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for ColdWatch.**
