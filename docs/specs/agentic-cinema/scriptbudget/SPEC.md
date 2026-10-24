# ScriptBudget — implementation-ready specification

**Project ID:** `scriptbudget`<br>
**Track / family:** Agentic Cinema / Replit alternate 03<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [15-scriptbudget.md](../15-scriptbudget.md) (historical context only)<br>
**Primary audience:** Independent producers building an early budget and schedule from an authorized screenplay

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

Early planning requires scene/location/cast/resource breakdowns and explicit rates/assumptions. Generated numbers can hide source gaps, arithmetic, small-sample limits, or inappropriate artistic/market judgments.

**Product promise:** extract page/line-grounded scene facts, route ambiguity to review, calculate budgets/schedules deterministically from producer-owned rates and assumptions, and export clearly labeled draft scenarios without revenue/greenlight/artistic predictions.

**Tagline:** Grounded screenplay breakdowns and transparent production scenarios—never a success prediction.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Producer | Owns screenplay upload/rights, fact verification, rates/assumptions/scenario selection, schedule, and export approval. |
| Line producer | Reviews breakdown/resources/rate card and may edit assigned planning values; no investor-success claims. |
| Benchmark curator | Owns licensed descriptive comparable data/provenance/minimum sample policy. |
| Gemini/ADK service | Extracts typed scene facts and explains deterministic tradeoffs; cannot change rates/scenes/assumptions or publish. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Upload authorized PDF/Fountain screenplay with hash/access scope and preserve page/line evidence.
- Extract scenes/locations/cast roles/day-night/effects/crowd/animal flags/resources with verified or unverified state.
- Provide producer review/correction for scene breaks, flashbacks, ambiguous locations, missing pages, and resource flags.
- Calculate integer-cent costs from versioned rate cards, quantities, formulas, rounding, and named assumptions.
- Generate deterministic location-grouped draft schedule/scenarios and sensitivity views without removing scenes autonomously.
- Optionally use licensed descriptive comparables with n/distribution; export exact approved draft budget/schedule/assumptions with no market prediction.

### 1.4 Explicit non-goals

- No box-office/revenue/success/artistic-merit/greenlight score or investor recommendation.
- No protected-trait/cast-demographic inference or demographic/market-value features in cost/ranking.
- No model-authored numeric totals, silent scene removal/rate changes, or small-corpus causal/predictive claims.
- No real screenplay/private rate data in public demo or non-Google AI provider.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Use an original synthetic 8-page/6-scene low-budget screenplay, USD integer cents, 10-hour production days, 5-minute schedule granularity, and Europe/Amsterdam timezone.
- Support PDF text layer and Fountain up to 5 MB/150 pages; scene facts require page/line spans or remain UNVERIFIED and block final draft export.
- Base cost = sum over scenes/resources of `quantity × rate_cents × units`, with exact decimal quantity, half-up rounding at line level, then contingency percentage applied once at scenario subtotal. No float money.
- Comparable ranges require n≥5 licensed records and show min/median/max/n/missing exclusions; otherwise display no benchmark range. Offline uses scripted Gemini; integrated requires Replit provenance/hosting and actual Google extraction.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Producer confirms screenplay rights and uploads PDF/Fountain; app hashes, scopes access, and extracts stable page/line locations.
2. Gemini proposes typed scene/resource facts with spans; deterministic validation rejects absent references and flags ambiguous scene breaks/flashbacks.
3. Producer verifies/corrects every required breakdown field; unverified values remain visible and block final scenario approval.
4. Producer selects/edits a versioned rate card and assumptions; every line displays quantity/rate/unit/formula/source.
5. The deterministic engine computes scenario line/subtotal/contingency/total and a location-grouped schedule with day/night/resource constraints.
6. Optional licensed comparables add descriptive min/median/max/n only; sensitivity reruns explicit producer-selected variables without protected traits.
7. Gemini explains tradeoffs using persisted numbers and scene IDs; producer alone edits/selects/approves scenario and local export.
8. Draft PDF/CSV/JSON export/read-back includes all scenes, assumptions, sources, ranges/limitations, schedule, and prominent non-prediction label.

### 2.2 Lifecycle and transition authority

```text
SCRIPT_RIGHTS_CONFIRMED → PARSE_AND_SEGMENT → GEMINI_FACT_EXTRACTION → SOURCE_VERIFICATION → (UNVERIFIED_REVIEW ↔ BREAKDOWN_READY) → RATE_CARD_ASSUMPTIONS → DETERMINISTIC_SCENARIOS → PRODUCER_REVIEW → APPROVAL → DRAFT_EXPORT; any scene/rate/assumption/schedule change invalidates prior approval
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

1. Upload authorized PDF/Fountain screenplay with hash/access scope and preserve page/line evidence.
2. Extract scenes/locations/cast roles/day-night/effects/crowd/animal flags/resources with verified or unverified state.
3. Provide producer review/correction for scene breaks, flashbacks, ambiguous locations, missing pages, and resource flags.
4. Calculate integer-cent costs from versioned rate cards, quantities, formulas, rounding, and named assumptions.
5. Generate deterministic location-grouped draft schedule/scenarios and sensitivity views without removing scenes autonomously.
6. Optionally use licensed descriptive comparables with n/distribution; export exact approved draft budget/schedule/assumptions with no market prediction.

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
| Screenplay / SourceSpan | `screenplay_id`, `sha256`, `format`, `rights_confirmation`, `access_scope`, `pages`; span `page`, `line_start/end`, `text_hash` | Original immutable; rights required; page/line references stable and verified. |
| Scene / SceneFact | `scene_id`, `heading`, `order`, `source_spans`, `verification`; fact `kind`, `typed_value`, `span`, `state`, `reviewer` | Ordered unique scenes; required facts verified or UNVERIFIED; model cannot delete/reorder authoritatively. |
| ResourceRequirement / RateCard | `scene_id`, `resource_kind`, `quantity`, `units`, `source`; rate `resource_kind`, `rate_cents`, `unit`, `effective_at`, `version`, `producer` | Exact decimals/integer cents; nonnegative quantity/rate; every rate producer-owned/versioned. |
| AssumptionSet / Scenario | `assumption_id`, `production_days`, `contingency_bps`, `rules`, `assumptions`; scenario `scene_version`, `rate_version`, `assumption_version`, `input_hash` | Named assumptions and versions; any input change invalidates results/approval. |
| BudgetLine / BudgetScenario | `scene_id`, `resource`, `quantity`, `rate`, `formula`, `rounding`, `line_total_cents`; scenario `subtotal`, `contingency`, `total`, `schedule` | All numbers recomputed from persisted lines; no float; totals reconcile exactly and source-linked. |
| ComparableSet / DraftExport | `dataset_id`, `license`, `records`, `n`, `exclusions`, `min/median/max`; export `scenario_hash`, `approval`, `sha256`, `readback` | n≥5 for descriptive range; no predictive target; exact approved draft with limitations. |
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
scriptbudget/
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

Replit Agent development provenance and Replit hosting are integrated requirements. Google ADK/Gemini performs active extraction; deterministic code owns all costs/schedules/ranges. No third-party AI or box-office model is used.

For cinema projects, offline completion and integrated completion are separate statuses: the sandbox proves product behavior, while only the live-smoke evidence can prove the required partner path.

Background processing uses durable jobs with bounded exponential backoff and jitter, a maximum attempt count, lease expiry, and dead-letter visibility. Only idempotent read/analysis jobs retry automatically. External effects with unknown outcomes enter `RECONCILIATION_REQUIRED`; never blind-retry them. The API returns `202` with a job URI for work exceeding the normal request budget.

### 5.4 HTTP API contract

The paths below are the minimum product API. Generate the final schema from FastAPI and generate the TypeScript client. Request bodies use explicit typed fields; examples and all error variants belong in OpenAPI.

| Method and path | Actor | Behavior |
| --- | --- | --- |
| POST `/api/v1/screenplays` / GET `/api/v1/screenplays/{id}/source` | Producer | Rights-confirm/upload/hash screenplay and read authorized page/line source. |
| POST `/api/v1/screenplays/{id}/breakdown` | Producer | Run Gemini typed scene/resource extraction with source spans and uncertainty. |
| GET `/api/v1/screenplays/{id}/scenes` / PATCH `/api/v1/scenes/{id}` | Producer/Line producer | Review/correct/version scene facts and verification state. |
| PUT `/api/v1/rate-cards/{id}` / PUT `/api/v1/assumptions/{id}` | Producer | Version producer-owned rates, units, rounding, schedule/contingency assumptions. |
| POST `/api/v1/scenarios` / GET `/api/v1/scenarios/{id}` | Producer | Compute deterministic budget/schedule/sensitivity from exact input hash. |
| GET `/api/v1/scenarios/{id}/lines` | Producer/Line producer | Read every quantity/rate/formula/rounding/source and reconciliation total. |
| POST `/api/v1/scenarios/{id}/approval` | Producer | Approve exact scenes/rates/assumptions/schedule/export digest or reject. |
| POST `/api/v1/scenarios/{id}/exports` | Producer | Generate/read back labeled draft PDF/CSV/JSON with all limitations and source manifest. |
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
| get_screenplay_source_excerpt | read | Returns authorized bounded page/line source for typed extraction; no other project data. |
| propose_scene_breakdown | proposal | Gemini returns scene/fact/resource values + source spans + uncertainty; no rates/totals/deletion. |
| get_scenario_calculations | read | Returns persisted budget lines/totals/schedule/assumptions/comparable n/ranges for explanation. |
| draft_tradeoff_explanation | proposal | Explains location grouping/cost deltas using exact scenario values; cannot change or approve inputs. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

Parse Fountain headings or PDF text into stable page/line spans. Scene extraction is a typed proposal; required scene identity/heading/location/day-night/resource facts need exact spans and producer verification. Flashbacks are scene attributes, not reasons to merge/drop scenes. Ambiguous breaks/missing pages stay UNVERIFIED.

For each budget line, compute exact decimal `raw = quantity × rate_cents × units`, round half-up to integer cents once at line level, then `subtotal = Σline_total`. `contingency = round_half_up(subtotal × contingency_bps / 10000)` and `total = subtotal + contingency`. Never use binary floats for money. Schedule uses deterministic scene ordering: preserve required chronology constraints, then group by verified location and day/night, sort by location ID/scene order, and pack into 10-hour days with setup/teardown/resource limits; infeasible inputs remain UNSCHEDULED with reasons rather than dropped.

Comparables are descriptive only: validate license/compatible production type, exclude missing values explicitly, require n≥5, and show min/nearest-rank median/max/n. Sensitivity changes only producer-selected planning variables. Demographic/protected-trait fields are not features; perturbation tests require byte-identical costs/rank.

| Policy area | Normative rule |
| --- | --- |
| Grounded breakdown | Every scene fact page/line cited or UNVERIFIED; missing/ambiguous content requires review and cannot silently become authoritative. |
| Producer authority | Only producer changes rates/assumptions/schedule/scenes/approval; model explanations cannot mutate values or publish. |
| Range/bias honesty | All estimates show assumptions/formulas/n/distribution/missing exclusions; no predicted gross/success score/protected-trait feature. |
| Draft export | Every number source/formula-linked; unverified required scenes block approval; output prominently labeled early planning draft, not investment advice. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** A transparent line-producer workbook with ochre accents, screenplay evidence beside breakdown rows, editable rate cards, and budget formulas exposed without spreadsheet clutter or “AI greenlight” theatrics. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #7f5b1f; --color-accent-ink: #ffffff;
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
| /screenplays | Screenplay projects | Rights/access, parse/breakdown verification, scenario/draft state, and New screenplay. |
| /screenplays/{id}/breakdown | Scene breakdown | Scene order/headings/locations/cast/resources/day-night, source links, and unverified review queue. |
| /scenes/{id} | Scene evidence | Page/line screenplay viewer, typed facts/resources, ambiguity/flashback flags, and producer correction. |
| /rate-cards/{id} | Rates and assumptions | Versioned resource rates/units/effective dates, production days/contingency/rules, and change diff. |
| /scenarios/{id}/budget | Budget scenario | Scene/resource lines, quantity×rate×units formula, rounding, subtotal/contingency/total, and reconciliation. |
| /scenarios/{id}/schedule | Schedule and sensitivity | Location-grouped day schedule/list, unscheduled reasons, producer-selected variables, and descriptive comparables. |
| /scenarios/{id}/export | Draft approval and export | All input hashes/assumptions/unverified blockers/range limits, exact approval, and PDF/CSV/JSON read-back. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **SceneFact:** typed value with Verified/Unverified text, exact page/line source, and correction action; uncertainty blocks downstream approval.
- **BudgetLine:** quantity/rate/unit/formula/line total with source/version and inline editable producer controls; totals update only after persisted recompute.
- **ScheduleBoard:** day/location visual lanes plus semantic scene table and unscheduled reasons; no drag-only scheduling.
- **AssumptionBanner:** scenario/rate/schedule versions, contingency, comparable n/range, and “Early planning draft — not a prediction” persistent label.
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
- **Privacy:** Screenplays/provider payloads/rate cards are private and delete 30 days after final draft export by default or immediately on producer request. Derived scene facts/scenarios delete with project; audit retains hashes only. Public demo uses original synthetic scripts and fictional comparables.
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

Commit 30 original synthetic screenplays/scenario cases with clear/fragmented scenes, flashbacks, ambiguous headings/locations, missing page text, crowd/animal/effects flags, resource/rate boundaries, contingency/rounding, infeasible schedules, demographic mention perturbations, injected script instructions, and licensed fictional comparables n<5/n≥5/missing values. Include independent breakdown labels and hand-calculated budget/schedule goldens.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Extraction quality | Report exact scene/fact precision/recall and abstention by difficulty; target ≥90% exact required facts on clear subset and zero unsupported verified facts. |
| Arithmetic/schedule | 100% hand-calculated line/subtotal/contingency/total/rounding and schedule fixtures; zero floats/dropped scenes/unreported infeasibility. |
| Range/bias honesty | 100% ranges show n/min/median/max/exclusions/assumptions; n<5 suppressed; demographic perturbations cause byte-identical cost/rank. |
| Authority/security | Zero script-injection tool/policy/cross-project effects or model rate/scene/export changes; stale approvals always refused. |
| Runtime/export | Integrated Replit + actual Google extraction evidenced; all draft exports read back with formulas/sources/limitations and no success/box-office language. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Upload the original synthetic screenplay and inspect rights/hash plus page/line-grounded scene breakdown.
2. Open an ambiguous flashback/location and keep it UNVERIFIED until producer correction; show final approval blocked before then.
3. Edit a producer rate and contingency; inspect exact budget-line formulas, rounding, and deterministic total delta.
4. Generate a location-grouped schedule and an infeasible control that leaves scenes explicitly unscheduled rather than dropping them.
5. Show comparables n/min/median/max and a demographic-mention invariance check; no revenue/success prediction exists.
6. Producer approves/exports/read back the labeled draft; integrated lane shows Replit hosting and actual Google extraction provenance.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Screenplay/Fountain/PDF source parser, scene/fact schemas, rights/access, and source-grounding tests.
2. Gemini breakdown + scripted adapter, verification/correction UI, ambiguity/injection/privacy tests.
3. Exact money/rate/budget/schedule/sensitivity engines with hand/property/golden tests.
4. Comparable provenance/ranges, scenario/budget/schedule UI, producer approval, and draft export/read-back.
5. 30-case eval, bias/accessibility/security review, Replit provenance/deployment, Google live smoke, and demo.

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
| SB-01 | upload requires rights/permission confirmation; file hash and access scope are recorded; demo uses original synthetic scripts only. | Run the seeded browser journey, retain the Playwright trace and short recording, and verify the evidence/refusal shown against API and audit state. | Core |
| SB-02 | each scene fact links to source page/line or is marked `unverified`; missing pages and ambiguous scene breaks require review. | Schema and integration tests resolve every reference to immutable source content; mutate/delete a reference and verify a visible hold, never a pass. | Core |
| SB-03 | all currency uses integer minor units; costs are recomputed from explicit rate cards and rounding rules; example fixtures match hand calculations. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SB-04 | estimates display assumptions, sample count, min/median/max or stated interval, and exclude missing data; no single “predicted gross” or success score. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SB-05 | changes to rate card, assumptions, schedule, or exported report require authenticated producer approval and audit diff. | State-machine and API negative tests for wrong actor, stale digest/version, replay, and concurrent requests; assert zero external side effects. | Core |
| SB-06 | do not infer cast demographics or market value; no protected-trait features. Tests verify that changing a demographic mention cannot change cost or ranking. | Run the seeded browser journey, retain the Playwright trace and short recording, and verify the evidence/refusal shown against API and audit state. | Core |
| SB-07 | script text cannot trigger tools, reveal another project, or modify application policy. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SB-08 | synthetic screenplay corpus covers fragmented scenes, flashbacks, ambiguous locations, missing page text, and arithmetic boundaries; report extraction exactness and forecast error separately. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| SB-09 | Replit Agent provenance and Replit-hosted URL are verified; Google AI runtime is used on active extraction path. | `make live-smoke` against the required isolated partner/runtime plus offline contract tests; retain sanitized provider/MCP/hosting evidence and never substitute fixtures. | Integration |
| SB-10 | show a grounded breakdown, one uncertain scene sent to review, producer-adjusted rate card, deterministic schedule/cost change, and a labeled draft export. | Unit/property tests with hand-calculated and boundary fixtures, plus API round-trip tests; failures must be fail-first and reproducible. | Core |

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

- Confirm production type, screenplay/rate/comparable data rights and licenses, retention, and producer/line-producer authority.
- Have a line producer validate resource taxonomy, rates, schedule rules, rounding, and minimum comparable sample policy.
- Recheck current Replit contest requirements and never use the tool for investment, market success, or artistic-merit recommendations.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for ScriptBudget.**
