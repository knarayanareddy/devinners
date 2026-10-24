# AssetFinder — implementation-ready specification

**Project ID:** `assetfinder`<br>
**Track / family:** Agentic Cinema / ClickHouse alternate 03<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [12-assetfinder.md](../12-assetfinder.md) (historical context only)<br>
**Primary audience:** Editors and production librarians searching an approved studio b-roll/archive catalog

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

Reusable footage is hard to find, but semantic retrieval can overstate visual matches and surface assets whose territory, term, use, or production access does not permit reuse.

**Product promise:** ingest rights-backed private media, derive versioned Google embeddings/metadata, retrieve tenant/rights-filtered candidates through actual ClickHouse MCP, explain structured/visual fit with uncertainty, and record human-selected exports only after a current rights gate.

**Tagline:** Find reusable studio shots without letting similarity outrank rights.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Editor | Searches authorized productions, reviews candidates/rights, previews permitted media, and selects export records. |
| Production librarian | Owns ingest, rights/source metadata, thumbnail policy, labeled query set, and deletion. |
| Rights reviewer | Approves license scope/current rights and resolves ambiguous/expired matches. |
| Gemini/ADK service | Translates intent to allowlisted filters and reviews a small frame set; cannot invent metadata or override rights. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Ingest studio-owned/licensed private footage with source/owner/use/territory/expiry and technical metadata.
- Hash originals, derive non-AI metadata/keyframes and versioned Gemini Embedding 2 vectors with lineage.
- Translate natural-language or authorized-still intent into bounded structured filters/vector search.
- Query actual ClickHouse metadata/vector neighbors through MCP with tenant/access/current-rights prefiltering.
- Review top candidates with Gemini bounded frames, similarity/filter reasons, uncertainty, and no-result behavior.
- Enforce rights again at preview/export and create an immutable human-selected export receipt without timeline mutation.

### 1.4 Explicit non-goals

- No “same shot”/identity/clearance claim from embedding distance or automatic final-timeline placement.
- No unapproved external model/media processing, cross-production leakage, or raw restricted content in results.
- No direct in-memory-only search as integrated ClickHouse proof or arbitrary SQL.
- No expired/missing/territory-mismatch preview beyond explicit thumbnail policy; demo policy allows none.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Use 60 original synthetic/licensed clips up to 30 seconds, H.264 MP4, 1080p maximum, and 50 frozen labeled search queries.
- Embedding dimensions/normalization/distance are pinned after verifying the installed Google API; mismatched dimension/model versions are separate indexes and never mixed. Integrated uses Gemini Embedding 2 as required by the source brief.
- Default retrieval k=20 then rights/access filter is applied in SQL before vector ranking; final review top 5. Target frozen before tuning: recall@10 ≥85%, precision@10 ≥70% on labeled clear queries, with no-result slices separate.
- Expired/missing rights assets return no thumbnail/preview/export. Signed URLs last 5 minutes; export is a local JSON/CSV reference receipt, not media copying.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Librarian ingests authorized media and exact rights/source/access metadata; duplicate hashes return existing asset idempotently.
2. Workers derive FFprobe metadata/keyframes and Google embeddings with model/version/dimension lineage and deletion hooks.
3. Editor submits text or authorized still; ADK produces an allowlisted intent schema with tenant/production/use/territory/date filters.
4. ClickHouse MCP applies access and rights predicates before bounded vector/metadata ranking and stores sanitized query/call evidence.
5. Gemini reviews at most 5 permitted keyframe sets and explains fit/uncertainty only from available structured/visual evidence.
6. Editor sees candidate reasons and current rights; low similarity/missing rights/ambiguous match can produce no suitable cleared match.
7. Selection rechecks asset version, production access, use/territory/date, and thumbnail policy before signed preview.
8. Export rechecks again and writes/read-back a local reference receipt with asset/hash/rights/query/model versions; no timeline mutation.

### 2.2 Lifecycle and transition authority

```text
RIGHTS_VERIFIED_INGEST → METADATA_AND_KEYFRAMES → EMBEDDING_INDEXED → EDITOR_QUERY → INTENT_SCHEMA → CLICKHOUSE_FILTERED_RETRIEVAL → GEMINI_CANDIDATE_REVIEW → (CANDIDATES | NO_SUITABLE_CLEARED_MATCH) → EDITOR_SELECTION → CURRENT_RIGHTS_RECHECK → PREVIEW / EXPORT_RECEIPT; rights/deletion change invalidates indexes and prior selection
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

1. Ingest studio-owned/licensed private footage with source/owner/use/territory/expiry and technical metadata.
2. Hash originals, derive non-AI metadata/keyframes and versioned Gemini Embedding 2 vectors with lineage.
3. Translate natural-language or authorized-still intent into bounded structured filters/vector search.
4. Query actual ClickHouse metadata/vector neighbors through MCP with tenant/access/current-rights prefiltering.
5. Review top candidates with Gemini bounded frames, similarity/filter reasons, uncertainty, and no-result behavior.
6. Enforce rights again at preview/export and create an immutable human-selected export receipt without timeline mutation.

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
| MediaAsset / Derivative | `asset_id`, `production_id`, `sha256`, `owner`, `source`, `technical_metadata`, `storage`; derivative `kind`, `hash`, `parent`, `generator_version` | Original private/immutable; duplicate ingest idempotent; complete derivative lineage and deletion cascade. |
| RightsGrant / AccessPolicy | `asset_id`, `uses`, `territories`, `valid_from/to`, `productions`, `thumbnail_policy`, `source_document`, `reviewer`, `version` | Current explicit rights required at search/preview/export; demo expired/missing yields no media. |
| EmbeddingIndex / Vector | `asset_id`, `model`, `model_version`, `dimension`, `normalized`, `vector`, `source_derivative_hash`, `deleted_at` | One model/dimension per index; no mixed versions; deletion removes vector with asset. |
| SearchIntent / SearchRun | `run_id`, `editor`, `text_or_still`, `filters`, `rights_context`, `k`, `schema_version`; intent model/provenance | Allowlisted filters only; tenant/access/rights context server-derived; query content untrusted. |
| Candidate / FitReview | `run_id`, `asset_id`, `rank`, `distance`, `structured_reasons`, `visual_observation`, `uncertainty`, `rights_version` | Candidate match not identity/clearance; all reasons from filters/keyframes; low confidence remains uncertain. |
| Selection / ExportReceipt | `selection_id`, `run_id`, `asset_id`, `editor`, `rights_recheck`, `preview_grant`; receipt `asset_hash`, `query_id`, `export_hash` | Human selection/current rights/version; signed URL short-lived; local receipt read-back. |
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
assetfinder/
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

Actual ClickHouse vector/metadata retrieval through official MCP is integrated proof. Google Gemini Embedding 2 and Gemini/ADK provide vectors and candidate review after verifying installed API behavior. No other AI provider or in-memory-only integrated path is allowed.

For cinema projects, offline completion and integrated completion are separate statuses: the sandbox proves product behavior, while only the live-smoke evidence can prove the required partner path.

Background processing uses durable jobs with bounded exponential backoff and jitter, a maximum attempt count, lease expiry, and dead-letter visibility. Only idempotent read/analysis jobs retry automatically. External effects with unknown outcomes enter `RECONCILIATION_REQUIRED`; never blind-retry them. The API returns `202` with a job URI for work exceeding the normal request budget.

### 5.4 HTTP API contract

The paths below are the minimum product API. Generate the final schema from FastAPI and generate the TypeScript client. Request bodies use explicit typed fields; examples and all error variants belong in OpenAPI.

| Method and path | Actor | Behavior |
| --- | --- | --- |
| POST `/api/v1/assets` / GET `/api/v1/assets/{id}` | Librarian/Authorized editor | Ingest rights-backed media and read role-scoped metadata/lineage/status. |
| POST `/api/v1/assets/{id}/index` | Librarian | Run keyframe/metadata/embedding pipeline with model/version and deletion-aware job. |
| POST `/api/v1/searches` | Editor | Create bounded text/still intent + ClickHouse MCP retrieval + Gemini review run. |
| GET `/api/v1/searches/{id}/candidates` | Editor | List rights-filtered candidates/reasons/distance/uncertainty or honest no-result. |
| GET `/api/v1/searches/{id}/trace` | Editor/Librarian | Inspect intent filters, MCP query/call, model/embedding versions, and counts/latency. |
| POST `/api/v1/candidates/{id}/selection` | Editor | Select exact candidate/run/version; stale rights/index returns 409. |
| POST `/api/v1/selections/{id}/preview` | Editor | Recheck rights/access and issue 5-minute signed preview only if thumbnail policy allows. |
| POST `/api/v1/selections/{id}/export-receipt` / DELETE `/api/v1/assets/{id}` | Editor/Librarian | Export/read back reference receipt or delete originals/derivatives/vectors/caches. |
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
| propose_search_intent | proposal | ADK converts text/still context to closed filter schema; server adds tenant/rights and rejects unknown fields. |
| clickhouse_search_asset_candidates | MCP read | Parameterized metadata/vector query with access+rights predicates, k≤20, timeout/read-only role. |
| get_candidate_keyframes | read | Returns at most 5 cleared candidate keyframe sets; no restricted signed URLs. |
| propose_candidate_fit | proposal | Gemini returns evidence-bound visual fit/uncertainty; cannot set rights or invent camera/lens metadata. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

At ingest, store `asset_id`, production/access, owner/rights version, technical metadata, original hash, derivative hashes, embedding model/version/dimension, and normalized `Array(Float32)` vector in ClickHouse. Keep vectors for different model versions/dimensions in separate tables. The MCP query is a pinned parameterized template: tenant/production ACL and `valid_from <= proposed_use_date < valid_to`, intended use and territory inclusion are predicates before `cosineDistance` ranking with `LIMIT 20`. No string concatenation of natural-language input into SQL.

Structured filters (duration/frame rate/resolution/audio/declared shot tags) produce explicit reasons; cosine distance is shown as similarity evidence, not identity or rights. Gemini reviews top 5 only and cannot add structured attributes. If no candidate meets the frozen distance/rights/quality threshold or review is ambiguous, return `NO_SUITABLE_CLEARED_MATCH`. Preview/export repeats rights checks against current primary database, not cached search state. Evaluation uses labeled relevant assets per query: recall@10 = retrieved relevant/ground-truth relevant; precision@10 = retrieved relevant/retrieved count, with no-result and rights-filtered slices reported separately.

| Policy area | Normative rule |
| --- | --- |
| Rights before media | ACL/rights filter retrieval and current primary-store recheck gates every preview/export; semantic score cannot override. |
| Ingest/lineage/deletion | Original hash/owner/rights/derivative/embedding lineage mandatory; duplicate idempotent and deletion cascades to vectors/caches/URLs. |
| Grounded fit | No invented lens/camera/identity/same-shot claims; low similarity or ambiguous visual match yields no suitable cleared match. |
| Data protection | Private originals/short signed URLs/server-side credentials; logs IDs/hashes not raw captions/URLs; metadata injection cannot change ACL/filters. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** An editor-focused visual library with forest-green accents, disciplined keyframe grids, rights information adjacent to every result, and a useful no-result state rather than forced similarity. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #2f6b4f; --color-accent-ink: #ffffff;
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
| /assets | Asset library | Authorized catalog, technical/rights/index status, expiry, and librarian ingest. |
| /assets/{id}/ingest | Ingest and rights | Private media/source/owner/rights/use/territory/expiry, duplicate/probe state, and access policy. |
| /search | Shot search | Natural-language/authorized-still input, intended use/territory/date, structured filters, and search caps. |
| /searches/{id} | Candidate results | Keyframe grid/list, match reasons/similarity, current rights, uncertainty, and no-suitable-match state. |
| /candidates/{id} | Candidate review | Permitted preview/keyframes, metadata/rights lineage, fit observations, and human selection. |
| /selections/{id} | Preview and export | Fresh rights recheck, 5-minute preview, local JSON/CSV receipt, and no-timeline-mutation note. |
| /librarian/evaluation | Retrieval and index health | Labeled queries, recall/precision/no-result slices, embedding versions, MCP traces, and deletion status. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **AssetCard:** keyframe only when permitted, title/duration/technical tags, rights state/expiry, and Candidate match label.
- **RightsPanel:** intended use/territory/date vs grant, reviewer/version/source, and exact block reason adjacent to preview/export.
- **MatchExplanation:** structured filters and similarity separated from Gemini visual observations; unsupported attributes absent.
- **SearchIntentSummary:** interpreted filters with editable controls and server-enforced context; user can correct intent before rerunning.
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
- **Privacy:** Private originals follow librarian policy; demo default 30 days. Embeddings/keyframes inherit asset deletion and are removed in the same deletion manifest. Signed URLs expire in 5 minutes; search logs retain IDs/hashes and redacted intent for 30 days, not raw captions/private URLs.
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

Commit 60 original/cleared clips, 50 independently labeled natural-language/still queries with relevant/no-result/rights-filtered cases, exact/near duplicates, expired/territory/use-mismatch licenses, low-similarity/ambiguous visuals, captions/metadata injection, cross-production canaries, embedding-version mismatch, and deletion fixtures. Freeze relevance labels and AF thresholds before any tuning.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Retrieval quality | On frozen clear-query set recall@10 ≥85% and precision@10 ≥70%; also report per-query recall/precision, rights-filtered and no-result behavior. |
| Rights/security | Zero expired/missing/mismatched/cross-production previews/exports or ACL bypass; all metadata injection and arbitrary SQL attempts denied. |
| Ingest/deletion | 100% duplicate/idempotency/lineage/model-dimension tests; deletion removes original/derivatives/vectors/caches and revokes URLs. |
| Grounding/uncertainty | 100% candidates expose structured+similarity reasons and rights; zero invented camera/lens/same-shot/cleared claims in adversarial outputs. |
| Runtime/reproducibility | Integrated actual ClickHouse MCP candidate query required; offline scripted Gemini path clean-clone reproducible and labeled. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Ingest a licensed clip and inspect original/derivative/rights/embedding lineage and idempotent duplicate handling.
2. Run a natural-language search with intended use/territory/date and inspect editable intent filters.
3. Open actual ClickHouse MCP trace and candidate match explanations; distinguish structured filters, similarity, and Gemini observations.
4. Show an expired-license near-match produces no preview/export and an ambiguous query can return no suitable cleared match.
5. Select a cleared candidate, recheck rights, preview via short-lived URL, and export/read back a local reference receipt.
6. Delete a separate asset and verify media/derivatives/vectors/caches are gone and injection cannot cross productions.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Rights/asset/private storage schemas, FFprobe/keyframe ingest, duplicate/lineage/deletion tests.
2. ClickHouse vector/metadata DDL, MCP filtered query templates, ACL/rights prefiltering, and retrieval evaluator.
3. Google embeddings + ADK intent/fit review with scripted path, versioned indexes, and injection tests.
4. Search/result/candidate UI, current-rights preview/export receipts, signed URLs, and audit.
5. 50-query frozen eval, accessibility/performance/security, integrated runtime, deployment/rollback, and demo.

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
| AF-01 | missing/expired/territory-mismatched license prevents preview/export beyond the approved thumbnail policy; no semantic score can override it. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| AF-02 | asset hash, derivative lineage, owner, license source, and model/embedding version are stored; duplicate ingest is idempotent. | Concurrency and integration tests deliver exact duplicates, legitimate near-duplicates, reordered events, and retries; assert one intended effect and no lost positive control. | Core |
| AF-03 | active MCP query retrieves candidates from the actual ClickHouse cluster; direct in-memory search is not the only path. | `make live-smoke` against the required isolated partner/runtime plus offline contract tests; retain sanitized provider/MCP/hosting evidence and never substitute fixtures. | Integration |
| AF-04 | labeled query set reports recall@k, precision@k, rights-filtered results, and no-result behavior. Exact metric thresholds are set with the librarian before model tuning and frozen during evaluation. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| AF-05 | every candidate shows why it matched (structured filters and similarity) and its rights metadata; the agent may not invent camera/lens attributes. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| AF-06 | low similarity, missing rights, or ambiguous visual match returns “no suitable cleared match” rather than forcing a result. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| AF-07 | prompt text in captions/metadata cannot change data filters, reveal another production, or bypass access controls; DB account is read-only. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| AF-08 | media URLs are signed and short-lived; previews and embeddings follow per-asset retention/deletion; logs contain IDs, not raw captions or URLs. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| AF-09 | use original/cleared footage only; show a natural-language request, rights-filtered candidate search, one rejected expired license, and a human-selected export record. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| AF-10 | `make setup`, `make verify`, and `make demo-e2e` work without cloud credentials using a compact synthetic asset set and scripted Gemini adapter. | Run the seeded browser journey, retain the Playwright trace and short recording, and verify the evidence/refusal shown against API and audit state. | Core |

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

- Confirm allowed asset classes, licensing source of truth, production ACLs, preview/thumbnail policy, and retention/deletion guarantees.
- Have librarian freeze relevance labels/metric thresholds before tuning and validate no-result usefulness with editors.
- Configure isolated ClickHouse/MCP/Google scopes, private object storage, model-media approval, and short-lived URL operations.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for AssetFinder.**
