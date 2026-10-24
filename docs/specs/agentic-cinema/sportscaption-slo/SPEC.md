# SportsCaption SLO — implementation-ready specification

**Project ID:** `sportscaption-slo`<br>
**Track / family:** Agentic Cinema / Grafana alternate 02<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [05-sportscaption-slo.md](../05-sportscaption-slo.md) (historical context only)<br>
**Primary audience:** A small live-sports streaming operator and accessibility incident commander

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

A stream can appear healthy while captions lag, alternate audio is silent, or player controls fail for a device/locale cohort. Response needs measurement, correlation, mitigation approval, and post-fix regression checks.

**Product promise:** collect synthetic probe/delivery evidence, evaluate versioned accessibility-track SLOs, correlate incidents through Grafana MCP, and close only after operator-approved mitigation and affected-plus-control probes pass.

**Tagline:** Treat caption and alternate-audio reliability as an owned service objective.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Incident commander | Owns mitigation approval, incident state, annotation, and closure after regression evidence. |
| Streaming operator | Runs probes, investigates cohorts, and executes only sandbox mitigation commands. |
| Accessibility reviewer | Defines probe/SLO semantics and reviews results; no disability inference or certification claim. |
| Gemini/ADK service | Correlates scoped Grafana evidence and proposes hypotheses/typed mitigation; cannot mutate tracks/alerts or close incidents. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Model one synthetic live event, 2 locales, 2 device classes, player builds, stream versions, and probe cohorts.
- Measure caption delay/readability, alternate-audio presence, track discoverability, and scripted keyboard operability.
- Evaluate versioned objectives/windows/budgets/thresholds with missing probes = not measured.
- Query Grafana metrics/logs/traces/alerts/dashboards via MCP and require valid evidence before analysis completes.
- Propose typed mitigation and approval-bound incident annotation; no automatic track switch or alert suppression.
- Re-run affected and unaffected control cohorts after mitigation; any regression keeps incident open.

### 1.4 Explicit non-goals

- No accessibility certification, disability inference, viewer profiling, or claim that SLO attainment equals full accessibility.
- No direct Prometheus/Loki/Tempo queries as a substitute for required Grafana MCP.
- No autonomous production mitigation, alert suppression, incident closure, or fabricated missing measurements.
- No real sports footage or viewer-identifying telemetry in the demo.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Demo event `SYNTH_MATCH_01` has English/Dutch captions, audio description, desktop/mobile synthetic player probes, 30-second probe cadence, and 30-minute rolling SLO windows.
- Engineering objectives: 99% valid caption probes with p95 delay ≤2.0s and readability parser pass; 99% alternate-audio probes without absence/silence >3s; 100% scripted track-discovery/keyboard checks. These are test objectives, not certification.
- Mitigation is sandbox `reload_caption_manifest` or `restart_alt_audio_probe`, exact event/cohort/config hash bound; post-change wait 60 seconds then affected and control probes.
- Offline uses recorded MCP evidence; integrated lane requires actual Grafana MCP read evidence + approved annotation and real ADK/Gemini.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Accessibility reviewer activates a versioned SLO/probe configuration for the synthetic event and cohorts.
2. Probe workers emit typed results with locale/device/player/build/stream/time/evidence; missing dimensions remain not measured.
3. The deterministic SLO engine computes delay/readability/audio/player results and error budget over explicit windows.
4. A violation opens an incident and the ADK agent gathers required Grafana MCP evidence or stops incomplete.
5. Gemini proposes correlated hypotheses with supporting/disconfirming evidence and a typed sandbox mitigation plan.
6. Incident commander previews exact event/cohort/action/config impact and approves or rejects; annotation is separately approved.
7. The sandbox adapter executes idempotently/read-back; scheduler runs affected plus adjacent control probes.
8. If all required fresh probes pass and no control regresses, commander closes with evidence; otherwise incident remains open.

### 2.2 Lifecycle and transition authority

```text
EVENT_CONFIGURED → PROBES_RUNNING → SLO_EVALUATION → (HEALTHY | NOT_MEASURED | VIOLATION) → INCIDENT_OPEN → MCP_CORRELATION → MITIGATION_PROPOSED → OPERATOR_APPROVAL → SANDBOX_MITIGATION → AFFECTED_AND_CONTROL_RECHECK → (CLOSED | REGRESSION_OPEN); partial evidence → INCOMPLETE_ANALYSIS
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

1. Model one synthetic live event, 2 locales, 2 device classes, player builds, stream versions, and probe cohorts.
2. Measure caption delay/readability, alternate-audio presence, track discoverability, and scripted keyboard operability.
3. Evaluate versioned objectives/windows/budgets/thresholds with missing probes = not measured.
4. Query Grafana metrics/logs/traces/alerts/dashboards via MCP and require valid evidence before analysis completes.
5. Propose typed mitigation and approval-bound incident annotation; no automatic track switch or alert suppression.
6. Re-run affected and unaffected control cohorts after mitigation; any regression keeps incident open.

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
| LiveEvent / Cohort | `event_id`, `start/end`, `stream_version`; cohort `locale`, `device_class`, `player_build`, `track_ids` | Every result has full cohort/version dimensions; unknown dimensions not measured. |
| ProbeResult | `probe_id`, `event_id`, `cohort_id`, `kind`, `probe_time`, `measurements`, `evidence_hash`, `status` | Typed caption/audio/player values; missing/error≠pass; original evidence immutable. |
| SLODefinition / SLOWindow | `slo_id`, `version`, `metric`, `threshold`, `window`, `budget`, `aggregation`; window `valid/total`, `value`, `state` | Versioned formula/denominator; exact time boundaries; missing probes explicitly counted. |
| GrafanaEvidence / Hypothesis | `mcp_tool`, `query`, `result_id`, `time_range`, `lane`; hypothesis `claim`, `support_ids`, `disconfirm_ids` | Required source data before completion; hypotheses never mutate metrics. |
| Incident / MitigationPlan | `incident_id`, `cohort_ids`, `state`, `owner`; plan `action`, `config_hash`, `expected_effect`, `rollback` | Typed allowlisted sandbox actions; exact approval and idempotency; no alert suppression action. |
| Recheck / IncidentAnnotation | `incident_id`, `affected_results`, `control_results`, `freshness`, `outcome`; annotation `dashboard`, `text_hash`, `provider_id` | Closure requires affected+control pass and commander decision; regression preserves open state. |
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
sportscaption-slo/
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

Grafana MCP is required at integrated runtime for metrics/logs/traces/alerts/dashboard search and approved annotation. Google ADK/Gemini is the only AI path. Direct datasource queries or screenshots do not count as partner proof.

For cinema projects, offline completion and integrated completion are separate statuses: the sandbox proves product behavior, while only the live-smoke evidence can prove the required partner path.

Background processing uses durable jobs with bounded exponential backoff and jitter, a maximum attempt count, lease expiry, and dead-letter visibility. Only idempotent read/analysis jobs retry automatically. External effects with unknown outcomes enter `RECONCILIATION_REQUIRED`; never blind-retry them. The API returns `202` with a job URI for work exceeding the normal request budget.

### 5.4 HTTP API contract

The paths below are the minimum product API. Generate the final schema from FastAPI and generate the TypeScript client. Request bodies use explicit typed fields; examples and all error variants belong in OpenAPI.

| Method and path | Actor | Behavior |
| --- | --- | --- |
| POST `/api/v1/events` / PUT `/api/v1/events/{id}/slos` | Operator/Reviewer | Configure synthetic event/cohorts and versioned SLO definitions. |
| POST `/api/v1/events/{id}/probe-results` | Probe worker | Ingest signed/idempotent typed measurements and evidence hashes. |
| GET `/api/v1/events/{id}/slo` | Operator | Return windowed values, budgets, cohort states, not-measured counts, and formula versions. |
| POST `/api/v1/incidents/{id}/correlate` | Operator | Run required Grafana MCP correlation + ADK hypotheses as a durable job. |
| GET `/api/v1/incidents/{id}` | Operator/Commander | Read cohort evidence, hypotheses, mitigation/recheck state, and trace. |
| POST `/api/v1/incidents/{id}/mitigation-approval` | Incident commander | Approve exact typed sandbox plan/config/rollback or reject. |
| POST `/api/v1/incidents/{id}/mitigations` / POST `/api/v1/incidents/{id}/recheck` | Operator application command | Execute/read back approved sandbox action and schedule affected+control probes. |
| POST `/api/v1/incidents/{id}/close` / `/annotations` | Incident commander | Close only with fresh passing recheck; separately approve/write/read back MCP annotation. |
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
| grafana_query_accessibility_metrics | MCP read | Allowlisted event/cohort/SLO queries with time/row caps and source identity. |
| grafana_search_player_logs | MCP read | Bounded log query; captions/log content treated as untrusted data. |
| grafana_get_traces_alerts_dashboards | MCP read | Scoped correlation evidence; missing required call blocks analysis completion. |
| propose_incident_hypothesis | proposal | Cited cause alternatives and typed mitigation option; no metrics/effects authority. |
| execute_mitigation | application only | Never exposed to agent; exact approved action/config, sandbox adapter, read-back, and recheck. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

Caption delay samples compare expected cue timestamp to observed rendered timestamp; each valid sample has nonnegative/declared signed delay in milliseconds. Aggregate p95 using the documented nearest-rank method over valid samples in `[window_start, window_end)`, report valid/total, and mark NOT_MEASURED below the configured minimum 10 valid probes. Readability is a deterministic fixture parser result for caption duration/line length, not a model judgment. Alternate-audio absence/silence uses probe measured intervals >3,000 ms; player checks are scripted boolean assertions with evidence.

Error budget is `1 − good_valid_probe_windows/total_required_windows`, with missing windows shown separately and never counted good. Correlation joins event/cohort/track/time, not viewer identity. Post-mitigation closure requires at least 2 consecutive fresh passing affected probes and 1 fresh passing probe for every declared control cohort; any regression/missing required recheck keeps open.

| Policy area | Normative rule |
| --- | --- |
| Measurement honesty | Every value has locale/device/player/build/stream/time/evidence; missing probe/dimension is not measured, never healthy. |
| SLO semantics | Objective/window/budget/threshold/version and denominator visible; no “certified accessible” wording anywhere. |
| Repair authority | Only commander-approved typed sandbox mitigation and annotation; no automatic track switch, alert suppression, or closure. |
| Regression gate | Affected and adjacent control cohorts rerun; fresh evidence and human closure required; any regression reopens/holds incident. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** A live reliability console with signal-orange highlights, cohort matrices paired with tables, clear SLO formulas, and accessible incident controls that never rely on color or real-time animation alone. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #9a4b1f; --color-accent-ink: #ffffff;
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
| /events/{id}/overview | Accessibility SLO overview | Event/stream state, SLO cards with formulas/budgets, cohort status, not-measured counts, and last probe. |
| /events/{id}/cohorts | Cohort matrix | Locale×device results, delay/audio/player metrics, evidence age, and accessible table alternative. |
| /incidents | Accessibility incidents | Open/regression/waiting-recheck states, cohort/owner/SLO, and acknowledged/approval state. |
| /incidents/{id}/evidence | Incident correlation | Grafana MCP metrics/logs/traces, supporting/disconfirming hypotheses, and missing-evidence blockers. |
| /incidents/{id}/mitigation | Mitigation review | Exact typed action/config/cohorts/rollback, risk, commander approval, and sandbox read-back. |
| /incidents/{id}/recheck | Regression verification | Affected/control probe results, freshness/consecutive-pass counts, regression reasons, and closure gate. |
| /admin/probes | Probe and SLO configuration | Versioned objectives/windows/thresholds, synthetic probe health, integration lane, and accessible test evidence. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **SLOCard:** current value, target, window, valid/total denominator, budget, and trend with table equivalent; no certification language.
- **CohortHeatmap:** optional visual grid with full semantic table, text labels, keyboard cell navigation, and no color-only status.
- **LiveUpdateRegion:** batches announcements, pause/resume updates, exact last-updated time, and reduced-motion behavior; no constant screen-reader chatter.
- **MitigationDiff:** current/proposed config and affected/control cohorts with rollback and exact approval digest.
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
- **Privacy:** Synthetic probes and Grafana extracts persist 30 days; caption/log text is redacted to IDs/time ranges and expires in 7 days. No viewer identity, disability, raw IP, or account data is collected. Incident/audit evidence remains 90 days.
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

Commit deterministic synthetic probe streams for 2 locales×2 devices and 40 incident scenarios: caption drift/lag, unreadable timing, alternate-audio silence/absence, track-menu trap, keyboard failure, missing/stale/partial telemetry, CDN confounders, good controls, mitigation regressions, injected captions/logs, and MCP outage. Include expected SLO hand calculations and player-probe transcripts.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| SLO arithmetic | 100% hand-calculated delay/window/budget/denominator/threshold results; missing probes never counted healthy. |
| Detection/regression | 100% deterministic drift/silence/absence/menu-trap cases detected; all affected/control regression gates enforced; false alarms reported. |
| Correlation quality | Report diagnosis recall/false alarms by locale/device/failure dimension and every miss; hypotheses include alternatives/disconfirming evidence. |
| Integration/authority | Integrated real MCP query + approved annotation/read-back; zero auto-mitigation/closure or injected log/tool effects. |
| Console accessibility | Zero serious/critical axe; complete keyboard/screen-reader/caption/zoom/reduced-motion incident journey with live updates controlled. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Open the synthetic event and explain one SLO formula/window/denominator and a not-measured cohort.
2. Inject caption lag for one device cohort and inspect the incident plus Grafana MCP evidence.
3. Review Gemini hypotheses with supporting/disconfirming data and reject an unsupported causal claim.
4. Commander approves exact sandbox mitigation and annotation; unapproved track/alert changes are unavailable/denied.
5. Run affected and adjacent control probes; show a synthetic regression keeps the incident open in a control case.
6. On the clean path, close with fresh passing evidence and inspect the accessible audit/annotation trace.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Probe/cohort/event schemas, deterministic SLO engine, synthetic stream generator, and hand calculations.
2. Grafana MCP adapter, recorded/live evidence lanes, required-source gate, and fault/injection tests.
3. ADK correlation/hypotheses, typed mitigation policy, incident UI, and approval controls.
4. Sandbox mitigation/read-back, affected/control rechecks, closure/annotation, and restart recovery.
5. 40-scenario eval, console accessibility/live-region testing, performance, integrated live-smoke, runbook, and demo.

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
| SCS-01 | every result has locale, device, player build, stream version, probe time, and evidence; missing probe is `not measured`. | Schema and integration tests resolve every reference to immutable source content; mutate/delete a reference and verify a visible hold, never a pass. | Core |
| SCS-02 | objective, window, budget, and threshold are versioned and shown; never display “certified accessible” from a model judgment. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SCS-03 | correlate by event/time/track/device and show evidence for each hypothesis; model cannot mutate the underlying metric. | Schema and integration tests resolve every reference to immutable source content; mutate/delete a reference and verify a visible hold, never a pass. | Core |
| SCS-04 | live Grafana MCP query plus an approved safe annotation appear in the trace; missing MCP capability prevents a green completion state. | `make live-smoke` against the required isolated partner/runtime plus offline contract tests; retain sanitized provider/MCP/hosting evidence and never substitute fixtures. | Integration |
| SCS-05 | proposed mitigation is a typed plan; no auto-switching tracks, suppressing alerts, or closing incident without operator permission and post-change probes. | API authorization/privacy integration tests with two tenants/actors and canary values; inspect model prompts, responses, exports, caches, and logs. | Core |
| SCS-06 | after a fix, run both the affected slice and unaffected control locales/devices; any regression keeps incident open. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SCS-07 | the console itself meets keyboard, screen-reader, contrast, captions, and zoom checks; status is never communicated by color alone. | Playwright keyboard/mobile journeys, axe-core, and documented NVDA/VoiceOver plus 200%/400% zoom checks; retain screenshots and manual notes. | Core |
| SCS-08 | prompt injection in log lines/caption text cannot change tools or policy; Grafana errors and partial results fail closed. | Fail-first security suite inspecting actual tool requests, state transitions, logs, and outbound payloads; include a benign positive control. | Core |
| SCS-09 | deterministic probes test drift, silence, absent track, player menu trap, and good controls. Report recall/false alarms by dimension, and all misses. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| SCS-10 | show a synthetic caption lag across one device cohort, inspect Grafana evidence, approve a simulated remediation, verify adjacent control cohort, then close with evidence. | `make live-smoke` in an isolated account plus contract tests; retain sanitized provider/MCP request IDs and clearly separate offline fixture evidence. | Core |

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

- Have an accessibility specialist/streaming operator approve probe meaning, SLO thresholds, device/locale coverage, and non-certification copy.
- Configure probe ownership, on-call routing, MCP auth/scopes, production mitigation approval, and rollback.
- Test with actual player devices and Deaf/hard-of-hearing reviewers before any accessibility or operational-impact claim.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for SportsCaption SLO.**
