# SecondUnit Match — implementation-ready specification

**Project ID:** `secondunit-match`<br>
**Track / family:** Agentic Cinema / IBM alternate 02<br>
**Status:** Normative build specification; no implementation is claimed<br>
**Specification date:** 2026-10-24<br>
**Source brief:** [02-secondunit-match.md](../02-secondunit-match.md) (historical context only)<br>
**Primary audience:** Assistant editors reconciling second-unit pickups with approved principal-unit scenes

> **How to use this document:** this file is the sole normative product, architecture, UI, and verification input for a standalone build. An implementation agent may make routine library-version choices, pin them in lockfiles, and record deviations in `docs/decisions/`; it must not relax scope, authority boundaries, acceptance criteria, or hard gates. All demo data is synthetic or explicitly licensed. Build the offline vertical slice first. Never represent a simulated provider, integration, result, or deployment as live.

## 1. Product contract

### 1.1 Problem and promised outcome

Pickup footage captured later can differ in props, wardrobe, lighting, direction, framing, or sound. Editors need bounded evidence before the crew/location disappears, without an automated “usable” verdict.

**Product promise:** probe and align an approved reference and pickup, generate exact frame/crop discrepancy candidates for Gemini review, and export only an editor-approved CMX3600/CSV note with valid source timecodes.

**Tagline:** Evidence cards for deciding whether pickup footage can intercut.

The problem and impact remain hypotheses until partner research validates them. The build can prove functional correctness on its committed corpus; it cannot prove user impact, legal/compliance correctness, safety in the real world, or production readiness from fixtures alone.

### 1.2 Actors and authorization

| Actor | Allowed authority |
| --- | --- |
| Assistant editor | Creates scene comparisons, reviews candidates, chooses dispositions, and approves exports. |
| Editor | Owns reference hierarchy, final `acceptable/fix_in_edit/reshoot_consideration/uncertain` decisions, and EDL approval. |
| Media manager | Uploads authorized reference/pickup media and slate/continuity notes; no verdict authority. |
| Gemini/ADK service | Adjudicates bounded evidence crops/audio context; no edit/render/publish tools. |

Additional authorization rules:

- Authorization is enforced in API/application services, never only by hiding UI. Every query includes tenant and actor scope. Another tenant's resource returns `404`; an authenticated but unauthorized action on a visible resource returns `403`.
- A demo role switcher is allowed only when `DEMO_MODE=true`, is visibly labeled, and is absent from deployed authentication. Production uses OIDC Authorization Code + PKCE or an equivalent managed identity provider.
- The agent is a constrained service principal, not a superuser. Human roles retain approval, publication, export, external-effect, and policy-administration authority as specified below.

### 1.3 MVP scope — required, not optional

- Ingest authorized reference/pickup clips, slate metadata, and scene continuity notes with immutable hashes.
- Validate codec/frame rate/duration/audio/timecode using FFprobe and reject malformed/out-of-scope media.
- Generate deterministic aligned frame pairs/crops and a versioned sampling plan.
- Use Gemini to assess props/wardrobe/lighting/screen direction/framing/sound candidates with uncertainty.
- Present side-by-side review and editor dispositions without modifying source footage.
- Export/reparse editor-approved CMX3600 EDL and CSV notes with source IDs, in-range timecodes, and evidence hashes.

### 1.4 Explicit non-goals

- No synthesized substitute footage, media repair, auto-edit/render, or autonomous usability/reshoot decision.
- No non-Google AI detectors, arbitrary cloud model, or unlicensed footage.
- No confidence-only approval or overwritten source media/scene notes.
- No Confluent dependency in v1; it remains unnecessary optional future scope.

### 1.5 Fixed product and delivery decisions

These decisions replace unresolved questions for the standalone synthetic build. A real partner may change them only through a versioned decision record and a new evaluation baseline.

- Demo uses original synthetic 25 fps non-drop H.264/AAC MP4 clips up to 90 seconds/500 MB and one PCM audio channel pair.
- Export profile is CMX3600 at 25 fps plus UTF-8 CSV; source timecodes are non-drop and record durations never exceed probed media.
- Sampling plan selects slate anchor plus 1 fps over the overlapping clip window, maximum 30 candidate pairs; deterministic crop/color controls are versioned.
- Only editor-approved candidates enter export; uncertain items appear in an explicit unresolved appendix rather than being omitted.
- Deliver a standalone monorepo with one deployable web application, one API/worker codebase, pinned lockfiles, seeded fixtures, and no dependency on another project in this portfolio.
- Default to one tenant and one synthetic demo workspace, while enforcing tenant keys from day one. Real-user pilots, paid spend, external contact, and production data are outside default setup.
- Store timestamps in UTC and display them in the workspace IANA timezone with the zone visible. Persist decimal money in integer minor units and rates/quantities as exact decimals where applicable.
- Use English UI copy unless this specification explicitly requires another language. All user-visible terminology must distinguish `verified`, `proposed`, `unknown`, `held`, and `rejected`; never use color alone.

## 2. End-to-end workflows and state

### 2.1 Primary happy-path journey

1. Editor creates/selects the approved scene reference and continuity-note version.
2. Media manager uploads pickup/slate; intake verifies rights, hashes, media metadata, and source immutability.
3. The deterministic aligner computes overlap, frame pairs, crop candidates, and audio/timecode evidence.
4. Gemini returns structured observations per candidate; the service validates source/timecode/category and retains uncertainty.
5. Editor compares frames/audio and assigns dispositions; model confidence cannot mark the take usable.
6. Changed media, slate, notes, or sampling plan invalidates the previous review and displays a diff.
7. Editor approves exact candidate/disposition/export payload; exporter validates source IDs, timecodes, and record mapping.
8. The system reparses EDL/CSV, compares events/hashes, and provides an editor-ready note with unresolved appendix.

### 2.2 Lifecycle and transition authority

```text
SCENE_REFERENCE → PICKUP_INTAKE → MEDIA_PROBE → ALIGNMENT → GEMINI_REVIEW → EDITOR_REVIEW → (ACCEPTABLE | FIX_IN_EDIT | RESHOOT_CONSIDERATION | UNCERTAIN) → EXPORT_APPROVAL → EDL_CSV_EXPORTED; malformed/rights failure → REJECTED_INTAKE; changed media/notes → STALE_REVIEW
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

1. Ingest authorized reference/pickup clips, slate metadata, and scene continuity notes with immutable hashes.
2. Validate codec/frame rate/duration/audio/timecode using FFprobe and reject malformed/out-of-scope media.
3. Generate deterministic aligned frame pairs/crops and a versioned sampling plan.
4. Use Gemini to assess props/wardrobe/lighting/screen direction/framing/sound candidates with uncertainty.
5. Present side-by-side review and editor dispositions without modifying source footage.
6. Export/reparse editor-approved CMX3600 EDL and CSV notes with source IDs, in-range timecodes, and evidence hashes.

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
| Scene / ReferenceClip | `scene_id`, `production_id`, `reference_clip_id`, `continuity_note_version`, `reference_hierarchy` | One active approved reference hierarchy; changes version the comparison. |
| Clip / Slate / MediaProbe | `clip_id`, `sha256`, `kind`, `rights_id`; slate `scene`, `take`, `timecode`; probe `codec`, `fps`, `duration`, `audio`, `timecode_bounds` | Original immutable; exact 25 fps demo profile; malformed/unsupported/rights-missing rejected. |
| SamplingPlan / FramePair | `clip_ids`, `overlap`, `frame_indexes`, `crop_boxes`, `algorithm_version`, `manifest_hash` | Canonical deterministic plan; exact in-bounds reference/pickup mapping and derivative lineage. |
| MismatchCandidate | `candidate_id`, `frame_pair_id`, `category`, `observation`, `verdict`, `uncertainty`, `model_version` | Allowed categories; absent evidence uncertain; model cannot set editor disposition. |
| EditorDisposition | `candidate_id`, `decision`, `note`, `editor_id`, `clip_versions`, `created_at` | Enum four states; authenticated editor; appended when inputs change. |
| EditNoteExport / ExportEvent | `export_id`, `format`, `source_clip_ids`, `events`, `unresolved`, `approval_hash`, `sha256`, `reparse_status` | CMX/CSV events valid/in-range; original media untouched; exact approved digest. |
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
secondunit-match/
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

Google ADK + Gemini on Vertex AI performs live candidate adjudication; classical FFmpeg/CV is non-AI processing. IBM Bob development provenance is mandatory for integrated track evidence. No Confluent or generative video dependency is required.

For cinema projects, offline completion and integrated completion are separate statuses: the sandbox proves product behavior, while only the live-smoke evidence can prove the required partner path.

Background processing uses durable jobs with bounded exponential backoff and jitter, a maximum attempt count, lease expiry, and dead-letter visibility. Only idempotent read/analysis jobs retry automatically. External effects with unknown outcomes enter `RECONCILIATION_REQUIRED`; never blind-retry them. The API returns `202` with a job URI for work exceeding the normal request budget.

### 5.4 HTTP API contract

The paths below are the minimum product API. Generate the final schema from FastAPI and generate the TypeScript client. Request bodies use explicit typed fields; examples and all error variants belong in OpenAPI.

| Method and path | Actor | Behavior |
| --- | --- | --- |
| POST `/api/v1/scenes` / POST `/api/v1/scenes/{id}/clips` | Editor/Media manager | Create reference context and ingest rights-checked clips/slates. |
| GET `/api/v1/clips/{id}/probe` | Editor | Return FFprobe/timecode/audio metadata and intake errors. |
| POST `/api/v1/comparisons` | Editor | Run deterministic alignment + Gemini candidates for exact reference/pickup hashes. |
| GET `/api/v1/comparisons/{id}/candidates` | Editor | List evidence pairs/categories/uncertainty/disposition status. |
| GET `/api/v1/candidates/{id}/evidence` | Editor | Return signed short-lived frame/clip/audio derivatives and source timecodes. |
| POST `/api/v1/candidates/{id}/disposition` | Editor | Record versioned human decision and note; stale media returns 409. |
| POST `/api/v1/comparisons/{id}/export-approval` | Editor | Approve exact dispositions, unresolved appendix, format, and local-download destination. |
| POST `/api/v1/comparisons/{id}/exports` / GET `/api/v1/exports/{id}/reparse` | Editor | Generate/reparse CMX3600+CSV and compare events/timecodes/hash. |
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
| get_scene_continuity_context | read | Returns current approved scene/reference/note version with no unrelated production data. |
| get_aligned_evidence | read | Returns bounded frame/crop/audio derivative IDs, source hashes, and timecodes. |
| propose_mismatch_observation | proposal | Gemini returns allowed category/observation/uncertainty tied to evidence IDs. |
| validate_editor_note | proposal | Checks editor note/source/timecode completeness; cannot approve or export. |

There is deliberately no generic `execute`, `sql`, `http`, `send`, `delete`, `publish`, `approve`, `advance`, or file-system tool. Unknown tools and extra JSON properties are denied. If a human command is available in the product, expose it only through the authenticated application API—not as an ambient agent capability.

### 6.2 Agent execution contract

1. Build a minimal context from authorized records. Treat file text, OCR, captions, logs, web results, metadata, and provider output as untrusted data, never instructions.
2. Ask the model for a bounded structured result: `{"schema_version":"1", "status":"proposal|uncertain|refused", "observations":[], "source_refs":[], "uncertainties":[]}`. Add only project fields required by the tools above.
3. Validate schema, source references, allowed enum values, maximum observations, and tenant/resource binding. Recompute material facts in deterministic code. A model confidence value never grants authority.
4. Persist the proposal with provider/model/prompt schema/tool versions, sanitized request ID, latency, token/cost metadata where available, and outcome. Do not log raw sensitive prompts.
5. On timeout/malformed content/outage, mark the run incomplete and preserve a manual route. Never substitute a cached success from different input hashes.

The scripted provider must execute the same agent loop, schema validators, tool guards, application state machine, and persistence as the live provider. It may script model responses; it may not bypass the product path or directly write expected final state.

## 7. Deterministic domain and decision policy

FFprobe establishes a common 25 fps non-drop timeline. Compute overlap from source timecode and duration; reject empty overlap. Sample the slate anchor then 1 fps within overlap, convert frame index with `timecode = clip_start + frame_index/fps`, and assert every index/timecode is in bounds. Produce crop pairs with the fixed alignment/version and retain color/exposure/crop control labels independently of Gemini.

For CMX3600 export, each approved event contains reel/source ID, clip kind, source in/out, record in/out, and a note reference. Validate nondecreasing source in<out, duration equality within one frame, legal reel characters, and source bounds. Re-parse the generated EDL with an independent parser and compare canonical events to the approved manifest; CSV carries candidate IDs/hashes/uncertain appendix.

| Policy area | Normative rule |
| --- | --- |
| Media/rights gate | Size/MIME/codec/fps/duration/audio/timecode/license/consent validated before derivatives or model calls; source never overwritten. |
| Artistic controls | Camera motion, grade, crop, exposure, and framing variations are separate eval slices; model observations remain candidates. |
| Editor authority | Only editor dispositions and exact export approval create notes; model cannot alter scene notes, mark usable, render, or publish. |
| Provenance/replay | Every observation/export event links both clips, frame/timecode, crop/sampling/model/disposition versions; stale inputs invalidate review. |

Universal precedence: authentication/tenant scope → input/media validity → consent/rights → hard safety and state guardrails → deterministic calculation/matching → model proposal → human approval where required → idempotent adapter effect → read-back/audit. A later stage cannot repair or override a failed earlier gate.

## 8. UI and UX build plan

### 8.1 Experience direction and design tokens

**Design character:** An assistant-editor suite with neutral graphite, electric-blue focus states, precise timecode/readout panels, and honest side-by-side evidence instead of automated quality scores. The interface should feel calm, exact, and evidence-led rather than like a generic chat dashboard. The agent is presented as an assistant inside a workflow, not as the home page.

Use these base tokens in `:root`, with semantic aliases rather than hard-coded component colors:

```css
:root {
  --color-bg: #f7f8fa; --color-surface: #ffffff; --color-ink: #17202a;
  --color-muted: #5c6673; --color-border: #d7dde5;
  --color-accent: #315d9e; --color-accent-ink: #ffffff;
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
| /scenes | Scene references | Approved reference hierarchy, pickup status, rights/probe state, and open review counts. |
| /scenes/{id}/intake | Pickup intake | Reference/pickup/slate upload, rights, media probe, continuity-note version, and validation. |
| /comparisons/{id}/setup | Alignment setup | Overlap/timecode/sampling plan, candidate cap, algorithm version, and run action. |
| /comparisons/{id}/review | Mismatch review | Category/status filters, evidence pairs, uncertainty, and editor progress. |
| /candidates/{id} | Evidence comparison | Side-by-side/overlay frames, audio playback/transcript context, exact timecodes, and four dispositions. |
| /comparisons/{id}/export | Editor export | Approved/unresolved lists, EDL/CSV preview, stale diff, exact approval, and reparse result. |
| /clips/{id}/lineage | Media lineage | Original/derivatives, hashes, rights, model runs, and export references. |

Every route has loading skeletons that preserve layout, an actionable error state, an empty state, offline/stale indicators where applicable, and a not-found/forbidden state. Deep links restore filters and selected record. Destructive/approval dialogs show the exact consequences and digest-relevant summary; they are not generic “Are you sure?” prompts.

### 8.3 Component and interaction specification

- **SyncClipCompare:** play/pause/frame-step/timecode controls accessible by keyboard; overlay has slider plus numeric input and textual differences.
- **TimecodeRange:** source in/out and duration with 25 fps/non-drop labels and in-range validation.
- **DispositionMenu:** four explicit editor choices with note and consequence; none selected by default from model output.
- **EDLPreview:** monospace event list plus semantic table, unresolved appendix, source IDs, and independent reparse status.
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
- **Privacy:** Source/pickup clips and derived frames delete 30 days after editor export unless the production selects shorter retention. Signed preview URLs expire in 10 minutes. Deletion covers model payloads/caches; exported notes retain hashes and role-label metadata only.
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

Commit at least 40 labeled original/licensed reference/pickup pairs with true prop/wardrobe/lighting/direction/framing/sound mismatches and camera-motion/grade/crop/exposure artistic controls. Include uncertain/no-overlap/malformed media, injected slate/transcript/filename, expired rights, stale review, and EDL round-trip golden files with independent editor labels.

Every fixture has a stable ID, license/origin record, expected label independent of implementation output, and a manifest hash. Do not label cases using the same model being evaluated. Keep raw personal/copyrighted material out of Git, screenshots, logs, and prompts.

### 11.2 Evaluation contract

`make eval` must regenerate `docs/eval/report.json` and `report.html` from committed cases and record source revision, corpus hash, code/policy/model versions, seed, run time, and lane (`scripted` or `live`). It reports per-case outcomes as well as aggregates; missing cases, parse failures, and abstentions remain visible in denominators.

| Metric / slice | Required report and completion threshold |
| --- | --- |
| Alignment/repeatability | 100% identical frame-pair manifests on repeat; all references/timecodes/hashes valid; no-overlap cases held. |
| Mismatch quality | On clear labeled subset target recall ≥90% and precision ≥85%; report per-category false alarms, abstention, and editor overrides. |
| Export correctness | 100% approved EDL/CSV events reparse equal to manifest; zero invalid source IDs/out-of-range timecodes or silent unresolved omissions. |
| Authority/security | Zero model self-approval/media mutation and zero slate-injection tool/data effects; rights gates always enforced. |
| Runtime truth | Scripted and live lanes separately evidenced; integrated lane retains actual Gemini/ADK and IBM Bob development artifacts. |

Report denominators and confidence intervals/trial counts for stochastic runs. Never convert “zero failures on this corpus” into a universal safety claim. A failing safety case blocks completion even if the aggregate score is high. Threshold changes require a new baseline decision record and retain old results.

### 11.3 Scripted end-to-end demo

1. Ingest approved reference and pickup, inspect FFprobe/rights, and run the fixed alignment plan.
2. Open one genuine prop mismatch and one color-grade artistic control; compare exact frame/timecode evidence.
3. Mark one uncertain case and prove it remains in the unresolved appendix rather than becoming usable.
4. Editor assigns dispositions and approves an EDL/CSV; a media change invalidates the old approval.
5. Reapprove and show independent EDL/CSV reparse equality with source hashes.
6. Show injected slate containment and separate scripted vs actual Gemini/ADK + Bob provenance evidence.

`make demo-e2e` runs this journey through the actual browser/API/domain/agent/sandbox adapters with no external contact or paid call. Reset produces the same initial manifest. The final screen links evidence, audit, and generated artifacts. Record a maximum three-minute demo for cinema projects and a concise equivalent for other projects; label every synthetic, simulated, live, and unverified element.

## 12. Implementation sequence and ownership

Build in vertical slices; each slice leaves `main` releasable and adds tests with the behavior, not after it.

1. Media/rights/slate intake, FFprobe validation, immutable originals, and test clips.
2. Deterministic overlap/alignment/crop/sampling manifests and export timecode utilities.
3. ADK/Gemini bounded review, scripted adapter, candidate schemas, and injection/failure tests.
4. Editor comparison/disposition UI, stale approval, CMX3600/CSV export/reparse, and audit.
5. 40-pair eval, accessible media UI, performance/recovery, Bob provenance, deployment/rollback, and demo.

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
| SUM-01 | file size, MIME, codec, duration, and license/consent are validated; malformed and unsupported media fail with a clear state. | API authorization/privacy integration tests with two tenants/actors and canary values; inspect model prompts, responses, exports, caches, and logs. | Core |
| SUM-02 | every mismatch card links to exact reference and pickup frames/timecodes and hashes; absent evidence yields `uncertain`. | Schema and integration tests resolve every reference to immutable source content; mutate/delete a reference and verify a visible hold, never a pass. | Core |
| SUM-03 | camera motion, color grade, crop, and exposure changes are included as negative controls; report false-alarm rate per category. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SUM-04 | model cannot mark a take usable, alter scene notes, or publish an EDL; editor action required and logged. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SUM-05 | malicious text in slates/transcripts cannot issue tools, retrieve other productions, or change verdict policy. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SUM-06 | identical inputs reproduce the same extracted frame pairs; model adjudication record is versioned and replayable. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |
| SUM-07 | generated EDL references valid source IDs and in-range timecodes; import/reparse round-trip test succeeds. | Schema and integration tests resolve every reference to immutable source content; mutate/delete a reference and verify a visible hold, never a pass. | Core |
| SUM-08 | at least 40 labeled reference/pickup pairs across true mismatches and artistic variations; report recall, precision, abstention, and editor overrides. Retain all misses. | `make eval`; inspect the versioned JSON/HTML report, recompute three rows independently, and retain every miss and its denominator. | Core |
| SUM-09 | demo proves active Gemini/ADK execution and IBM Bob provenance; credentials/cost must be capped and not required by default verification. | `make live-smoke` against the required isolated partner/runtime plus offline contract tests; retain sanitized provider/MCP/hosting evidence and never substitute fixtures. | Integration |
| SUM-10 | show one defect caught, one artistic difference not overcalled, one `uncertain` case, and an editor-approved EDL. | Domain, API, and browser integration tests exercise both the positive control and the prohibited/failure path; retain JUnit results and relevant audit/trace evidence. | Core |

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

- Secure production media/likeness permissions, reference hierarchy, retention, and assistant-editor/editor roles.
- Confirm the production’s exact EDL flavor/frame-rate/timecode conventions and import workflow.
- Recheck current IBM track requirements and Bob evidence format before claiming qualification; the historical contest deadline has passed.

Any scope, policy, threshold, source, role, or external-effect change requires a versioned ADR, migration/compatibility analysis, updated acceptance matrix, and regenerated evaluation. Preserve previous reports; never delete or relabel failing cases to make a score improve.

---

**End of normative specification for SecondUnit Match.**
