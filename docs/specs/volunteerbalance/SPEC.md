# VolunteerBalance — implementation-ready specification

**Project ID:** `volunteerbalance`<br>
**Track / family:** Independent agent products / 02<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [2026-10-23-volunteerbalance-spec.md](../2026-10-23-volunteerbalance-spec.md) (historical context only)<br>
**Primary audience:** Mutual-aid coordinators and adult volunteers scheduling recurring non-emergency work

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

Spreadsheet scheduling can expose personal reasons, miss hard availability or rest constraints, and treat equal shift counts as fair even when duration and travel differ.

**Product promise:** propose deterministic feasible schedules, quantify workload without claiming moral objectivity, let each volunteer accept or decline their own assignments, and keep uncovered or disputed work visible to the coordinator.

**Tagline:** Private constraints in; explainable, consent-based rota proposals out.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Coordinator | Defines tasks/period policy, reviews proposals/exceptions, and publishes only after required responses. Cannot read private reason text. |
| Volunteer | Owns private constraints and public availability effects; responds only to own assignments and may offer a bounded counterproposal. |
| Auditor | Sees redacted allocation/audit metrics, never private reasons. |
| Agent service | Summarizes approved preference effects and proposes candidate swaps; cannot publish, alter capacity, or reassign accepted work. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Create scheduling periods with tasks, skills, locations, duration, priority, rest rules, and coordinator workload policy.
- Let volunteers privately enter availability, maximum minutes/shifts, travel limits, preferences, and visibility settings.
- Generate a reproducible constraint-valid proposal with uncovered-work and infeasibility explanations.
- Show capacity-adjusted burden and travel/duration distributions with formulas and persisted inputs.
- Support per-assignment accept/decline/counter, version-bound approvals, and minimal reopening after changes.
- Publish a redacted accepted rota, export calendar/CSV, and preserve audit/exception history.

### 1.4 Explicit non-goals

- No employment, emergency, medical, caregiving, or disciplinary allocation.
- No inference of sensitive reasons, public volunteer ranking, punitive scores, or automated acceptance.
- No automatic reassignment of accepted shifts or relaxation of hard limits to fill a rota.
- No volunteer-to-volunteer contact exchange without the specified mutual consent.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Use a fictional adult mutual-aid group, 8 volunteers, 12 tasks, one-week periods, Europe/Amsterdam timezone, and 30-minute scheduling granularity.
- Use OR-Tools CP-SAT pinned in the lockfile, fixed seed 0, one solver worker, 10-second limit, and stable UUID tie-breaking; `UNKNOWN` timeout is not feasible.
- Fairness policy is frozen before intake: burden is assigned minutes divided by approved maximum minutes; travel is reported separately and never inferred from private reasons.
- Publication requires every non-cancelled assignment to be accepted; uncovered tasks remain explicitly unpublished and coordinator-owned.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Coordinator creates tasks and freezes hard constraints, fairness formula, and response deadline before invitations.
2. Each volunteer enters private reasons separately from machine-usable constraints and previews exactly what coordinators can see.
3. The deterministic allocator validates input, solves, and persists candidate assignments plus objective/status and uncovered tasks.
4. The agent explains the proposal using only opaque constraint effects; it cannot access private reason fields.
5. Volunteers accept or decline their own assignments; a decline reopens only that assignment and dependent swaps.
6. Coordinator reviews uncovered/disputed work and may request a new solve, never edits an accepted assignment directly.
7. After all responses, coordinator approves the exact rota/recipient projection and publishes the redacted version.
8. Export/read-back verifies accepted assignments, versions, and absence of private canary fields.

### 2.2 Lifecycle and transition authority

```text
PERIOD_DRAFT → PRIVATE_INTAKE → PROPOSAL_READY → VOLUNTEER_REVIEW → COORDINATOR_REVIEW → PUBLISHED → IN_PROGRESS → CLOSED; any affected change → NEEDS_HUMAN → VOLUNTEER_REVIEW; branches DECLINED and CANCELLED remain audited
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

1. Create scheduling periods with tasks, skills, locations, duration, priority, rest rules, and coordinator workload policy.
2. Let volunteers privately enter availability, maximum minutes/shifts, travel limits, preferences, and visibility settings.
3. Generate a reproducible constraint-valid proposal with uncovered-work and infeasibility explanations.
4. Show capacity-adjusted burden and travel/duration distributions with formulas and persisted inputs.
5. Support per-assignment accept/decline/counter, version-bound approvals, and minimal reopening after changes.
6. Publish a redacted accepted rota, export calendar/CSV, and preserve audit/exception history.

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
| SchedulingPeriod / Task | period `policy_version`, `state`, `response_deadline`; task `start`, `end`, `location_id`, `skill_ids`, `priority`, `required_people`, `prerequisite_ids` | Task end>start; skills/location references valid; dependency graph acyclic; policy immutable after intake opens. |
| VolunteerProfile / PrivateConstraint | `volunteer_id`, `max_minutes`, `max_shifts`, `skills`, `travel_limit`; constraint `effect_type`, `effect_payload`, `private_reason_ciphertext`, `visibility` | Allocator/model projections contain effects and opaque IDs only; private reason plaintext never leaves owner record. |
| Assignment | `id`, `task_id`, `volunteer_id`, `proposal_version`, `state`, `response_version`, `accepted_at` | Unique active volunteer/task; accepted assignment cannot move without a new affected proposal and response. |
| ScheduleProposal | `id`, `period_id`, `input_hash`, `solver_version`, `seed`, `status`, `objective`, `bound`, `assignments`, `uncovered[]` | Fixed inputs/version reproduce byte-stable canonical proposal; OPTIMAL only with solver proof. |
| FairnessReport | `proposal_id`, `formula_version`, `volunteer_metrics[]`, `range`, `mean_absolute_deviation`, `caveats` | Every value recomputes from accepted capacities/durations; row order cannot affect output. |
| Consent / RotaPublication | pair `consent_state`, `expires_at`; publication `rota_hash`, `recipient_scope`, `approved_by`, `version` | No contact exchange without current pair consent; publication hash covers all accepted assignments and redacted fields. |
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
volunteerbalance/
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
| POST `/api/v1/periods` / POST `/api/v1/periods/{id}/tasks` | Coordinator | Create draft period/tasks; freeze policy when intake opens. |
| PUT `/api/v1/me/availability` / PUT `/api/v1/me/constraints` | Volunteer | Versioned private intake; response separates owner and coordinator projections. |
| POST `/api/v1/periods/{id}/proposals` | Coordinator | Run solver asynchronously with input hash and deterministic config. |
| GET `/api/v1/proposals/{id}` / GET `/api/v1/proposals/{id}/fairness` | Authorized scoped roles | Return role-redacted assignments, solver status, uncovered reasons, and fairness calculations. |
| POST `/api/v1/assignments/{id}/response` | Owning volunteer | Accept/decline/counter exact assignment version; duplicate response is idempotent. |
| POST `/api/v1/proposals/{id}/resolve` | Coordinator | Request re-solve or keep uncovered work; cannot set acceptance for a volunteer. |
| POST `/api/v1/periods/{id}/publish` | Coordinator | Approve exact rota hash and recipient scope after response gate. |
| GET `/api/v1/periods/{id}/rota.csv` / `.ics` | Published participants | Download accepted role-scoped rota; response includes content hash for read-back. |
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
| list_candidate_assignments | read | Returns proposal assignments and opaque constraint effects for the authorized period only. |
| explain_fairness | read | Returns persisted formula inputs/results; no arithmetic generated by the model. |
| propose_swap | proposal | Suggests task/volunteer IDs for deterministic revalidation; cannot write or trigger messages. |
| draft_rota_summary | proposal | Uses accepted/public fields only and labels uncovered tasks; private reasons are absent from context. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

Canonicalize tasks and volunteers by UUID before constructing CP-SAT. Hard constraints enforce availability, skill, location/travel limit, rest interval, max shifts/minutes, prerequisite timing, exclusive volunteer/resource overlap, and required headcount when feasible. If no complete solution exists, produce the best explicitly labeled partial proposal only from a separate diagnostic solve whose objective minimizes weighted uncovered slots; never present that partial result as satisfying required coverage.

For volunteer `v`, `burden_v = assigned_minutes_v / max_minutes_v` when max_minutes>0; zero capacity forces zero assignments and no division. Report min/max/range, mean absolute deviation, total minutes, travel minutes, and shift count. Objective lexicographically minimizes uncovered priority weight (diagnostic only), burden range scaled to integer millionths, total travel, then canonical assignment key. Fixed solver version/seed/workers and canonical serialization ensure stable artifacts.

| Policy area | Normative rule |
| --- | --- |
| Private projection | Reason text is encrypted/access-controlled separately. Coordinator, solver, agent, notifications, exports, and logs receive only effect type/time/location and opaque constraint ID. |
| Consent state | Silence is not consent. Acceptance binds assignment/version; changed time, task, volunteer, or dependent swap invalidates only affected responses. |
| Infeasibility | Return named conflicting constraint IDs and uncovered tasks with suggested human inputs to inspect; never relax a rule or invent availability. |
| Publication | Only accepted, current assignments enter the public rota. Declined/uncovered work stays in coordinator exception view and audit history. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** A humane scheduling tool with clear calendar geometry, soft teal accents, private/public preview cues, and fairness shown as transparent distributions rather than leaderboards. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #0f6f68; --color-accent-ink: #ffffff;
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
| /periods | Scheduling periods | Draft/open/published periods, response counts, uncovered count, and Create period. |
| /periods/{id}/tasks | Task builder | Accessible calendar and list editor, skill/location requirements, conflicts, and frozen-policy summary. |
| /me/availability | My private availability | Week grid with equivalent form/list controls, max workload, travel, private reason field, and visibility preview. |
| /proposals/{id} | Proposal review | Rota by person/task, solver status, uncovered work, and candidate swap impact preview. |
| /proposals/{id}/fairness | Fairness explanation | Formula, per-volunteer burden bars with table equivalent, travel/minutes distributions, and caveats; no ranking labels. |
| /me/assignments | My assignments | Proposed/accepted cards with exact details, accept/decline/counter, stale-version diff, and calendar export. |
| /periods/{id}/publish | Coordinator publication | Response checklist, unresolved exceptions, redacted rota preview, recipient scope, approval, and audit link. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **AvailabilityGrid:** pointer painting has add/remove time-range forms and keyboard navigation; busy/free is textually labeled.
- **PrivacyPreview:** two explicit panels “I can see” and “Coordinator can see”; private reason never appears in the latter.
- **AssignmentCard:** state, time zone, location, duration, version, and response actions; acceptance requires an unchecked explicit action.
- **FairnessDistribution:** labeled bars plus sortable table and formula disclosure; does not use red/green moral judgments or volunteer ranks.
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
- **Privacy:** Private reason text is deleted 7 days after period closure by default; scheduling effects persist for 90 days, then are anonymized. Audit retains opaque constraint IDs and action hashes, not reasons. Deletion covers query caches, prompts, exports, and search indexes.
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

Commit 40 synthetic scheduling scenarios with 8 adult profiles, skill/location/rest boundaries, infeasible periods, equal-count/unequal-duration controls, zero capacity, travel limits, private canary reasons, stale responses, duplicate webhooks, and row-order permutations. Include expected canonical proposals and independent hand/naive constraint validation.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Hard constraints | Zero availability/skill/location/rest/capacity/overlap violations across all proposals and property tests. |
| Reproducibility/fairness | Byte-stable canonical output across row permutations/restarts; 100% fairness values independently recomputed. |
| Allocation quality | Report filled priority weight, burden range/MAD, travel, uncovered tasks, solver status/time, and human overrides against a first-fit baseline; no forced coverage target. |
| Privacy and consent | Zero private canaries in any non-owner projection/prompt/log/export; zero publications/contact exchanges without current required consent. |
| Recovery | 100% duplicate/restart/stale/concurrent tests preserve one correct assignment state and visible uncertain outcomes. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Coordinator opens a seeded period and freezes the fairness policy.
2. Two volunteers enter different private constraints; the coordinator projection shows only availability effects.
3. Generate a proposal, independently inspect its fairness formula, and attempt an infeasible swap that is refused.
4. Volunteer A accepts while Volunteer B declines; no rota is published yet and only B’s assignment reopens.
5. Resolve the open slot, collect acceptance, publish the redacted rota, and verify calendar/CSV output.
6. Inspect audit and privacy canary results, then restart and show pending state preserved.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Pure canonical constraint model, CP-SAT adapter, fairness formulas, naive validator, and property tests.
2. Private intake/role projections, task builder, canary leakage tests, and accessible availability UI.
3. Strands explanation/swap proposal path with fixed tools, schemas, and agent authorization tests.
4. Response/consent state machines, stale versions, publication/export, event log, and restart tests.
5. Scenario eval, responsive polish, performance/recovery checks, operations guide, and demo.

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
| VB-01 | clean setup and `make verify` work without credentials or network; fixed seed produces byte-stable proposals. | Clean-clone CI job with network and credentials disabled; run twice, compare deterministic artifacts, and retain dependency/test logs. | Core |
| VB-02 | no generated proposal violates availability, skills, max shifts, location, or rest interval; property tests cover boundary values. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| VB-03 | every score is recomputable from persisted inputs and versioned formula; changing order of input rows does not change the result. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| VB-04 | if no feasible allocation exists, preserve uncovered tasks and surface a coordinator decision. Never relax a hard limit to make the rota look complete. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| VB-05 | a seeded private reason is absent from every other volunteer’s API projection, model request, log, notification, and exported rota. Include canary tests for direct, paraphrased, encoded, and split text; no claim of perfect semantic leak detection. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| VB-06 | no volunteer-to-volunteer contact or schedule publication before both relevant participants consent; test conditional language, silence, decline, stale consent, and duplicate taps. | Concurrency and integration tests deliver exact duplicates, legitimate near-duplicates, reordered events, and retries; assert one intended effect and no lost positive control. | Core |
| VB-07 | unknown tool/action denied by default. The agent cannot publish, reassign an accepted shift, alter someone’s cap, or reveal a reason. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| VB-08 | approval is bound to the exact proposal version and affected volunteers; a changed task or availability makes the old approval invalid. | State-machine and API negative tests for wrong actor, stale digest/version, replay, and concurrent requests; assert zero external side effects. | Core |
| VB-09 | duplicate event delivery does not double-assign; restart preserves pending decisions and accepted assignments; uncertain writes are shown as uncertain, never replayed blindly. | Concurrency and integration tests deliver exact duplicates, legitimate near-duplicates, reordered events, and retries; assert one intended effect and no lost positive control. | Core |
| VB-10 | versioned synthetic scenarios report hard-constraint violations (must be 0), fairness distribution, unfilled work, and human override rate. Publish all failures and the baseline formula. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| VB-11 | a volunteer can set availability privately, understand one proposed shift, accept/decline, and see the effect without needing to use a group chat; keyboard, screen-reader, and narrow-screen checks pass. | Playwright keyboard/mobile journeys, axe-core, and documented NVDA/VoiceOver plus 200%/400% zoom checks; retain screenshots and manual notes. | Core |

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

- Confirm real scheduling/rest/travel rules and who may freeze policy or publish a period.
- Approve plain-language privacy/consent text, retention, and manual dispute fallback with coordinators and volunteers.
- Run discovery with at least three coordinators and five adult volunteers before claiming retention or fairness impact.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for VolunteerBalance.**
