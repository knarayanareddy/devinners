# End-to-end repository review

**Review date:** 2026-10-24<br>
**Reviewed baseline:** `d249cdb7b1a0635f86c363dfc8f7a09bcaa6760f` (`main` at session start)<br>
**Working branch:** `arena/ad441810-devinners`<br>
**Repository type:** documentation-only product-specification portfolio<br>
**Detailed-spec baseline:** [Project specification index](../specs/README.md)

## 1. Executive summary

The original repository was a compact, thoughtful **concept portfolio**, not a software repository. It contained 25 product briefs with strong boundaries around human authority, evidence, privacy, failure handling, and evaluation. It did not contain application source, dependency manifests, tests, CI, deployment configuration, or runnable demos. Therefore, this review could assess documentation quality and implementation readiness, but could not execute or assess product runtime behavior.

The principal gap was implementation specificity. The 25 briefs averaged about 41 lines and provided useful problem statements and acceptance headlines, but not enough concrete data models, API behavior, algorithms, screen designs, failure semantics, operational budgets, or completion scoring for an agent to build autonomously without making major undisclosed product decisions.

The remediation adds **25 standalone, project-specific build specifications** totaling **13,117 lines**. Each is approximately 520 lines and preserves every historical acceptance statement. The pack now contains:

- 25 self-contained `SPEC.md` documents in respective project folders.
- 258 inherited acceptance criteria, represented with verification methods and unique detailed-spec IDs.
- Concrete actors, scope/non-goals, fixed synthetic-demo decisions, workflows, and state machines.
- Project aggregates, invariants, persistence rules, architecture, repository layout, and API contracts.
- Agent/tool boundaries, deterministic algorithms, failure precedence, and integration lanes.
- Screen-by-screen UI plans, component behavior, design tokens, responsive states, and WCAG 2.2 AA requirements.
- Security/privacy/retention, performance/operations, seed/eval/demo plans, build slices, and handoff requirements.
- A 100-point rubric plus non-compensable hard gates for every project.
- A root/portfolio index and a standard-library validator for structure, links, and acceptance traceability.

**Current maturity remains `specified`, not implemented.** The documentation can now guide complete standalone builds, but no working software, live integration, user impact, production readiness, legal/compliance correctness, or contest qualification is claimed.

## 2. Review scope and method

### 2.1 What was inspected

- All 27 tracked files at the starting revision, all of which were Markdown.
- Both portfolio indexes and all 25 project briefs.
- Product promises, actors, scope, non-goals, workflows, domain hints, agent boundaries, acceptance criteria, evaluation plans, delivery slices, and open questions.
- Git history/branch/remotes and repository-level file inventory.
- Cross-project acceptance-ID uniqueness and documentation links.
- Suitability of each brief as a standalone implementation input.

### 2.2 What could not be inspected or executed

There was no product code, package manifest, test suite, database schema, deployment, or runtime to assess. Accordingly, this review makes no statement about application correctness, vulnerability posture, accessibility of an implemented interface, actual performance, provider behavior, or operational resilience.

External contest rules, winner pages, partner SDKs, and live integrations were **not independently revalidated during this review**. The historical Agentic Cinema source index remains provenance. Current official documentation and installed SDK signatures must be checked during implementation before making integration or track-qualification claims.

### 2.3 Baseline measurements

| Measurement | Original repository |
| --- | ---: |
| Tracked files | 27 |
| Non-Markdown tracked files | 0 |
| Independent agent project briefs | 10 |
| Agentic Cinema project briefs | 15 |
| Total project briefs | 25 |
| Project-brief lines, excluding two indexes | 1,017 |
| Median project-brief length | 39 lines |
| Shortest / longest brief | 30 / 72 lines |
| Historical acceptance statements | 258 |
| Unique historical IDs across projects | 248 |
| Runnable product manifests/tests/implementations | 0 |

The 10-ID difference was caused by MixWatch and MuseumWorld both using `MW-01` through `MW-10`.

## 3. Original documentation strengths

The remediation deliberately preserves these strengths:

1. **Bounded authority.** The briefs consistently distinguish model proposals from deterministic calculations, authorization, policy, state transitions, and external effects.
2. **Human accountability.** Consequential publication, approval, contact, schedule, clearance, and state changes remain with named human roles.
3. **Evidence orientation.** Source spans, media hashes, timecodes, rule versions, tool/query identities, and audit history are recurring design elements.
4. **Failure honesty.** Unknown, timeout, stale data, malformed output, missing evidence, and provider failure generally fail into visible review rather than false success.
5. **Explicit non-goals.** The briefs avoid dangerous scope expansion into legal/medical claims, emergency response, automatic publication, payments, or uncontrolled media mutation.
6. **Adversarial and negative cases.** Prompt injection, replay, stale approval, duplicate delivery, cross-user access, near-matches, and positive controls are common requirements.
7. **Evaluation humility.** The source documents repeatedly require denominators, misses, abstentions, false positives/negatives, and no unsupported field-impact claims.
8. **Distinct product concepts.** The 10 independent and 15 cinema briefs represent separate standalone workflows, not a disguised single monolithic application.

These are good product-safety foundations. The issue was not lack of intent; it was the distance between intent and executable specification.

## 4. Findings and remediation

| ID | Severity | Finding at baseline | Remediation in this change | Status |
| --- | --- | --- | --- | --- |
| R-01 | Informational | No product implementation existed, so end-to-end runtime review was impossible. | Clearly label every document/index/review as specification-only and define separate offline, integrated, and pilot completion labels. | **Bounded / disclosed** |
| R-02 | High | Briefs were too short to serve as sole autonomous-build inputs; agents would need to invent architecture and product behavior. | Add 25 self-contained specifications with fixed defaults, data/invariants, APIs, algorithms, jobs, errors, state, and delivery artifacts. | **Addressed in docs** |
| R-03 | High | UI planning was mostly one accessibility criterion, without routes, screen contents, components, responsive composition, or interaction states. | Add project-specific visual direction, tokens, 6–7 routes per product, components, mobile/desktop behavior, state matrix, and accessibility/content rules. | **Addressed in docs** |
| R-04 | High | Domain entities were illustrative rather than implementation contracts; endpoint, concurrency, idempotency, migration, and persistence behavior was absent. | Add required fields/invariants, aggregate versions, actor-scoped APIs, error semantics, idempotency, approval digests, outbox/jobs, and storage rules. | **Addressed in docs** |
| R-05 | Medium | Open questions and unspecified partner choices could stall an implementation agent or produce inconsistent assumptions. | Resolve the synthetic standalone build with conservative fixed decisions; move real partner choices into explicit pre-pilot gates. | **Addressed for demo; pilot remains gated** |
| R-06 | Medium | `MW-01`–`MW-10` collided between MixWatch and MuseumWorld, weakening portfolio-wide traceability. | Preserve MixWatch `MW-*`; migrate detailed MuseumWorld criteria to `MUS-*` with an explicit source mapping. | **Addressed** |
| R-07 | Medium | No root README, unified portfolio navigation, or explanation of documentation maturity existed. | Add root README and a 25-project index with scope, usage, completion labels, and project focus. | **Addressed** |
| R-08 | Medium | Offline/scripted evidence and live partner evidence could be conflated; the historical cinema contest had already closed. | Require explicit scripted/simulated/live labels, separate offline/integrated scores, actual provider/MCP/hosting proof, and no contest-qualification claim. | **Addressed in docs; external proof pending builds** |
| R-09 | Medium | Performance, capacity, accessibility verification, backup/restore, rollback, observability, retention deletion, and handoff were not uniformly specified. | Add measurable non-functional budgets, telemetry/runbook requirements, deletion manifests, recovery drills, and handoff checklists to every spec. | **Addressed in docs** |
| R-10 | Medium | No automated check protected acceptance coverage, section completeness, links, or ID uniqueness. | Add `make verify-docs` and a standard-library validator covering 25 specs, 258 criteria, links, required sections, UI/eval/rubric content, and placeholders. | **Addressed for docs** |
| R-11 | Low / owner decision | No repository-wide license or contribution/governance policy was present. | Not chosen unilaterally. Each future implementation must include an appropriate license; the repository owner should select documentation licensing before external reuse. | **Open owner decision** |

“Addressed in docs” means the implementation input now specifies the requirement. It does not mean any product has implemented or passed it.

## 5. Detailed-specification architecture

Every `SPEC.md` follows the same 15-part contract so an implementation agent can navigate any project predictably:

| Section | Implementation question answered |
| --- | --- |
| 1. Product contract | Who is it for, what exactly is in/out, which fixed assumptions avoid product ambiguity? |
| 2. Workflows and state | What happens end to end, which transitions are legal, and how do failures/stale versions behave? |
| 3. Functional requirements | Which capabilities and cross-cutting behaviors are binding? |
| 4. Domain and persistence | Which records/fields/invariants, transactions, migrations, files, hashes, and versions are required? |
| 5. Technical architecture | Which stack, modules, topology, APIs, errors, jobs, and adapters should be built? |
| 6. Agent/tool boundary | What can the model read/propose, and which privileged capabilities are deliberately unavailable? |
| 7. Deterministic policy | Which formulas, matching rules, gate precedence, and domain calculations cannot be delegated to prose? |
| 8. UI and UX | Which routes/components/tokens/states/responsive/accessibility behaviors constitute the interface? |
| 9. Security and privacy | Which threats, authorization rules, upload/egress controls, retention, and audit properties are tested? |
| 10. Non-functional/operations | Which performance/capacity/reliability budgets, telemetry, backup, rollback, and kill switches are required? |
| 11. Data/eval/demo | Which fixtures, labels, metrics, thresholds, and end-to-end demonstration prove the build? |
| 12. Implementation sequence | Which vertical slices and artifacts lead to a reviewable handoff? |
| 13. Acceptance traceability | How does every original criterion map to verification and retained evidence? |
| 14. Completion rubric | What does 100-point completion mean, and which failures cannot be compensated by points? |
| 15. Pilot/change control | What remains prohibited until a real partner approves data, policy, consent, staffing, and operations? |

The documents are intentionally standalone. Shared architecture is repeated rather than forcing an agent to reconcile several inherited documents with possible conflicts.

## 6. Project-by-project coverage

### 6.1 Independent agent products

| Project | Detailed spec | Criteria | Distinctive implementation contract added |
| --- | --- | ---: | --- |
| GrantSnap | [Spec](../specs/grantsnap/SPEC.md) | 12 | Integer-cent reconciliation, rulebook activation, duplicate semantics, complete packet/export read-back |
| VolunteerBalance | [Spec](../specs/volunteerbalance/SPEC.md) | 11 | Canonical CP-SAT model, capacity-adjusted burden formula, private projections, per-assignment consent |
| BridgeMentor | [Spec](../specs/bridgementor/SPEC.md) | 11 | Hard eligibility filters, disclosed ranking formula, public-card allowlist, dual-consent introduction transaction |
| ToolTutor | [Spec](../specs/tooltutor/SPEC.md) | 11 | Signed three-step demo procedure, evidence binding, StepGate algorithm, stop/hold precedence |
| StreetVendor Radar | [Spec](../specs/streetvendor-radar/SPEC.md) | 11 | Source/revision model, staged triage, quoted-span validator, freshness and notification functions |
| UtilityShield | [Spec](../specs/utilityshield/SPEC.md) | 11 | Fictional reviewed rule pack, operational-vs-legal dates, severity ladder, capacity-held queue |
| LibraryLoop | [Spec](../specs/libraryloop/SPEC.md) | 11 | Closed policy DSL, guardrail precedence, row-level replay gate, idempotent inventory read-back |
| ColdWatch | [Spec](../specs/coldwatch/SPEC.md) | 11 | Dequeue-time consent/activation checks, attempt caps, monotonic severity, pause/suppress semantics |
| CenterSignal | [Spec](../specs/centersignal/SPEC.md) | 11 | Statement→readback→confirmation sequence, all-or-nothing snapshots, per-field TTL, report transaction |
| SchoolNotice | [Spec](../specs/schoolnotice/SPEC.md) | 10 | Digital-text/OCR basis, cross-stage value allowlists, constrained Spanish fixture path, ICS read-back |

### 6.2 Agentic Cinema products

| Project | Detailed spec | Criteria | Distinctive implementation contract added |
| --- | --- | ---: | --- |
| StageLine | [Spec](../specs/agentic-cinema/stageline/SPEC.md) | 9 | Rights gates, 2 fps bounded alignment, crop lineage, human continuity ledger |
| SecondUnit Match | [Spec](../specs/agentic-cinema/secondunit-match/SPEC.md) | 10 | FFprobe/overlap rules, deterministic frame pairs, CMX3600/CSV reparse validation |
| CrewClock | [Spec](../specs/agentic-cinema/crewclock/SPEC.md) | 10 | Canonical CP-SAT intervals, hard/soft rule separation, solver-proof labels, stale call-sheet approval |
| PremiereWatch | [Spec](../specs/agentic-cinema/premierewatch/SPEC.md) | 10 | Six-package matrix, evidence TTL, Grafana MCP identity, approval-bound annotation/read-back |
| SportsCaption SLO | [Spec](../specs/agentic-cinema/sportscaption-slo/SPEC.md) | 10 | Explicit probe/SLO formulas, minimum samples, confounder correlation, affected+control rechecks |
| MixWatch | [Spec](../specs/agentic-cinema/mixwatch/SPEC.md) | 10 | FFmpeg/EBU R128 facts, source-separated findings, n≥5 schedule estimates, new-artifact retry lineage |
| Fieldnote Desk | [Spec](../specs/agentic-cinema/fieldnote-desk/SPEC.md) | 10 | Default-deny confidentiality gateway, minimal public queries, conservative claim status, cited script diffs |
| Rights Ledger | [Spec](../specs/agentic-cinema/rights-ledger/SPEC.md) | 10 | Exact quote validation, per-dimension scope matcher, confidential public-signal separation |
| Archive Dossier | [Spec](../specs/agentic-cinema/archive-dossier/SPEC.md) | 10 | Atomic budget guard, extraction outcome enum, contradiction preservation, deterministic coverage formula |
| RunOfShow | [Spec](../specs/agentic-cinema/runofshow/SPEC.md) | 10 | ClickHouse sample/quantile schema, n≥8/fallback logic, coverage DAG/optimizer, no show control |
| Podcast Pulse | [Spec](../specs/agentic-cinema/podcast-pulse/SPEC.md) | 9 | ClickHouse event/views, exact retention denominators, cohort suppression, confounder-first investigation |
| AssetFinder | [Spec](../specs/agentic-cinema/assetfinder/SPEC.md) | 10 | Versioned vector indexes, rights-prefiltered MCP retrieval, frozen recall/precision targets, deletion cascade |
| MuseumWorld | [Spec](../specs/agentic-cinema/museumworld/SPEC.md) | 10 | Typed world compiler, deterministic conditions/effects, grounded narration, isolated sessions, `MUS-*` IDs |
| CaptionProof | [Spec](../specs/agentic-cinema/captionproof/SPEC.md) | 10 | Canonical cue patches, delivery-profile validation, exact editor batches, VTT/SRT reparse/revert lineage |
| ScriptBudget | [Spec](../specs/agentic-cinema/scriptbudget/SPEC.md) | 10 | Page/line breakdown, exact-cent formulas, deterministic grouping/schedule, n≥5 descriptive ranges, bias invariance |

## 7. UI and UX review

### 7.1 Baseline gap

The historical briefs named accessibility and occasionally mobile use, but did not define an implementable information architecture. An agent would have had to invent the majority of the interface, risking a generic chat-first dashboard inconsistent with the products' evidence- and workflow-centered intent.

### 7.2 Added UI contract

Every detailed spec now defines:

- A product-specific visual character and accent token, with semantic success/warning/danger/info/focus colors.
- Typography, spacing, radius, elevation, contrast, tabular-number, and system-font/offline behavior.
- Desktop rail/content/detail composition and single-column mobile adaptation.
- Named routes and the exact content/actions required on each screen.
- Domain-specific components such as GrantSnap's `DuplicateCompare`, ToolTutor's `StepCard`, RunOfShow's `CoverageMatrix`, and CaptionProof's `SuggestionDiff`.
- Shared evidence/source, status, approval, asynchronous job, table, toast/persistent-result, and error behavior.
- Loading, empty, unknown/partial, offline/error, success, stale approval, and refusal designs.
- Keyboard/focus/screen-reader/live-region/target-size/reflow/zoom/reduced-motion/media-alternative requirements.
- Plain-language constraints that prevent uncertainty, legal status, safety, or model proposals from being overstated.

An **Impeccable / UI UX Pro Max-style review lens** is included as a craft checklist: hierarchy, typography, spacing, purposeful color, realistic content, complete states, responsive composition, accessibility, and concise copy. These references are not presented as formal standards or dependencies. **WCAG 2.2 AA and the explicit manual tests are the normative accessibility bar.**

### 7.3 Remaining UI validation work

The specifications are textual build plans, not evidence of a visually implemented or user-tested interface. During each build, the agent must produce actual route/component implementations, browser traces, accessibility results, and realistic screenshots. A designer/accessibility reviewer and target users should review the implemented product; a token list or zero automated axe violations alone is not sufficient.

## 8. Technical soundness review of the new defaults

The common stack—Python/FastAPI/Pydantic/SQLAlchemy, React/TypeScript/Vite, relational persistence, private object storage, durable jobs, generated OpenAPI/client, and unit/property/API/security/browser/accessibility tests—is deliberately conventional and implementable. Project-specific kernels remain independent of web/model layers.

Key safeguards now specified include:

- Aggregate versions, idempotency keys, content-hash approvals, transactional audit/outbox, and explicit stale/conflict errors.
- SQLite restricted to single-process demos, with PostgreSQL for reference/multi-worker deployment.
- No generic agent SQL/HTTP/send/delete/publish/approve capability; partner tools are scoped schemas/templates.
- Scripted providers exercising the same agent/tool/policy/state path rather than bypassing it.
- Actual media/frame/timecode/audio/cost/schedule formulas instead of model-generated numeric authority.
- Separate offline and live evidence, explicit external blockers, and no fabricated integration claims.

Implementation agents must still verify the following rather than treating the spec as a substitute for engineering validation:

1. **Installed SDK behavior.** Strands, Google ADK/Gemini, Grafana MCP, Parallel, `mcp-clickhouse`, and Replit interfaces must be checked against the pinned installed versions. No document-defined tool name licenses inventing an SDK call.
2. **Native media dependencies.** FFmpeg/FFprobe and audio/image behavior must be pinned and golden-tested on the actual deployment platform.
3. **Solver reproducibility.** Fixed versions, one worker, canonical ordering, integer-scaled objectives, and golden outputs are required; byte-stability claims must be tested on supported platforms, not assumed across arbitrary versions.
4. **Database parity.** SQLite/PostgreSQL differences in transactions, locking, JSON, date/time, and concurrency require integration coverage before multi-worker claims.
5. **Offline setup truth.** Lockfiles and package caches must support the claimed offline path; a clean-clone test with network disabled must distinguish dependency-cache availability from hidden downloads.
6. **Human-reviewed source material.** Rulebooks, translations, media rights, accessibility conclusions, and legal/policy interpretations cannot be self-certified by an implementation agent or model.
7. **Real accessibility and usability.** Automated checks are only one layer; manual keyboard, screen-reader, zoom/reflow, media alternatives, and target-user review remain required.

## 9. Verification and rubric design

Each detailed specification carries its historical acceptance rows plus six global documentation-to-build gates. The 100-point rubric allocates:

- 15 points — product workflow and scope.
- 20 points — domain correctness and provenance.
- 15 points — agent and integration boundary.
- 15 points — UI/UX and accessibility.
- 15 points — security, privacy, and abuse resistance.
- 10 points — verification and evaluation.
- 10 points — operations and handoff.

Full completion requires at least 90 points, no category below 80% of its weight, all applicable acceptance criteria, and every hard gate. This prevents a visually polished demo from compensating for an authorization bypass, fabricated evidence, missing negative case, or silent data loss.

The evaluation requirements are deliberately corpus-specific. Targets such as GrantSnap's zero false eligible inclusions, AssetFinder's frozen recall@10/precision@10, or ColdWatch's repeated urgent-persona trials are engineering gates on named fixtures—not claims about field performance.

## 10. Residual risks and owner decisions

| Risk / decision | Why it remains | Required handling |
| --- | --- | --- |
| Specifications are not implementations | No runtime has been built or tested. | Select a project, implement its slices, and retain actual evidence before changing maturity. |
| External providers/partners are unverified here | Accounts, current docs, SDK versions, quotas, and hosting were not exercised. | Keep integration status blocked/pending until real sanitized live-smoke evidence exists. |
| Real-world sources/policies need owners | Fictional demo rules cannot establish legal, safety, district, rights, or production correctness. | Named partner review is a pre-pilot gate; never model-generate authoritative policy. |
| Human research/accessibility review is pending | Documents cannot validate user value, translation quality, or real usability. | Conduct discovery, target-user testing, accessibility review, and qualified translation/policy review. |
| Quantitative thresholds are initial engineering baselines | Synthetic corpora may be easier or different from field data. | Freeze labels before tuning, report every miss, and version threshold changes with new evaluations. |
| Repository licensing is unspecified | The owner did not request a license choice and none should be inferred. | Choose documentation/code licenses deliberately before external reuse or distribution. |
| Building 25 products at once would dilute quality | Each spec intentionally describes a complete standalone vertical product. | Select one based on partner/data access; do not merge the portfolio into a single runtime. |

## 11. Recommended implementation rollout

1. **Select one product**, based on a real user problem and access to a partner who can own policies/sources—not on which concept appears easiest to demo.
2. **Create a new standalone repository** and copy the chosen `SPEC.md` into it as the normative input. Keep the other 24 products out of scope.
3. **Create the acceptance matrix before coding.** Map every source criterion and global gate to a module/symbol, fail-first test or manual procedure, expected result, and evidence path.
4. **Build the deterministic kernel and fixtures first.** Prove calculations, constraints, state, authority, provenance, and failure cases without a model.
5. **Add the real agent loop with scripted responses.** Verify that the model cannot bypass tools/policy/state and that offline tests require no paid call or external contact.
6. **Implement the UI vertical slice and all states.** Include keyboard/mobile/screen-reader/zoom behavior as each route lands, not as a final cosmetic pass.
7. **Complete export/read-back, recovery, evaluation, accessibility, and runbook evidence.** Publish all misses and unresolved external blockers.
8. **Run integrated live smoke only when authorized.** Use isolated accounts, hard spend/request caps, server-side secrets, and sanitized request/provider/MCP/hosting evidence.
9. **Treat a real pilot as a separate approval.** Obtain consent, source/policy ownership, retention/deletion approval, staffing, security review, and rehearsed disable/restore before real data or contact.

## 12. Documentation validation result

The repository now includes a standard-library validator invoked by:

```bash
make verify-docs
```

**Result at handoff: PASS.** The completed run reported 25 detailed / 25 historical projects, 258 inherited criteria with globally unique detailed IDs, 13,117 detailed-spec lines, and 108 resolved local links.

It checks:

- 25 historical briefs and 25 detailed specifications.
- Every required specification section and standalone-use statement.
- At least five concrete UI routes and four evaluation metrics per project.
- Seven rubric categories totaling 100 points per project.
- All 258 historical criteria and their original requirement text.
- Global uniqueness of detailed acceptance IDs, including the MuseumWorld migration.
- Portfolio index coverage and local Markdown link existence.
- Absence of unfinished `TBD`/`TODO`/`FIXME`/lorem markers.

The validator is intentionally a **documentation integrity check**, not a substitute for reviewing technical content or implementing the products.

## 13. Conclusion

The original repository had strong conceptual safety and evaluation instincts but was not detailed enough to function as an autonomous build specification. The new per-project folders close that documentation gap with concrete architecture, domain logic, APIs, UI plans, evaluation, and completion governance while retaining the original briefs for provenance.

The appropriate next action is **one evidence-led standalone implementation**, not a claim that 25 products are complete and not a combined portfolio application. All maturity, integration, and impact claims should remain tied to retained build and partner evidence.
