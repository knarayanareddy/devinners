# CrewClock — implementation-ready specification

**Project ID:** `crewclock`<br>
**Track / family:** Agentic Cinema / IBM alternate 03<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [03-crewclock.md](../03-crewclock.md) (historical context only)<br>
**Primary audience:** Production coordinators planning a small documentary crew’s multi-location day

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

Scenes, travel, access, availability, equipment, meals, setup, and rest interact. A plausible spreadsheet can hide double booking or assume an unreviewed labor rule.

**Product promise:** parse inputs into cited typed records, compute honestly labeled feasible/optimal/infeasible/unknown schedules with a deterministic solver, and require coordinator approval before any call-sheet export.

**Tagline:** Feasible documentary crew days with every constraint and tradeoff exposed.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Production coordinator | Owns scenes/resources/travel inputs, candidate selection, approval, and call-sheet export. |
| Crew participant | Views own role-scoped availability/schedule; private reason text remains owner-only. |
| Rule reviewer | Reviews constraint packs and sources; cannot self-activate a pack. |
| Gemini/ADK service | Extracts call-sheet facts and explains persisted conflicts; never computes feasibility or changes rules. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Input production day, scenes, roles/equipment, locations, travel estimates, availability, setup/teardown, and buffers.
- Maintain twice-reviewed versioned hard/soft constraint packs with source and effective date.
- Use CP-SAT to compute candidates with status, objective, bound, constraint IDs, and uncovered/infeasibility explanation.
- Recompute on any travel/availability/duration/rule change and invalidate stale approvals.
- Provide timeline/list review, role-private projections, conflict explanation, and candidate comparison.
- Export/read back coordinator-approved PDF/CSV call sheet without private reasons or unproven compliance claims.

### 1.4 Explicit non-goals

- No inferred statutory/union rules, legal compliance certification, automatic call-sheet sending, or hard-rule override.
- No labeling timeout/unknown as feasible or optimality without solver proof.
- No private availability reasons in model prompts/call sheets or participant double booking.
- No live travel provider requirement; demo travel estimates are explicit versioned inputs.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Use one fictional documentary crew, 6 scenes, 4 locations, 8 role participants, Europe/Amsterdam timezone, 5-minute scheduling granularity, and Europe/Amsterdam naive-local input rejected unless zone confirmed.
- Use pinned OR-Tools CP-SAT, one worker, fixed seed 0, 15-second limit; all durations integer minutes and travel includes explicit source/method/timestamp.
- Demo constraint pack contains only production policies (exclusive resources, availability, setup/teardown, meal break after 6 hours, 10-hour rest across days); no legal/union claim.
- Coordinator publishes local PDF/CSV only; publication recipient set is `production-participants`, with role-redacted projections.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Coordinator creates a timezone-aware production day and imports/enters scenes/resources/windows.
2. Gemini may extract candidate call-sheet fields with source spans; humans verify required values and private reasons remain separate.
3. A twice-reviewed rule pack is activated and the input validator rejects duplicates, overlaps, invalid travel, and timezone-less data.
4. CP-SAT canonicalizes inputs and returns candidate status/objective/bound or a constraint-linked infeasible/unknown result.
5. Coordinator inspects timeline/list, travel/setup/meal/rest traces, and soft-objective tradeoffs; no model-supplied totals.
6. Changing travel, availability, duration, or rules marks candidate/approval stale and requires a fresh solve.
7. Coordinator selects/approves exact schedule/rule/recipient hash; publication rechecks current version.
8. PDF/CSV export is parsed/read back and each participant sees only their role-scoped call-sheet projection.

### 2.2 Lifecycle and transition authority

```text
DAY_DRAFT → INPUT_VERIFIED → RULEPACK_ACTIVE → SOLVING → (OPTIMAL | FEASIBLE | INFEASIBLE | UNKNOWN) → COORDINATOR_REVIEW → APPROVAL → CALL_SHEET_EXPORTED; any material input change → STALE → SOLVING; infeasible/unknown requires human input, never relaxation
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

1. Input production day, scenes, roles/equipment, locations, travel estimates, availability, setup/teardown, and buffers.
2. Maintain twice-reviewed versioned hard/soft constraint packs with source and effective date.
3. Use CP-SAT to compute candidates with status, objective, bound, constraint IDs, and uncovered/infeasibility explanation.
4. Recompute on any travel/availability/duration/rule change and invalidate stale approvals.
5. Provide timeline/list review, role-private projections, conflict explanation, and candidate comparison.
6. Export/read back coordinator-approved PDF/CSV call sheet without private reasons or unproven compliance claims.

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
| ProductionDay / Scene | `day_id`, `date`, `timezone`; scene `id`, `duration_min`, `setup_min`, `teardown_min`, `location_id`, `window`, `sequence` | Unique scene IDs; positive durations/buffers; timezone-aware windows and no duplicate active scenes. |
| RoleRequirement / Resource / Availability | `scene_id`, `role`, `resource_id`, `participant_id`; availability `start`, `end`, `effect`, `private_reason` | Exclusive resources/participants cannot overlap; model/export projections omit private reason. |
| Location / TravelEstimate | `location_id`, `access_window`; travel `from`, `to`, `minutes`, `method`, `source`, `observed_at`, `version` | Nonnegative integer duration; directed pairs; source/timestamp mandatory and changes invalidate solves. |
| ConstraintRule / RulePack | `rule_id`, `kind`, `hard`, `parameters`, `source`, `version`, `reviewers`, `effective_at` | Hard/soft separated; two reviewers; unreviewed pack cannot drive a verdict. |
| ScheduleCandidate / Assignment | `candidate_id`, `input_hash`, `solver_version`, `status`, `objective`, `bound`, `solve_ms`; assignment `scene`, `start`, `end`, `resources` | Canonical stable output; OPTIMAL only solver-proven; assignment satisfies all hard constraints. |
| ApprovalSnapshot / CallSheet | `candidate_id`, `schedule_hash`, `rule_version`, `recipient_scope`, `approved_by`; export `hash`, `readback` | Exact schedule/inputs/rules/recipients bound; edits invalidate; private fields excluded by schema. |
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
crewclock/
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

Google ADK + Gemini extracts/explains, while pinned CP-SAT owns all schedule facts. IBM Bob development use/provenance is required for integrated track evidence. No runtime IBM endpoint is assumed without current official verification.

For cinema projects, offline completion and integrated completion are separate statuses: the sandbox proves product behavior, while only the live-smoke evidence can prove the required partner path.

Background processing uses durable jobs with bounded exponential backoff and jitter, a maximum attempt count, lease expiry, and dead-letter visibility. Only idempotent read/analysis jobs retry automatically. External effects with unknown outcomes enter `RECONCILIATION_REQUIRED`; never blind-retry them. The API returns `202` with a job URI for work exceeding the normal request budget.

### 5.4 HTTP API contract

The paths below are the minimum product API. Generate the final schema from FastAPI and generate the TypeScript client. Request bodies use explicit typed fields; examples and all error variants belong in OpenAPI.

| Method and path | Actor | Behavior |
| --- | --- | --- |
| POST `/api/v1/production-days` / POST `/api/v1/days/{id}/scenes` | Coordinator | Create timezone-aware day/scenes/resources and validate graph/input. |
| PUT `/api/v1/days/{id}/travel` / PUT `/api/v1/me/availability` | Coordinator/Participant | Version travel and role-private availability effects with source/projection controls. |
| POST `/api/v1/rule-packs` / POST `/api/v1/rule-packs/{id}/activate` | Rule reviewer | Create and twice-review/activate immutable typed rule pack. |
| POST `/api/v1/days/{id}/solve` | Coordinator | Run canonical solver asynchronously with fixed config and input hash. |
| GET `/api/v1/candidates/{id}` / GET `/api/v1/candidates/{id}/conflicts` | Coordinator | Return timeline, status/objective/bound, hard traces, soft costs, and conflict IDs. |
| POST `/api/v1/candidates/{id}/select` | Coordinator | Select candidate for review without publishing or changing solver result. |
| POST `/api/v1/candidates/{id}/approval` | Coordinator | Approve exact schedule/rule/recipient/local-export digest; stale returns 409. |
| POST `/api/v1/candidates/{id}/call-sheet` / GET `/api/v1/me/call-sheet` | Coordinator/Participant | Generate/read back PDF+CSV and role-redacted participant projection. |
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
| get_call_sheet_source | read | Returns bounded authorized source text/spans for candidate extraction. |
| get_solver_result | read | Returns persisted status/objective/bound/assignments/conflict IDs; no solver mutation. |
| explain_constraint_conflict | proposal | Explains named reviewed constraints and inputs without inventing rules/times. |
| draft_schedule_summary | proposal | Uses deterministic candidate values and labels infeasible/unknown; cannot publish or send. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

Canonicalize scene/resource/participant IDs and discretize all times to 5-minute integer ticks in the production timezone. Create optional/required interval variables for scene work, setup, teardown, travel, meals, and rest. Hard constraints enforce access/availability windows, no-overlap for participants/equipment/locations as declared, directed travel, prerequisites, required setup/teardown, meal/rest rules, and production-day bounds. Soft penalties separately represent travel minutes, idle gaps, and overtime exposure using reviewed integer weights.

Run CP-SAT with one worker/fixed seed/version. Map solver status exactly: OPTIMAL only proven optimal; FEASIBLE for a feasible non-proven solution; INFEASIBLE only solver-proven; timeout/unbounded/error = UNKNOWN. Report objective and best bound without claiming a gap when unsupported. Infeasibility explanation uses an independently computed conflict set/unsatisfied input list where available; it never drops constraints to find a “valid” schedule. A naive validator rechecks every returned assignment.

| Policy area | Normative rule |
| --- | --- |
| Rule provenance | Every hard constraint has source/version/two reviewers/effective scope; statutory/union labels are absent from the fictional demo. |
| Solver honesty | Timeout, malformed input, and UNKNOWN remain non-publishable; FEASIBLE and OPTIMAL are never conflated. |
| Recompute/approval | Any travel/availability/scene/resource/rule change changes input hash, invalidates candidate/approval, and requires fresh review. |
| Privacy/export | Private reason text never enters solver/model/call sheet; participant projection contains only own schedule and shared logistics. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** A precise production-planning board with cobalt accents, timeline and list parity, visible solver-status language, and conflict explanations that read like a coordinator’s working notes. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #2c5795; --color-accent-ink: #ffffff;
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
| /days | Production days | Date/status/rule pack, candidate state, approval/export status, and New day. |
| /days/{id}/inputs | Scene and resource builder | Scene list/timeline, role/equipment/location windows, setup/teardown, validation, and source citations. |
| /days/{id}/travel | Travel and availability | Directed travel matrix with source/age, role availability, private projection, and invalid/stale warnings. |
| /days/{id}/rules | Constraint pack | Hard vs soft sections, sources/reviewers/effective version, weights, and activation state. |
| /candidates/{id} | Schedule review | Timeline/list parity, solver status/objective/bound, travel/meal/rest traces, and conflict panel. |
| /candidates/{id}/compare | Candidate comparison | Feasible candidates and soft tradeoffs with table equivalents; infeasible/unknown kept separate. |
| /candidates/{id}/publish | Call-sheet approval | Exact schedule/rule/recipient hash, stale diff, redacted preview, export/read-back, and audit. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **ScheduleTimeline:** visual lanes plus equivalent sortable scene table and keyboard time editing; overlaps/conflicts have text labels.
- **SolverStatus:** OPTIMAL/FEASIBLE/INFEASIBLE/UNKNOWN with objective/bound/solve time and plain-language meaning.
- **ConstraintTrace:** rule ID/source/version and the exact scenes/resources/times involved; suggested edits are links, not automatic fixes.
- **CallSheetPreview:** print/PDF layout with timezone, version, sources, private-field absence, and participant-view toggle limited to authorized previews.
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
- **Privacy:** Availability private reasons delete 7 days after the production day; schedule/audit records persist 90 days with role labels. Source call sheets delete on coordinator request and are removed from model payloads/caches. Call-sheet downloads expire after 15 minutes.
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

Commit 50 synthetic production-day scenarios: feasible multi-location days, access/weather windows, exclusive role/equipment overlap, meal/rest/overtime boundaries, directed travel changes, missing/timezone-less inputs, duplicate scenes, infeasible and timeout controls, private canaries, and stale publish approvals. Include naive-validator expected feasibility and hand-calculated small schedules/objectives.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Feasibility correctness | Zero hard-constraint violations/double bookings across all returned schedules and property tests; naive validator agrees on 100% fixtures. |
| Solver honesty | 100% OPTIMAL/FEASIBLE/INFEASIBLE/UNKNOWN labels match solver proof/status; timeout never publishes. |
| Recompute/approval | 100% material input mutations change hash/invalidate approval; stale/wrong-recipient export refused. |
| Evaluation quality | Report feasibility accuracy, objective/bound/gap, solve time, human edits, and comparison to a simple sequential baseline; small cases match hand calculations. |
| Privacy/partner | Zero private reasons in solver/model/export; scripted/live Gemini lanes and Bob development evidence remain distinct. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Open a feasible seeded multi-location day and inspect reviewed hard/soft rules.
2. Solve and inspect timeline/list, objective/bound, travel/setup/meal traces, and naive validation.
3. Open an infeasible scenario and show named constraints with no automatic relaxation.
4. Change a travel estimate and prove prior candidate and publish approval become stale.
5. Resolve/re-solve, approve exact schedule/recipients, export/read back PDF+CSV, and view role-redacted participant output.
6. Show private-reason exclusion and separate real/scripted Gemini plus IBM Bob provenance.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Typed day/scene/resource/travel schemas, canonical time utilities, naive validator, and property tests.
2. Reviewed rule packs, CP-SAT solver, status/objective/conflict reporting, and 50 scenarios.
3. ADK/Gemini source extraction/explanation with scripted path, privacy projections, and injection tests.
4. Candidate/timeline/compare UI, version-bound approval, PDF/CSV export/read-back, and audit.
5. Performance/solver recovery, accessibility, Bob provenance, cloud/rollback runbook, and demo.

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
| CC-01 | duplicate scenes, timezone-less times, overlapping exclusive resources, or invalid travel duration are rejected or held for coordinator clarification. | Concurrency and integration tests deliver exact duplicates, legitimate near-duplicates, reordered events, and retries; assert one intended effect and no lost positive control. | Core |
| CC-02 | every hard constraint has source/version/reviewer; unreviewed rule packs cannot drive a compliance verdict. | Schema and integration tests resolve every reference to immutable source content; mutate/delete a reference and verify a visible hold, never a pass. | Core |
| CC-03 | `OPTIMAL`, `FEASIBLE`, timeout, and `INFEASIBLE` are distinct; objective and lower bound are reported; no “optimal” claim without solver proof. | Unit/property tests with hand-calculated and boundary fixtures, plus API round-trip tests; failures must be fail-first and reproducible. | Core |
| CC-04 | impossible schedule returns named conflicting constraints and an explicit human action path, not a relaxed solution. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| CC-05 | publishing requires coordinator approval bound to exact schedule, recipients, and rule version; edits invalidate it. | State-machine and API negative tests for wrong actor, stale digest/version, replay, and concurrent requests; assert zero external side effects. | Core |
| CC-06 | changing a travel estimate, availability, or scene duration invalidates prior candidate and reruns the solver; stale approval is refused. | State-machine and API negative tests for wrong actor, stale digest/version, replay, and concurrent requests; assert zero external side effects. | Core |
| CC-07 | fixed input/solver version returns stable constraints and objective; property tests verify no participant is double-booked. | Unit/property tests with hand-calculated and boundary fixtures, plus API round-trip tests; failures must be fail-first and reproducible. | Core |
| CC-08 | cast/crew availability is role-scoped; private reason fields are not sent to the model or included in the call sheet. | API authorization/privacy integration tests with two tenants/actors and canary values; inspect model prompts, responses, exports, caches, and logs. | Core |
| CC-09 | synthetic productions cover multi-location days, weather/access window, overtime thresholds, missing inputs, and infeasible cases; report feasibility accuracy, objective cost, and human edits. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| CC-10 | Gemini/Google is active; IBM Bob development evidence is retained; demo includes one feasible schedule, one infeasible schedule, a change and a stale publish approval refusal. | `make live-smoke` against the required isolated partner/runtime plus offline contract tests; retain sanitized provider/MCP/hosting evidence and never substitute fixtures. | Integration |

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

- Select actual jurisdiction/union/production policies and authorized rule reviewers; do not activate unreviewed legal rules.
- Confirm travel source/update policy, coordinator approver, participant privacy, and call-sheet format/distribution.
- Recheck current IBM track rules before qualification claims and validate schedule usefulness with a production coordinator.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for CrewClock.**
