# RunOfShow — implementation-ready specification

**Project ID:** `runofshow`<br>
**Track / family:** Agentic Cinema / ClickHouse alternate 01<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [10-runofshow.md](../10-runofshow.md) (historical context only)<br>
**Primary audience:** A small live-event producer and stage manager coordinating cues, cameras, graphics, audio, and segment deadlines

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

When an event runs late, producers need feasible options that preserve required coverage and dependencies. Historical durations can help, but empty/out-of-distribution history and solver uncertainty must remain visible.

**Product promise:** validate a versioned cue DAG/coverage matrix, query actual ClickHouse history through MCP, compute feasible schedule alternatives deterministically, and export only a producer/stage-manager-approved plan without controlling the show.

**Tagline:** Cue coverage and recovery options grounded in event history and hard constraints.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Producer | Imports run-of-show/history, reviews tradeoffs, requests alternatives, and approves plan changes. |
| Stage manager | Owns cue waivers, final schedule selection, and export; cannot waive without reason. |
| Coverage lead | Defines camera/graphics/audio requirements and resolves uncovered resources. |
| Gemini/ADK service | Queries allowlisted ClickHouse MCP reads and explains bottlenecks/proposals; cannot execute arbitrary SQL or mutate plan. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Import cues, dependencies, durations/deadlines/timezone, required coverage, crew/room constraints, and change versions.
- Validate DAG, IDs, time windows, media/resource coverage, and explicit human waivers.
- Store/query synthetic historical cue execution samples and aggregate quantiles in ClickHouse via official MCP.
- Expose sample count/cohort/quantile/window/fallback and no-history uncertainty for every estimate.
- Compute FEASIBLE/OPTIMAL/INFEASIBLE/UNKNOWN alternatives with a deterministic optimizer and coverage reasons.
- Compare tradeoffs, bind approval to exact cue graph/data snapshot/export target, and read back CSV/PDF plan.

### 1.4 Explicit non-goals

- No live-show switching/control, autonomous cue cut/waiver, arbitrary SQL, or ClickHouse writes by the agent.
- No numeric confidence from empty history or model-generated totals/durations.
- No INFEASIBLE/UNKNOWN described as valid or OPTIMAL without proof.
- No real event/crew data required in the public demo.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Use one synthetic awards-event run-of-show with 20 cues, 4 cameras, graphics/audio roles, Europe/Amsterdam timezone, 1-second scheduling granularity, and 200 historical event samples.
- Demo history lives in a local real ClickHouse cluster accessed through `mcp-clickhouse`; recorded MCP fixtures are fallback test evidence, not integrated proof.
- Duration estimate uses p75 for planning when same cue-type/venue cohort n≥8; otherwise reviewed static fallback is labeled `FALLBACK`, and with neither returns UNKNOWN.
- CP-SAT uses fixed seed 0/one worker/10-second limit; only stage manager can waive coverage with reason, and waived items remain in export.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Producer imports run-of-show/cue DAG/coverage and corrects invalid cycles, IDs, timezones, or resources before history analysis.
2. The application builds allowlisted parameterized ClickHouse MCP queries for approved cohorts and stores tool/SQL/row/latency/result identity.
3. The estimate service calculates p75/fallback/unknown with sample/cohort/window provenance and freezes a data snapshot.
4. CP-SAT evaluates cue timing/dependencies/resources/coverage and returns candidate status/objective/bound/tradeoffs.
5. Gemini explains bottlenecks using only persisted estimates/solver facts and proposes option IDs, never numeric values or arbitrary queries.
6. Producer compares protected/deferred/cut cue options and uncovered/waived coverage; stage manager records any waiver.
7. Approval binds exact cue graph, estimates/data snapshot, constraint version, selected option, and local export target.
8. CSV/PDF export/read-back includes all cues, coverage/waivers, estimates, tradeoffs, and NOT_ASSESSED uncertainty.

### 2.2 Lifecycle and transition authority

```text
RUN_IMPORT → GRAPH_AND_COVERAGE_VALIDATION → CLICKHOUSE_HISTORY_QUERY → ESTIMATE_PROVENANCE → OPTIMIZER → (FEASIBLE | OPTIMAL | INFEASIBLE | UNKNOWN) → PRODUCER_REVIEW → STAGE_MANAGER_APPROVAL → PLAN_EXPORTED; changed graph/history/rules/target → STALE_APPROVAL
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

1. Import cues, dependencies, durations/deadlines/timezone, required coverage, crew/room constraints, and change versions.
2. Validate DAG, IDs, time windows, media/resource coverage, and explicit human waivers.
3. Store/query synthetic historical cue execution samples and aggregate quantiles in ClickHouse via official MCP.
4. Expose sample count/cohort/quantile/window/fallback and no-history uncertainty for every estimate.
5. Compute FEASIBLE/OPTIMAL/INFEASIBLE/UNKNOWN alternatives with a deterministic optimizer and coverage reasons.
6. Compare tradeoffs, bind approval to exact cue graph/data snapshot/export target, and read back CSV/PDF plan.

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
| RunOfShow / Cue | `run_id`, `event_type`, `timezone`, `version`; cue `id`, `kind`, `planned_duration`, `dependencies`, `earliest/latest`, `protected`, `state` | Unique IDs; DAG acyclic; valid durations/windows; deleted cues create new version, not silent history removal. |
| CoverageRequirement / Waiver | `cue_id`, `kind`, `resource_role`, `required_count`, `waived_by`, `reason`, `version` | Every requirement covered or explicit current human waiver; model cannot waive. |
| CueExecutionSample | `event_id`, `cue_type`, `venue_cohort`, `start/end`, `actual_duration_ms`, `dropped`, `resource_ids`, `ingested_at` | Append-only synthetic history; UTC timestamps; valid durations/outliers labeled, not silently removed. |
| EstimateSnapshot | `cue_id`, `cohort`, `n`, `quantile`, `value_ms`, `data_window`, `fallback`, `clickhouse_result_id`, `snapshot_hash` | n<8 requires reviewed fallback or UNKNOWN; all figures sourced to ClickHouse result or static rule. |
| ScheduleCandidate / CueAssignment | `candidate_id`, `run_version`, `estimate_snapshot`, `status`, `objective`, `bound`; assignment `cue`, `start/end`, `resources`, `change_type` | Hard constraints independently validated; OPTIMAL only proof; totals code-computed. |
| PlanApproval / Export | `candidate_hash`, `cue_graph_hash`, `data_snapshot`, `constraint_version`, `target`, `approved_by`; export `sha256`, `readback` | Any input/target change invalidates; local CSV/PDF only, no show-control adapter. |
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
| Agent | Google ADK with Gemini on Vertex AI; a scripted ADK-compatible model adapter for offline tests | Pin the actually installed SDK; inspect its signatures. No invented hook/interrupt APIs. |
| Frontend | Node 22, React, TypeScript, Vite, React Router, TanStack Query | Use pnpm lockfile; server state remains query cache, forms use accessible controlled components. |
| Styling | CSS custom-property tokens + CSS Modules; system font stack | No remote font dependency. Charts require text/table equivalents and accessible names. |
| Testing | pytest, Hypothesis, Vitest, Testing Library, Playwright, axe-core, Ruff, mypy | Zero collected tests or collection errors fail CI; coverage alone is not correctness. |
| Local services | Makefile + optional Docker Compose | Clean offline setup uses committed fixtures and sandbox adapters; cloud credentials are never required for `make verify`. |

```text
runofshow/
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

Official `mcp-clickhouse` queries an actual local or isolated ClickHouse cluster for integrated history evidence. Google ADK/Gemini explains results. Direct agent SQL/static JSON does not count; model has no ClickHouse write capability.

For cinema projects, offline completion and integrated completion are separate statuses: the sandbox proves product behavior, while only the live-smoke evidence can prove the required partner path.

Background processing uses durable jobs with bounded exponential backoff and jitter, a maximum attempt count, lease expiry, and dead-letter visibility. Only idempotent read/analysis jobs retry automatically. External effects with unknown outcomes enter `RECONCILIATION_REQUIRED`; never blind-retry them. The API returns `202` with a job URI for work exceeding the normal request budget.

### 5.4 HTTP API contract

The paths below are the minimum product API. Generate the final schema from FastAPI and generate the TypeScript client. Request bodies use explicit typed fields; examples and all error variants belong in OpenAPI.

| Method and path | Actor | Behavior |
| --- | --- | --- |
| POST `/api/v1/runs` / POST `/api/v1/runs/{id}/cues` | Producer | Create/import versioned cue graph and validate IDs/DAG/timezone/durations. |
| PUT `/api/v1/runs/{id}/coverage` / POST `/api/v1/coverage/{id}/waiver` | Coverage lead/Stage manager | Define requirements or record exact current waiver with reason. |
| POST `/api/v1/history/samples` | History ingest worker | Batch import validated synthetic execution samples to ClickHouse through application, not agent. |
| POST `/api/v1/runs/{id}/estimates` | Producer | Execute allowlisted ClickHouse MCP history queries and freeze estimate snapshot. |
| POST `/api/v1/runs/{id}/candidates` | Producer | Run deterministic optimizer on exact graph/estimates/constraints. |
| GET `/api/v1/candidates/{id}` / `/compare` | Producer/Stage manager | Read status/assignments/coverage/tradeoffs/estimate provenance and alternatives. |
| POST `/api/v1/candidates/{id}/approval` | Stage manager | Approve exact selected option/graph/data/target digest or reject. |
| POST `/api/v1/candidates/{id}/exports` | Stage manager | Generate/read back CSV/PDF with all cues, waivers, gaps, estimates, and audit hash. |
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
| clickhouse_query_cue_durations | MCP read | Parameterized approved cohort/query template, row/time caps, read-only account; records sanitized SQL/tool/call ID. |
| clickhouse_query_execution_outcomes | MCP read | Allowlisted dropped/delay/resource aggregates; no arbitrary SQL or write function. |
| get_schedule_candidate | read | Returns deterministic status/assignments/objective/bound/coverage/tradeoffs and estimate IDs. |
| propose_recovery_explanation | proposal | Explains existing candidate/constraint IDs; cannot create times, waive, publish, or mutate plan. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

ClickHouse stores samples in `cue_execution_samples(event_id UUID, cue_type String, venue_cohort String, start_utc DateTime64(3), end_utc DateTime64(3), duration_ms UInt64, dropped Bool, resource_ids Array(String), ingested_at DateTime64(3))` and an application-owned materialized view aggregates count/quantiles by cue_type/venue/month. Agent access is read-only through named MCP query templates with `cue_type`, cohort, and bounded date parameters; result row count/latency/query/call IDs persist.

For each cue, use nearest-rank p75 from n≥8 matching non-dropped samples; report dropped rate separately. Otherwise use the reviewed static fallback labeled FALLBACK; absent both yields UNKNOWN and blocks numeric optimization unless the producer supplies a reviewed duration. CP-SAT enforces dependencies, windows, protected cues, exclusive crew/room/camera/graphics/audio coverage, and deadlines. Objective lexicographically minimizes unprotected cuts, deadline slack violation (hard rules remain hard), reorder distance, and overtime exposure. A naive validator rechecks every candidate.

| Policy area | Normative rule |
| --- | --- |
| Coverage completeness | Each requirement is assigned, explicitly waived by stage manager with reason, or listed uncovered; agent cannot invent/waive it. |
| Estimate provenance | Every duration names ClickHouse cohort/n/quantile/window/result or reviewed fallback; empty/out-of-distribution history is uncertain. |
| Solver/source honesty | Model supplies no costs/times; code recomputes from snapshot/rules and labels solver status exactly. |
| No show control | Only local approved export; no live switcher/cue endpoint exists, and ClickHouse writes are application-only ingestion. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** A live-production planning board with deep indigo, cyan evidence accents, cue timelines backed by tables, and recovery tradeoffs presented without the drama of a switcher interface. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #3556a8; --color-accent-ink: #ffffff;
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
| /runs | Runs of show | Event/version, validation/coverage state, history snapshot, candidates, and approval/export status. |
| /runs/{id}/cues | Cue graph and coverage | DAG/list/timeline alternatives, dependencies, durations/deadlines, resources, and waiver state. |
| /runs/{id}/history | ClickHouse history | Cohorts/n/p75/data window/dropped rates, MCP query identity, fallback/unknown cues, and snapshot action. |
| /candidates/{id} | Recovery candidate | Cue timing/change type, coverage, solver status/objective/bound, constraint traces, and tradeoffs. |
| /candidates/compare | Option comparison | Original vs alternatives, protected/deferred/cut counts, totals with source, and uncertainty/gaps. |
| /candidates/{id}/approve | Producer approval | Exact graph/data/rules/target hashes, waivers/gaps, stale diff, and stage-manager decision. |
| /exports/{id} | Plan export | CSV/PDF preview/read-back, all cues/coverage/waivers/estimates, and no-live-control label. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **CueTimeline:** zoom/pan plus semantic cue table and keyboard reorder proposal controls; actual changes occur only through solver/new version.
- **EstimateBadge:** p75/FALLBACK/UNKNOWN with n/cohort/window and ClickHouse result drawer; no naked confidence percentage.
- **CoverageMatrix:** cue×resource requirement state with Assigned/Waived/Uncovered text and waiver reason/source.
- **TradeoffPanel:** original/candidate code-computed deltas, solver status, affected cues, and source snapshot; no model-authored numbers.
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
- **Privacy:** Synthetic execution history remains in local ClickHouse for one year; real history requires production rights and minimization. Plan/audit snapshots persist 90 days. MCP logs store sanitized SQL/IDs/row counts, not comments or private crew data.
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

Commit 200 synthetic historical event samples and 40 planning scenarios with dropped/slow cues, resource conflicts, camera/graphics/audio gaps, DAG cycles, no-history/out-of-distribution cohorts, reordered controls, fallback-only estimates, timezone/deadline boundaries, injected cue comments/query rows, and stale approvals. Include hand/naive feasibility labels and ClickHouse DDL/seed manifest.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Import/coverage/solver | 100% invalid graphs held; zero uncovered requirements without explicit waiver; naive validator agrees on every candidate and status label. |
| Estimate accuracy/provenance | 100% estimates expose n/cohort/quantile/window/source; n<8 never claims numeric confidence; report MAE vs held-out durations by cohort. |
| ClickHouse runtime | Integrated real MCP query/call/SQL/row/latency evidence; malformed/empty results remain distinct and no arbitrary/write SQL succeeds. |
| Plan quality | Report feasibility, protected-cue retention, deadline/reorder/overtime objectives, and human edits against original/simple baseline. |
| Authority/security | Zero injected arbitrary queries/waivers/publishes; 100% stale graph/data/target approvals refused and export/read-back exact. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Import a run with a coverage gap and invalid dependency control; correct them before solving.
2. Query local ClickHouse through MCP and inspect p75/n/cohort plus a no-history fallback/UNKNOWN cue.
3. Generate original and recovery candidates and inspect naive validation, solver status, coverage, and quantified tradeoffs.
4. Attempt a cue-comment injection asking for arbitrary SQL/waiver; the agent remains within read templates and cannot change plan.
5. Stage manager records a waiver/approves exact graph/data/target; a cue edit invalidates the old approval.
6. Reapprove/export/read back CSV/PDF with gaps/waivers/estimate provenance and no show-control effect.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Cue DAG/coverage schemas, naive validator, optimizer, and synthetic planning fixtures.
2. ClickHouse DDL/seed/materialized views, MCP read templates, estimate snapshots, and runtime/fault tests.
3. ADK explanation/proposal path, query allowlists, injection containment, and candidate comparison UI.
4. Waiver/approval/version invalidation, CSV/PDF export/read-back, audit, and restart tests.
5. 40-scenario eval, accessibility/performance, real MCP evidence, deployment/rollback, and demo.

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
| ROS-01 | schema validates cue IDs, dependencies, durations, time zones, and media coverage; invalid graphs are held for producer correction. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| ROS-02 | each cue requirement is satisfied, explicitly waived by a human, or listed as uncovered; agent cannot invent required coverage. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| ROS-03 | deterministic engine returns `FEASIBLE`, `OPTIMAL`, `INFEASIBLE`, or `UNKNOWN`; only proven states are labeled as such. | Unit/property tests with hand-calculated and boundary fixtures, plus API round-trip tests; failures must be fail-first and reproducible. | Core |
| ROS-04 | ClickHouse-derived duration estimates expose population and quantile; insufficient data prevents a numeric confidence claim. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| ROS-05 | model explanation never supplies cost/time figures; code recomputes totals from cited rows and rule versions. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| ROS-06 | a schedule change is bound to exact cue graph, data snapshot, and export target; any change invalidates approval. | State-machine and API negative tests for wrong actor, stale digest/version, replay, and concurrent requests; assert zero external side effects. | Core |
| ROS-07 | tests and demo verify actual ClickHouse MCP query execution and result parsing; malformed/empty result sets remain distinct. | `make live-smoke` against the required isolated partner/runtime plus offline contract tests; retain sanitized provider/MCP/hosting evidence and never substitute fixtures. | Integration |
| ROS-08 | cue names/comments and query results cannot make the agent run arbitrary SQL or mutate a plan. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| ROS-09 | synthetic past events include dropped cues, slow segments, resource conflicts, no-history cohorts, and reordering controls. Report plan feasibility and historical estimate error. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| ROS-10 | show original coverage gaps, a solver-produced alternative, the quantified tradeoff with provenance, and a producer-approved export; never control a live show. | Unit/property tests with hand-calculated and boundary fixtures, plus API round-trip tests; failures must be fail-first and reproducible. | Core |

### 13.3 Additional global gates

| Gate | Pass condition |
| --- | --- |
| G-01 Traceability | All 10 source criteria plus FR-C01…C06 map to implementation and retained evidence; no orphan or unverified criterion. |
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

**Score rule:** award 0 / 50% / 100% of each category only from retained evidence (no partial fractions otherwise). Full completion requires **≥90/100, no category below 80% of its weight, every hard gate below, and every applicable §13 criterion passed**. A rubric score cannot compensate for a hard-gate failure. For cinema projects, report both `offline score` and `integrated score`; full completion requires the required integration criteria and the actual partner runtime described in §5.3.

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

- Confirm first event type, cue/coverage/waiver authority, historical data rights, and production export conventions.
- Configure isolated ClickHouse/MCP read roles, query limits, retention, and application-only ingestion.
- Rehearse manual show-recovery fallback; the product remains a planning aid and never connects to a live switcher.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for RunOfShow.**
