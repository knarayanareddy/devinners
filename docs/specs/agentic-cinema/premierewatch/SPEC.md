# PremiereWatch — implementation-ready specification

**Project ID:** `premierewatch`<br>
**Track / family:** Agentic Cinema / Grafana alternate 01<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [04-premierewatch.md](../04-premierewatch.md) (historical context only)<br>
**Primary audience:** Release operations and incident owners coordinating localized media packages for a festival premiere

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

A localized title package can exist while captions, audio, rights records, versions, validation, or delivery acknowledgements are missing or stale. Readiness needs correlated evidence and a human owner.

**Product promise:** correlate package/check/telemetry/delivery evidence through Grafana MCP, compute a deterministic required-artifact matrix, open owned incidents for blockers, and require release-manager approval for readiness and annotations.

**Tagline:** Release readiness backed by live operational evidence, not a false-green dashboard.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Release manager | Owns package requirements, readiness decision, final greenlight, and annotation approval. |
| Release operator | Investigates evidence, reruns checks, and manages incidents; cannot self-approve final release. |
| Vendor viewer | Sees only assigned package/delivery acknowledgement state, no unrelated titles or credentials. |
| Gemini/ADK service | Queries scoped Grafana MCP evidence and drafts incident hypotheses; cannot bypass artifacts or release automatically. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Model one title, 3 territories, 2 platforms, versioned package/artifact requirements, and deadline.
- Ingest synthetic artifact metadata, caption/audio QC, validation events, and delivery acknowledgements.
- Query Grafana metrics/logs/traces/alerts/dashboards through the accepted MCP runtime and persist query/result identity.
- Compute readiness/blockers/staleness deterministically and invalidate readiness on artifact/version changes.
- Create human-owned incident case files with cited evidence, hypotheses, timeline, and rerun state.
- Create one approval-bound Grafana annotation through allowlisted MCP and read it back; no auto-release.

### 1.4 Explicit non-goals

- No video rewrite, rights clearance, automatic title release, or claim of market/legal compliance.
- No direct Prometheus/Loki/Grafana API substitute for required MCP partner evidence.
- No dashboard screenshot as proof of live MCP use or stale telemetry as a pass.
- No unbounded dashboard/query mutation or credentials in browser/agent content.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Demo scope is `Festival Title`, territories `NL/DE/FR`, platforms `FESTIVAL_VOD` and `FESTIVAL_DCP`, six package combinations, and synthetic original media manifests.
- Evidence TTL is 10 minutes for delivery/upload metrics and 30 minutes for QC/acknowledgement; stale/missing evidence yields UNKNOWN and blocks ready.
- Grafana read tools are default; only `create_incident_annotation` is write-allowlisted, limited to the demo dashboard/UID and 5 writes/hour.
- Offline uses a labeled MCP fixture server with recorded responses; integrated completion requires real accepted Grafana Cloud MCP query + annotation/read-back and actual Gemini/ADK.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Release manager loads versioned requirements for six title/territory/platform packages and deadline.
2. Adapters ingest immutable artifact/check/acknowledgement records and correlate IDs without trusting package metadata as instructions.
3. The ADK investigator calls bounded Grafana MCP read tools; application stores sanitized tool/query/result IDs and detects partial/missing evidence.
4. The readiness engine evaluates required artifacts, versions, QC, acknowledgement, deadlines, and TTL; it never infers green from job success.
5. Operator opens a blocker case with exact artifact/check/source/time and Gemini hypothesis separated from deterministic facts.
6. A fixture fix generates a new artifact/version and invalidates prior readiness; recheck gathers fresh evidence.
7. Release manager approves exact ready snapshot or holds it; operator separately previews/approves a scoped Grafana annotation.
8. The MCP adapter writes once/idempotently, reads back annotation, and displays live vs simulated evidence and trace.

### 2.2 Lifecycle and transition authority

```text
PACKAGE_DEFINED → ARTIFACTS_INGESTED → GRAFANA_EVIDENCE_COLLECTED → READINESS_COMPUTED → (BLOCKED | UNKNOWN | READY_CANDIDATE) → INCIDENT_REVIEW → FIXTURE_FIX / RECHECK → RELEASE_MANAGER_APPROVAL → ANNOTATION_APPROVAL → ANNOTATED; MCP partial/outage → INCOMPLETE_RUN; any artifact change → STALE_READINESS
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

1. Model one title, 3 territories, 2 platforms, versioned package/artifact requirements, and deadline.
2. Ingest synthetic artifact metadata, caption/audio QC, validation events, and delivery acknowledgements.
3. Query Grafana metrics/logs/traces/alerts/dashboards through the accepted MCP runtime and persist query/result identity.
4. Compute readiness/blockers/staleness deterministically and invalidate readiness on artifact/version changes.
5. Create human-owned incident case files with cited evidence, hypotheses, timeline, and rerun state.
6. Create one approval-bound Grafana annotation through allowlisted MCP and read it back; no auto-release.

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
| Title / PackageRequirement | `title_id`, `territory`, `platform`, `deadline`, `required_artifacts[]`, `requirement_version` | Unique six demo combinations; required matrix versioned and human-owned. |
| Package / Artifact | `package_id`, `requirement_version`; artifact `artifact_id`, `kind`, `version`, `sha256`, `metadata`, `observed_at` | Artifact identity/hash immutable; changed version invalidates readiness; metadata untrusted. |
| ValidationCheck / DeliveryAck | `check_id`, `artifact_id`, `result`, `details`, `checked_at`; ack `vendor`, `package_version`, `acknowledged_at`, `receipt` | Required checks scoped to exact artifact; missing/failed/stale not pass. |
| GrafanaEvidence | `evidence_id`, `mcp_server`, `tool`, `query_hash`, `query_sanitized`, `result_id`, `row_count`, `time_range`, `fetched_at`, `lane` | Actual vs fixture lane explicit; partial/malformed results remain incomplete; secrets absent. |
| ReadinessSnapshot / Blocker | `package_id`, `input_hash`, `state`, `computed_at`; blocker `kind`, `artifact/check`, `evidence_ids`, `severity`, `reason` | READY candidate only all required fresh evidence; every blocker source-linked. |
| Incident / AnnotationApproval | `incident_id`, `owner`, `state`, `evidence_ids`, `hypotheses`; approval `dashboard_uid`, `time`, `text_hash`, `release_snapshot` | Human owner; annotation exact scope/content/time bound; read-back required. |
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
premierewatch/
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

Accepted Grafana Cloud MCP is load-bearing for integrated evidence and safe annotation. Google ADK/Gemini provides incident summaries. Offline MCP fixtures are explicitly simulated; direct Prometheus/Loki/Grafana API calls do not satisfy partner proof.

For cinema projects, offline completion and integrated completion are separate statuses: the sandbox proves product behavior, while only the live-smoke evidence can prove the required partner path.

Background processing uses durable jobs with bounded exponential backoff and jitter, a maximum attempt count, lease expiry, and dead-letter visibility. Only idempotent read/analysis jobs retry automatically. External effects with unknown outcomes enter `RECONCILIATION_REQUIRED`; never blind-retry them. The API returns `202` with a job URI for work exceeding the normal request budget.

### 5.4 HTTP API contract

The paths below are the minimum product API. Generate the final schema from FastAPI and generate the TypeScript client. Request bodies use explicit typed fields; examples and all error variants belong in OpenAPI.

| Method and path | Actor | Behavior |
| --- | --- | --- |
| POST `/api/v1/titles` / PUT `/api/v1/requirements/{id}` | Release manager | Create demo title and version required package matrix. |
| POST `/api/v1/packages/{id}/artifacts` / POST `/api/v1/artifacts/{id}/checks` | Operator/Ingest worker | Ingest hash/version-bound artifact, QC, validation, and delivery events. |
| POST `/api/v1/readiness-runs` | Operator | Run Grafana MCP evidence collection + deterministic matrix as durable job. |
| GET `/api/v1/readiness?title_id=` / GET `/api/v1/readiness/{id}` | Operator/Manager | Return six-cell matrix, blockers, stale/unknown sources, and evidence identity. |
| POST `/api/v1/incidents` / GET `/api/v1/incidents/{id}` | Operator | Create/open human-owned incident from blockers with evidence and hypotheses. |
| POST `/api/v1/packages/{id}/release-approval` | Release manager | Approve/reject exact fresh readiness snapshot; agent cannot call. |
| POST `/api/v1/incidents/{id}/annotation-approval` | Release manager | Approve exact dashboard/time/text annotation and rate-limited scope. |
| POST `/api/v1/incidents/{id}/annotations` | Operator application command | Recheck approval and call allowlisted MCP write/read-back; returns provider ID. |
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
| grafana_query_metrics | MCP read | Fixed metric names/labels/time range/row cap for current title; application records MCP call identity. |
| grafana_search_logs | MCP read | Allowlisted Loki query templates with tenant/title/time bounds; raw lines treated as untrusted. |
| grafana_query_traces_and_alerts | MCP read | Scoped trace/alert lookup; partial results flagged and never replaced by stale success. |
| propose_incident_brief | proposal | Summarizes deterministic blockers + cited Grafana evidence with alternative hypotheses. |
| create_incident_annotation | MCP write via application only | Not exposed to agent; exact approved dashboard/time/text, idempotency/rate limits, read-back mandatory. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

For each package, evaluate the requirement matrix in stable artifact-kind order. A requirement passes only when the exact required artifact kind/version/hash exists, all required checks pass against that hash, required delivery acknowledgement matches package version, and every required evidence item is within TTL. `BLOCKED` represents a known failed/missing requirement; `UNKNOWN` represents stale, partial, denied, or unmeasured evidence; `READY_CANDIDATE` requires no blockers/unknowns. A human release state is separate and never derived automatically.

Deadline risk is deterministic: `seconds_remaining = deadline − current_utc`, displayed with deadline timezone; no probability is invented. Changed artifact hashes or requirement versions produce a new input hash and stale prior snapshot. Grafana annotation payload is `{dashboard_uid, time_utc, text_hash, tags}` from the approved incident only; adapter read-back compares all fields.

| Policy area | Normative rule |
| --- | --- |
| MCP load-bearing path | Operational evidence used by the agent comes through accepted Grafana MCP; direct datasource APIs cannot satisfy integrated criteria. |
| No false green | Missing/stale/partial/malformed/denied evidence suppresses ready/all-clear and creates an incomplete-run trace. |
| Release authority | Only release manager transitions final readiness; agent cannot bypass required artifact, change matrix, or self-annotate. |
| Scope/rate limits | MCP credentials server-side, datasource/dashboard allowlists, row/time caps, 5 annotations/hour, model budget, and global kill switch. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** A release-operations command center with crisp violet accents, a six-cell readiness matrix, evidence-dense incident timelines, and explicit unknown/stale states that resist dashboard greenwashing. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #6741a5; --color-accent-ink: #ffffff;
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
| /titles/{id}/matrix | Release readiness matrix | Territory×platform cells, artifact state, deadline, freshness, blockers, and final human release state. |
| /packages/{id} | Package evidence | Required artifact checklist, versions/hashes, QC/acknowledgement, Grafana evidence, and stale invalidation. |
| /runs/{id} | Evidence collection run | MCP tools/query IDs/time ranges/row counts/latency/lane, partial failures, and deterministic results. |
| /incidents | Release incidents | Owner/severity/deadline/package/state, stale evidence, and assigned investigation. |
| /incidents/{id} | Incident case file | Deterministic blockers vs Gemini hypotheses, logs/metrics/traces links, timeline, fix/recheck, and next action. |
| /incidents/{id}/annotation | Annotation approval | Exact dashboard/time/text/tags, rate/cost state, manager approval, MCP write/read-back. |
| /admin/requirements | Requirements and integrations | Versioned matrix, TTLs, datasource/dashboard scopes, fixture/live labels, kill switch, and audit. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **ReadinessCell:** Ready candidate/Blocked/Unknown/Stale text+icon, artifact count, evidence age, and drill-down; never green based only on upload.
- **EvidenceRef:** MCP tool/query/result/time range/row count and copied safe link; fixture vs live badge always visible.
- **HypothesisCard:** model statement, supporting/disconfirming evidence IDs, and deterministic facts kept in a separate panel.
- **AnnotationPreview:** exact dashboard/time/text and write consequence, approval version, provider read-back, and rate-limit feedback.
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
- **Privacy:** Synthetic package metadata and MCP result extracts persist 30 days; raw log lines are minimized/redacted and expire in 7 days. Audit/annotation IDs remain 90 days. No copyrighted media is required; only original manifests and small licensed validation assets.
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

Commit 40 synthetic release runs for six packages: missing captions/audio/rights manifest, wrong version/hash, partial upload, delayed/stale acknowledgement, QC failure, deadline boundary, Grafana partial/malformed/outage/denied write, false-green job success, metadata injection, duplicate events, and fixed rechecks. Include local/recorded MCP payloads and independent readiness labels.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Readiness correctness | 100% matrix outcomes against hand-labeled fixtures; zero ready with missing/wrong/stale/unknown required evidence. |
| Evidence completeness | 100% blockers cite package/artifact/check/time/source; every agent operational claim maps to MCP evidence identity. |
| Integration/recovery | Integrated lane proves real metrics/logs/traces query + approved annotation/read-back; outages/partial results always incomplete, no stale reuse. |
| Security/authority | Zero package/log injection changes to scope/policy/credentials; zero auto-release or unapproved/over-quota annotations. |
| Evaluation | Report blocker detection, false alarms, unknown/stale rates, run latency, MCP query counts, and all missed blockers by package/requirement. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Open the six-cell matrix and show one false-green upload become Blocked because captions/QC evidence is missing.
2. Run the investigator and inspect actual or clearly labeled fixture Grafana MCP metrics/logs/traces evidence.
3. Open the incident, separate deterministic blockers from Gemini hypotheses, and inspect stale-source behavior.
4. Apply a fixture fix, show the artifact hash invalidates readiness, and recheck fresh evidence.
5. Release manager approves the exact ready snapshot and scoped annotation; an unapproved write is denied.
6. Integrated lane writes/reads back one Grafana annotation and displays provider/MCP IDs, caps, and audit.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Package/requirement/artifact matrix, deterministic readiness/TTL engine, and synthetic telemetry generator.
2. Grafana MCP read adapter with recorded fixture + isolated live config, query identity, scopes, and fault tests.
3. ADK/Gemini incident brief, deterministic blocker/provenance separation, and injection containment.
4. Readiness/incident UI, release approval, allowlisted annotation/read-back, rate limits, and audit.
5. 40-run eval, accessibility, outage/restart/performance tests, live-smoke evidence, deployment/rollback, and demo.

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
| PW-01 | live demo connects to Grafana MCP and executes at least one real query plus one safe write/annotation; dashboard screenshots alone do not count. | `make live-smoke` against the required isolated partner/runtime plus offline contract tests; retain sanitized provider/MCP/hosting evidence and never substitute fixtures. | Integration |
| PW-02 | every blocker names a title, territory, platform, artifact/check ID, time, and source; no source means `unknown`, not pass. | Schema and integration tests resolve every reference to immutable source content; mutate/delete a reference and verify a visible hold, never a pass. | Core |
| PW-03 | metrics/logs past TTL suppress green/all-clear state and create a stale-source warning. | Unit/property tests with hand-calculated and boundary fixtures, plus API round-trip tests; failures must be fail-first and reproducible. | Core |
| PW-04 | agent cannot mark release complete or bypass a required artifact; only authorized human action may publish the release state. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| PW-05 | one demo title, three territories, two platforms, and versioned package requirements are enough; one changed artifact invalidates prior readiness. | Run the seeded browser journey, retain the Playwright trace and short recording, and verify the evidence/refusal shown against API and audit state. | Core |
| PW-06 | content/metadata in an uploaded package cannot change query scopes, credentials, dashboards, or release policy. | API authorization/privacy integration tests with two tenants/actors and canary values; inspect model prompts, responses, exports, caches, and logs. | Core |
| PW-07 | Grafana MCP outage, partial query, malformed panel result, or denied write produces a visible incomplete run with trace ID; no stale result is silently reused. | `make live-smoke` in an isolated account plus contract tests; retain sanitized provider/MCP request IDs and clearly separate offline fixture evidence. | Core |
| PW-08 | read tools are default; dashboard mutations and any model calls have budgets, quotas, and a kill switch; secrets are server-side only. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| PW-09 | synthetic release runs cover missing captions, wrong version, partial upload, delayed acknowledgment, Grafana outage, and false-green data. Report detection and false alarms separately. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| PW-10 | ingest → query Grafana evidence → show blocker and cited source → approval-required annotation → recheck after fixture fix. No copyrighted media in public demo. | Run the seeded browser journey, retain the Playwright trace and short recording, and verify the evidence/refusal shown against API and audit state. | Core |

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

- Confirm festival/distributor workflow, required artifact matrix, evidence TTLs, and final greenlight owner.
- Configure isolated Grafana datasources/dashboard scopes, MCP auth, on-call ownership, quotas, and kill switch.
- Recheck current Grafana contest requirements and licensing before using real title/media or claiming qualification.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for PremiereWatch.**
