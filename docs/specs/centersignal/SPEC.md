# CenterSignal — implementation-ready specification

**Project ID:** `centersignal`<br>
**Track / family:** Independent agent products / 09<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [2026-10-23-centersignal-spec.md](../2026-10-23-centersignal-spec.md) (historical context only)<br>
**Primary audience:** Community navigators, center curators, and residents using one city’s cooling/warming-center directory

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

People may travel to a center after hours, capacity, accessibility, pet, or language information changes; a static directory hides when and how each fact was verified.

**Product promise:** verify a narrow field set through a sandbox provider readback or approved source, atomically publish evidence-backed status snapshots with expiry, and let closed-door reports elevate verification without directly publishing a closure.

**Tagline:** A public center directory whose freshness and evidence are visible.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Public visitor | Reads public status, filters centers, and optionally submits a pseudonymous failure report; cannot change status. |
| Curator | Owns verification tasks, provider-call review, safety/closure decisions, and manual status snapshots. |
| Center provider persona | Synthetic authorized speaker who states and confirms exact changed fields during readback. |
| Agent service | Extracts proposed changes and performs scripted readback; cannot publish or decide safety-related fields. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Maintain a synthetic center registry and public read-only directory with explicit open/unknown/closed distinctions.
- Run scheduled verification tasks and scripted provider calls with disclosure, allowed windows, and per-center caps.
- Extract field proposals, read back full canonical values, require explicit provider confirmation, and preserve evidence quotes.
- Atomically update only low-judgment allowlisted fields; route mixed/safety/closure/contradictory calls wholly to curator.
- Expire each status to UNKNOWN at TTL and display last verified/source age everywhere.
- Accept transactional user failure reports that create/raise one open task without automatically publishing closure.

### 1.4 Explicit non-goals

- No guarantee of current availability, exact capacity counts, eligibility decisions, navigation, or emergency advice.
- No real phone calls or real shelter/center claims in the demo.
- No partial publication from a call containing any review-required field.
- No user-report-driven closure, retained audio by default, or exposure of reporter identity.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Use 8 fictional centers in `Example City`, sandbox voice turns, and English; no live telephony credentials are required.
- TTLs: staffed-through/capacity 30 minutes, languages/pet policy 60 minutes, accessibility 24 hours; any open/closed or safety-related change requires curator review.
- Capacity enum is `20_PLUS`, `5_TO_19`, `1_TO_4`, `FULL`, `UNKNOWN`; exact counts are rejected.
- Calling window is 09:00–17:00 local, maximum 2 attempts/task; automated disclosure is mandatory at turn one.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Scheduler creates due verification tasks from per-field TTLs and curator/source priorities.
2. Sandbox adapter checks fictional center consent/window/cap/allowlist and begins with automated-caller disclosure.
3. Provider states changes; the agent proposes typed fields with quote/turn references and canonical values.
4. The assistant reads back every full changed value and requires an explicit later confirmation turn; corrections restart readback.
5. Deterministic field policy checks allowlist, contradictions, capacity enum, safety/closure rules, and evidence sequence.
6. If all fields are safe, one transaction publishes a complete snapshot; if any field needs review, none from that call publish.
7. Public directory shows current facts, last verified, expiry/unknown, filters, and evidence summary without private call details.
8. A visitor closed-door report marks affected status unverified and creates/raises one task atomically; curator/provider evidence resolves it.

### 2.2 Lifecycle and transition authority

```text
VERIFICATION_DUE → CALL_QUEUED → PROVIDER_STATEMENT → CHANGE_PROPOSED → EXACT_READBACK → PROVIDER_CONFIRMATION → FIELD_POLICY → (ATOMIC_PUBLISH | NEEDS_REVIEW) → STATUS_SNAPSHOT → EXPIRED_UNKNOWN; user report → EXISTING_OR_NEW_OPEN_TASK (status becomes UNVERIFIED, not automatically CLOSED)
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

1. Maintain a synthetic center registry and public read-only directory with explicit open/unknown/closed distinctions.
2. Run scheduled verification tasks and scripted provider calls with disclosure, allowed windows, and per-center caps.
3. Extract field proposals, read back full canonical values, require explicit provider confirmation, and preserve evidence quotes.
4. Atomically update only low-judgment allowlisted fields; route mixed/safety/closure/contradictory calls wholly to curator.
5. Expire each status to UNKNOWN at TTL and display last verified/source age everywhere.
6. Accept transactional user failure reports that create/raise one open task without automatically publishing closure.

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
| Center / CenterContactPolicy | `center_id`, `name`, `public_location`, `timezone`, `active`; policy `consent`, `allowed_number`, `window`, `attempt_cap`, `live_enabled` | Synthetic public records; live disabled; number allowlist/consent checked server-side. |
| VerificationTask / CallAttempt | `task_id`, `center_id`, `reason`, `priority`, `state`; attempt `correlation_id`, `sequence`, `disclosure_turn`, `outcome` | Duplicate report merges open task; max attempts; disclosure required before provider content. |
| ProposedChange / EvidenceTurn | `attempt_id`, `field`, `canonical_value`, `statement_turn`, `readback_turn`, `confirmation_turn`, `quote_hashes` | Strict statement→full readback→explicit confirmation order; correction/hedge/silence invalidates. |
| PolicyDecision | `attempt_id`, `field_decisions`, `all_fields_safe`, `rule_version`, `reason_codes` | One call-level atomic decision; any unsafe/contradictory/unrecognized field blocks whole snapshot. |
| StatusSnapshot / StatusField | `center_id`, `snapshot_version`, `published_at`, `source_attempt`; field `value`, `verified_at`, `expires_at`, `evidence_id`, `state` | Public field resolves to evidence/policy; expired values project UNKNOWN; no partial call update. |
| UserFailureReport | `report_id`, `center_id`, `field`, `observed_at`, `optional_contact_ciphertext`, `task_id`, `dedupe_key` | Transaction creates/raises one open task and unverified marker; identity never exposed without consent. |
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
centersignal/
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
| GET `/api/v1/public/centers` / GET `/api/v1/public/centers/{id}` | Anonymous | Read fresh/unknown status, last verified, accessibility/language/pet filters; no private evidence/contact. |
| POST `/api/v1/public/centers/{id}/failure-reports` | Anonymous rate-limited | Submit bounded report/dedupe key; transaction returns task reference without curator-private data. |
| GET `/api/v1/curator/tasks` / POST `/api/v1/curator/tasks/{id}/calls` | Curator | Prioritize queue and start a sandbox call after policy preconditions. |
| POST `/api/v1/call-attempts/{id}/turns` | Sandbox provider adapter | Submit signed scripted provider turn and process disclosure/readback/confirmation state. |
| GET `/api/v1/call-attempts/{id}/review` | Curator | Inspect proposals, evidence turns, atomic policy reasons, and review requirements. |
| POST `/api/v1/call-attempts/{id}/curator-decision` | Curator | Approve/reject held complete snapshot with exact evidence/version; required for safety changes. |
| POST `/api/v1/centers/{id}/status-expiry` | Scheduler worker | Evaluate TTL and persist/emit unknown projections; does not erase prior evidence. |
| GET `/api/v1/centers/{id}/evidence` | Curator/Auditor | Read scoped quote/event/policy/audit lineage and hash verification. |
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
| get_verification_context | read | Returns allowed center fields/current values/task and scripted provider turns; no unrelated centers. |
| propose_structured_changes | proposal | Returns field/canonical value/statement quote; exact counts and unrecognized fields rejected. |
| validate_readback_sequence | proposal | Deterministic helper returns missing/full-value/confirmation/order errors; cannot publish. |
| summarize_curator_review | proposal | Summarizes policy reasons/evidence; curator alone decides held snapshots. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

For each proposed field, locate provider statement `S`, assistant readback `R`, and provider confirmation `C` with increasing turn indexes. Canonicalize the full value (including end time, enum, language list, or pet condition) and require it to appear exactly in `R`. `C` must match an explicit confirmation grammar such as “yes, that is correct”; maybe, silence, wrong-speaker, correction, or new conditions restart/fail the sequence. Stop requests end the call.

Field policy then evaluates all proposed fields together. Auto-publish candidates are limited to staffed-through, capacity band, supported languages, and pet policy; exact capacity, closure/removal/open-state, accessibility/safety/eligibility, contradictory response, and unknown fields require curator. If any field requires review, persist the whole attempt as NEEDS_REVIEW and publish zero fields. A snapshot field expires at its own TTL and the public projection returns `UNKNOWN` with last verified time.

| Policy area | Normative rule |
| --- | --- |
| Call consent/disclosure | Sandbox script identifies automated caller; live adapter refuses without center consent, number allowlist, local window, attempt cap, and explicit live flag. |
| Atomic evidence gate | Statement/readback/confirmation and field policy all pass before one snapshot transaction; no mixed safe/unsafe partial updates. |
| Failure reports | Report+task promotion+unverified marker commit atomically; duplicates merge; report alone never publishes closed/open. |
| Public honesty | Open, closed, and unknown are distinct text/icon states; stale open becomes unknown. Capacity always uses bands, never exact model-invented counts. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** A reassuring public directory paired with a forensic curator console: clear civic blue, large open/unknown labels, useful filters, and minimal friction for reporting a failed visit. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #216a78; --color-accent-ink: #ffffff;
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
| /centers | Public directory | Mobile-first list/map alternative, open/unknown/accessibility/language/pet filters, last verified, and source-stale banners. |
| /centers/{id} | Public center detail | Address/access instructions, status fields with expiry/evidence age, capacity band, and Report a problem. |
| /centers/{id}/report | Failure report | Observed field/time, optional details/contact consent, duplicate-safe confirmation, and no promise of immediate update. |
| /curator/tasks | Verification queue | Due/expired/report-promoted tasks, center/reason/age/attempts, and sandbox call action. |
| /calls/{id} | Readback review | Turn timeline, statement/readback/confirmation highlights, proposed canonical fields, and policy result. |
| /curator/review/{id} | Atomic snapshot decision | Complete old/new field diff, safety hold reasons, all-or-nothing approval, and evidence hashes. |
| /curator/centers/{id}/history | Status evidence history | Snapshots, TTL transitions, user reports, call attempts, policy versions, and audit integrity. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **CenterStatusCard:** name/location, text/icon open-unknown-closed, last verified, capacity band, and key filters; no green-only meaning.
- **FreshnessTimestamp:** relative time plus exact local timestamp and expiry; expired state announces on refresh without abrupt focus.
- **ReadbackTimeline:** three evidence turns with order markers and canonical value diff; hedges/corrections show exactly why review is required.
- **FailureReportForm:** short accessible form with optional identity/consent, anti-spam/rate-limit feedback, and persistent submission state.
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
- **Privacy:** No audio is retained. Turn transcripts store only required redacted quotes for 30 days; reporter optional contact deletes after task closure and is never shared by default. Public snapshots retain evidence hashes/version history for one year.
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

Commit 8 fictional centers and 80 scripted provider personas: exact confirmations, partial readback, hedges, corrections, contradictions, stop requests, wrong speaker, no answer, prompt injection, exact capacity attempts, mixed safe/unsafe changes, duplicate/no-answer calls, expired fields, and duplicate closed-door reports. Include expected atomic public projections and independent safe-change labels.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Update safety | Zero unsafe/partial auto-updates across all personas; 100% closure/safety/contradiction/mixed calls held in full. |
| Readback correctness | 100% statement/full-readback/explicit-confirmation order tests; correction/hedge/silence/wrong speaker always fails. |
| Coverage/escalation | Report safe-change coverage and over-escalation with per-field denominators; target ≥85% on clearly safe exact-confirmation subset. |
| Freshness/report atomicity | 100% TTL and mixed-field transaction tests; duplicate reports yield one open task and no direct closure. |
| Privacy/UX | No audio/raw personal contacts in logs; zero reporter identity exposure; complete mobile filter/report keyboard and screen-reader journeys. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Open the public directory and compare fresh, expired-unknown, and closed statuses with exact timestamps.
2. Run an exact synthetic provider readback for a safe capacity/language change and publish one atomic evidence-backed snapshot.
3. Run a mixed safe-plus-closure call and show zero fields auto-publish while the curator receives the whole review.
4. Submit a closed-door report twice and show one promoted task plus unverified public status, not an automatic closure.
5. Curator resolves the held snapshot with evidence and the directory updates with a new version.
6. Inspect quote/policy/audit lineage and verify no audio or reporter identity is exposed.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Center/status schema, TTL projector, public directory/filter UI, and synthetic fixtures.
2. Transactional failure reports/task queue, role projections, rate limits, and duplicate tests.
3. Sandbox voice turn state machine, exact readback validator, Strands proposals, and adversarial personas.
4. Atomic field policy/snapshot/curator approval, evidence history, audit, and restart tests.
5. 80-persona eval, accessibility/privacy checks, hosted synthetic demo, operations, and pilot runbook.

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
| CS-01 | every sandbox script clearly identifies the automated caller; live call is impossible without center consent, approved window, per-center cap, number allowlist, and explicit live-mode flag. | API authorization/privacy integration tests with two tenants/actors and canary values; inspect model prompts, responses, exports, caches, and logs. | Core |
| CS-02 | auto-update requires provider-stated value, assistant readback containing the full canonical value, and explicit provider confirmation in order; “maybe,” correction, or silence fails. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| CS-03 | only configured low-judgment fields can auto-update. Closure/removal, capacity beyond configured band, contradictory response, and unrecognized field route to curator. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| CS-04 | when any field in one call requires review, no field from that call is partially published; test mixed safe/unsafe changes. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| CS-05 | every public status shows last verified time and expires to `UNKNOWN` after its configured TTL; stale status is not rendered as open. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| CS-06 | user report creates or raises one open verification task in the same transaction; duplicate submissions do not multiply tasks; the status remains unverified until provider evidence or curator decision. | Concurrency and integration tests deliver exact duplicates, legitimate near-duplicates, reordered events, and retries; assert one intended effect and no lost positive control. | Core |
| CS-07 | every public field maps to a source quote/event and policy version; append-only audit rejects update/delete and detects tampering. | Schema and integration tests resolve every reference to immutable source content; mutate/delete a reference and verify a visible hold, never a pass. | Core |
| CS-08 | no audio retained by default; transcripts redact personal contact details; reporting user identity is optional and never exposed to centers without consent. | API authorization/privacy integration tests with two tenants/actors and canary values; inspect model prompts, responses, exports, caches, and logs. | Core |
| CS-09 | scripted provider personas include exact confirmations, hedges, contradictions, stop requests, wrong speaker, prompt injection, and no answer. Zero unsafe auto-updates; report safe-change coverage and over-escalation. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| CS-10 | user can filter by open/unknown, accessibility, and language; “unknown” is visually distinct from “closed”; mobile keyboard/screen-reader flows pass. | Playwright keyboard/mobile journeys, axe-core, and documented NVDA/VoiceOver plus 200%/400% zoom checks; retain screenshots and manual notes. | Core |
| CS-11 | simulate a verified status, an expired status, a false/ambiguous readback held for curator, and a user-reported closed door promoted to the queue. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |

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

- Name city/center-list owner and approve authoritative sources, field definitions, capacity bands, TTLs, and dispute handling.
- Obtain center calling consent/disclosure/window/allowlist and community support/fallback for people who cannot rely on the page.
- Approve reporter privacy/rate limiting, curator staffing, retention, and real-center claims before any live call or deployment.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for CenterSignal.**
