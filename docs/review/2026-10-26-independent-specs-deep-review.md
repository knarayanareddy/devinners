# Deep review — the 11 independent-portfolio documents

**Review date:** 2026-10-26<br>
**Baseline:** `40bef4a4137882230dd8d349c6ed945f99b4cffa` on `arena/4a7846ca-devinners`<br>
**Documents reviewed (11):** [Portfolio index](../specs/README.md) + the 10 independent-agent specifications (`docs/specs/<project>/SPEC.md`)<br>
**Companion:** [2026-10-26 end-to-end repository review](2026-10-26-end-to-end-review.md)

## 1. Method

The index and **GrantSnap** were read end to end (GrantSnap serves as the family reference). The ten specifications share a deliberately repeated 15-section contract: line-level analysis showed **78% of each document is verbatim-identical shared template text** (already reviewed in full via GrantSnap), and **~113 lines per document (22%) are project-specific**. Every project-specific line of all nine remaining specifications was read in full, presented under its section heading, after machine-verifying that the shared remainder is identical to the reference text.

Supporting checks run over all 11 documents:

- Criteria counts: index row → historical brief → `SPEC.md` acceptance table → `G-01` traceability gate (all four agree per project; 110 criteria total for this family).
- Copy-paste residue scan: GrantSnap-specific nouns (`receipt`, `expense`, `rulebook`, `packet`) appear in other specs only as legitimate domain terms (e.g., UtilityShield's own rulebook/packets, "retention receipt" phrasing).
- Per-project design token distinctness, route counts (7 each), specification dates, corpus-size claims coherence across §1.5 / §11.1 / §12 / acceptance rows, non-empty acceptance cells, and family-wide score-rule uniformity.
- Verification-cell distinctness per acceptance table (the portfolio-level E-03 finding, quantified per document here).

## 2. Verdict

**The index is accurate and all ten specifications are implementation-ready, internally consistent, and genuinely project-specific where it matters.** Domain policy (§7), actors, workflows, aggregates, APIs, tools, UI routes/components, evaluation contracts, and pilot gates are concrete and distinct in every document; only the cross-cutting contract text (security boilerplate, API semantics, rubric, commands) is shared — by design and disclosed.

Three findings, all **Low**, none blocking an implementation start — and all three remediated on 2026-10-26 (see §7):

| ID | Document | Finding |
| --- | --- | --- |
| FD-1 | All 10 (worst: StreetVendor Radar) | Acceptance-table verification text is partially templated: 63/110 distinct cells in this family. Requirement text is always specific; the verification/evidence column often repeats a generic method that fits only loosely (examples below). Deepens portfolio finding E-03. |
| FD-2 | ToolTutor | Retry-count ambiguity: §1.5 says "at most 3 evidence retries before instructor hold" while §7 says "the third failure creates hold" — 3 retries implies up to 4 submissions, the third failure implies 3. An implementer could build either. |
| FD-3 | ToolTutor | Internal tension: `TT-07` requires "the real Strands hook/service boundary" to block `advance_step`, while §5.2 of the same document warns "No invented hook/interrupt APIs." The criterion should name the application-service/authorization boundary instead of presuming an SDK hook. |

## 3. Portfolio index (`docs/specs/README.md`)

**Strengths**

- Every numeric claim checks out: 10 + 15 rows, per-row criteria counts match the historical briefs and spec tables (110 for this family), completion labels match what the specs actually enforce, and the `MW-*`/`MUS-*` collision note is accurate.
- Honest framing throughout: "documentation only", specification ≠ implementation ≠ integration ≠ pilot, contest closed for cinema, and the "do not weaken gates to obtain a passing score" instruction.
- The UI/UX baseline section is not aspirational — each listed property exists in the specs (verified: project-specific tokens, 7 named routes per spec, full state matrix, WCAG 2.2 AA + manual checks, Impeccable lens).
- Navigation links to all 25 `SPEC.md` files, both historical indexes, and the review; all resolve.

**Gaps:** none found in this document.

## 4. Per-specification reviews

### 4.1 GrantSnap — 12 criteria (index: 12 ✓)

**Strengths.** The most money-rigorous spec of the family: integer-cent-only arithmetic with a lint-enforced "no float money" eval metric; reconciliation formula (`Σextended + tax − discount`) with mismatch → `needs_review`, never auto-balanced; duplicate detection requires **both** identical evidence SHA-256 and matching normalized vendor/date/amount, so legitimate repeat purchases survive; rulebook activation requires `REVIEWED` status with source URI and reviewer identity; packet approval binds a digest over ordered lines/dispositions/amounts + evidence hashes + rulebook version + destination, and export re-parses CSV/PDF against the manifest (read-back, not write-and-forget). `GS-01` makes clean-clone offline setup a criterion, not an aspiration.

**Notes.** Verification-cell reuse: `GS-04`, `GS-06`, `GS-09` share one verification sentence — but they test different things (evidence spans, duplicate semantics, unreadable-total holds). The "mutate/delete a reference → visible hold" instruction fits GS-04, only loosely GS-06/GS-09 (FD-1 exemplar). Eval thresholds are corpus-scoped and say so explicitly ("zero false eligible inclusions **on the safety corpus**").

### 4.2 VolunteerBalance — 11 criteria (✓)

**Strengths.** The strongest solver-honesty design: canonical CP-SAT model, pinned version/seed/one worker/10s limit, lexicographic objective (uncovered-priority diagnostic only → burden range in integer millionths → travel → canonical UUID key), and partial results explicitly labeled as a separate diagnostic solve that can never masquerade as satisfied coverage. `burden = assigned_minutes / max_minutes` with a zero-capacity guard. Private reasons are encrypted with canary tests covering direct, paraphrased, encoded, and split exfiltration — and the spec refuses "perfect semantic leak detection" claims. Publication requires every non-cancelled assignment accepted; fairness output is row-order invariant and recomputable.

**Notes.** "Byte-stable canonical proposal" is asserted as an evaluation target — as the prior review already records, solver byte-stability must be *empirically proven* on the pinned platform, not assumed from the spec (carried risk, not a new defect).

### 4.3 BridgeMentor — 11 criteria (✓)

**Strengths.** Hard eligibility filters run **before** any model call, and the agent can only explain, never re-rank: `score = 40·goal + 25·skill + 15·language + 10·mode + 10·overlap` over approved public fields only, with taxonomy Jaccard overlap and an explicit "no embeddings or protected-trait proxies in v1". Dual consent is an atomic transaction over matching pair/card/message hashes — one-sided, stale, duplicate, or reordered decisions cannot produce an introduction; block/report bypasses consent entirely and never exposes the report narrative to the other party. `BM-10` bans dark patterns and default-checked consent. Fixed decisions (capacity 3, 7-day invitations, 14-day consent) are internally consistent across §1.5, §4, and §7.

**Notes.** None beyond family-wide FD-1 (`BM-02/03/06/08` share one verification sentence).

### 4.4 ToolTutor — 11 criteria (✓)

**Strengths.** The most precisely gated spec: `StepGate.decide` enumerates every binding (actor=worker, session/step/machine/version identity, proposal↔submission hash, schema/model allowlist), quality flags force `uncertain` regardless of a proposed pass, `STOP` sets hold + instructor task in the same transaction and later passes cannot reopen, and the gate endpoint is internal-only (external/agent callers get 403). Hazard precedence, 3-attempt bounded retry, completion ≠ safety certification, and a20-run-per-stop-persona eval are all explicit. The §11.3 demo includes the adversarial `advance_step` attempt.

**Gaps.**
- **FD-2:** retry off-by-one between §1.5 ("at most 3 evidence retries") and §7 ("the third failure creates hold"). The historical brief contains no retry count, so both clauses originate here; pick one (recommendation: keep §7's normative "third failure → hold" and reword §1.5 to "two retries after a failed attempt, hold on the third failure").
- **FD-3:** `TT-07`'s "real Strands hook/service boundary" conflicts with §5.2's "No invented hook/interrupt APIs" (lines 174 and 460 of the same file). The boundary to name is the application service/authorization layer; the scripted-model test does not need an SDK hook to exist.

### 4.5 StreetVendor Radar — 11 criteria (✓)

**Strengths.** Auditability is the core design, not a bolt-on: every pipeline stage — fetch, normalize, dedupe, metadata filter, triage reject, attachment failure — must produce exactly one searchable decision with a reason; `all_clear` is computable only when every required source is fresh and no required triage job is incomplete; profile changes are owner-approved versioned diffs that re-triage forward without rewriting history; attachment extraction is bounded (3 attachments/30 pages/15 MB) and failures become `REVIEW_REQUIRED`, never silent rejects; notification policy (quiet hours, caps, urgent rule) is pure functions with no model discretion.

**Notes.** **FD-1 worst case:** only 4/11 distinct verification cells — `SV-01/02/07/11` share one sentence ("schema and integration tests resolve every reference…"), `SV-03/04/05/06` share another, `SV-08/10` share the `make eval` text even though SV-10 is specifically about scripted-default/live-capped evaluation runs. The requirement column is specific; the verification column should be too.

### 4.6 UtilityShield — 11 criteria (✓)

**Strengths.** The honesty model is exceptional: the **only** computed date is `operational_review_by = stated_shutoff_date − 2 reviewed business days`, `legal_deadline` stays null unless separately reviewed, and unsupported jurisdictions refuse rather than fall back to generic rules. Severity (`IMMEDIATE_SERVICE_RISK > DATE_WITHIN_WINDOW > UNRESOLVED_CLOCK > MONITOR`) keeps unresolved clocks visible; capacity adds `HELD_CAPACITY` without ever mutating severity or hiding cases; two-person rulebook review; a language guard forbids eligibility/entitlement/protection claims in generated text; v1 has no egress at all (`US-07`).

**Notes.** Corpus (60+ notices), capacity (5), the two-day rule, and retention windows are consistent across §1.5/§7/§9/§11/§13. Family FD-1 applies (`US-02/05/11` share a verification sentence).

### 4.7 LibraryLoop — 11 criteria (✓)

**Strengths.** The most conservative policy-automation spec: a closed typed DSL (`eq`/`in`/`is_true` only, unknown properties rejected, no code/SQL strings), guardrails that always escalate damage/safety/serial/dispute/conflict/duplicates *before* policy evaluation, and replay semantics where `REVIEW` labels count as **false automatic actions** when matched — conservative in exactly the right direction. Activation requires current corpus hash, `false_auto = 0`, `coverage > 0`, a distinct approver, and an exact diff; the spec explicitly refuses coverage-quota pressure. Execution re-derives facts and compares `input_fact_hash` before one idempotent action with read-back.

**Notes.** Verification grouping `LL-01/02/07/10/11` (5 criteria) under one sentence is the second-largest repeated group in the family (FD-1).

### 4.8 ColdWatch — 11 criteria (✓)

**Strengths.** Every contact precondition is re-checked at dequeue time (incident active, alert valid, plan hash current, consent, suppression, local window, attempt cap, channel caps) with the leased outbox key committed before adapter invocation; `final = max(model, phrase_backstop, protocol_backstop)` is monotonic and can never be lowered; no-answer/voicemail/timeout/unknown are structurally incapable of becoming `OK`; outbound text scanners prohibit unverified arrival/medical/emergency claims; live mode has no configured recipients and must refuse; a always-visible kill switch, per-mode caps, and cost counters round it out. The spec states outright that adapter success ≠ resident safety.

**Notes.** Window (09:00–18:00), 2 attempts/15 min apart, 12 residents, 100 cases, and 20-run urgent trials are consistent across §1.5/§7/§11. Family FD-1 applies (`CW-05/06/08/11` share one sentence).

### 4.9 CenterSignal — 11 criteria (✓)

**Strengths.** The cleanest evidence-state machine in the family: statement `S` → full-value readback `R` → explicit confirmation `C` with strictly increasing turn indexes, where hedges/silence/corrections/wrong-speaker restart or fail the sequence; field policy is evaluated for the whole call and any review-required field publishes **zero** fields (no mixed snapshots); per-field TTLs expire to `UNKNOWN` without erasing evidence; capacity uses bands and rejects exact counts outright; a visitor's closed-door report atomically creates/merges one task and marks status unverified — never auto-closing. Audio is never retained.

**Notes.** 8 centers / 80 personas / TTL tiers / calling window + attempt cap are coherent across §1.5/§4/§7/§11. FD-1: `CS-02/03/04/05/11` share one verification sentence — the largest single group alongside ToolTutor's.

### 4.10 SchoolNotice — 10 criteria (index: 10 ✓)

**Strengths.** Child-data discipline is woven through every stage: digital-text vs OCR basis is a first-class disclosed distinction; `allowed_values` is rebuilt from verified facts before *every* generation stage (explanation, translation, reminder, draft) and complementary parsers reject any ungrounded date/time/number/URL/phone/address/ID token — rejecting the whole artifact, not warning; the Spanish path is a fixed reviewed glossary/fixture described honestly as "a test oracle, not a claim of district/official translation quality"; reminders are local `.ics` with `DTSTART;TZID=Europe/Amsterdam` parsed back for equality; there is no school-send capability at all; raw notices delete after 24 hours with per-store deletion manifests.

**Notes.** Glossary pairs, 50+ corpus, retention, and route contents all agree across sections. `SN-05` mentions school messaging but correctly scopes it ("MVP provides draft/copy only—no autonomous send"). Family FD-1: `SN-01/03/06/07/09` share one verification sentence.

## 5. What was checked and passed

| Check | Result |
| --- | --- |
| Index criteria counts vs briefs vs spec tables vs `G-01` | ✅ 10/10 (110 family total) |
| Track/family numbering in specs vs index rows | ✅ 10/10 |
| Specification dates (2026-10-24) | ✅ 10/10 |
| UI routes per spec (§8.2) | ✅ 7 each |
| Design tokens project-specific (distinct accents) | ✅ 10/10 |
| Family score rule (≥90, 80% floor, optional live-model lane) | ✅ 10/10 |
| Acceptance rows: unique IDs, non-empty cells, lanes | ✅ 110/110 |
| Corpus-size claims coherent across §1.5/§11.1/§12/§13 | ✅ no contradictions |
| GrantSnap noun residue in other specs | ✅ none (domain-legitimate uses only) |
| Source-brief links (sole local link per spec) | ✅ 10/10 |
| Section contract (15 sections, order, rubric 7×100, hard gates) | ✅ 10/10 (per end-to-end audit) |

## 6. Recommended edits (optional, all small)

1. **FD-1:** rewrite the repeated verification cells in `streetvendor-radar` (4/11), then `tooltutor`, `libraryloop`, `schoolnotice`, `centersignal`, `coldwatch`, `volunteerbalance` (each 6/11) so each row names its own test surface and evidence artifact. Keep the requirement text untouched (it is baseline-bound).
2. **FD-2:** in `tooltutor`, align §1.5 with §7's normative "third failure creates hold" (e.g., "at most two retries after a failed attempt; the third failure creates an instructor hold").
3. **FD-3:** in `tooltutor`, reword `TT-07`'s verification of the boundary as "the application service/authorization boundary blocks it before state mutation", matching §5.2's warning against invented SDK hooks.
4. Carried from the prior review: treat VolunteerBalance's byte-stable solver claim as a build-time experiment with retained evidence, not a spec guarantee.

None of these block handing any of the ten specifications to an implementation agent; they are precision improvements to the verification layer.

## 7. Post-review remediation (2026-10-26)

All three findings were remediated the same day, without touching the historical briefs (provenance is preserved and validator-enforced):

| Finding | Change applied | Verification |
| --- | --- | --- |
| FD-1 (worst case) | Rewrote all 11 StreetVendor Radar verification cells so each names its own test surface and evidence artifact (source-metadata refusals, evidence resolution, per-stage decision-log parity, TTL clock control, profile-write authorization, injection suite, duplicate/revision lineage, digest boundaries, scripted-vs-live cost lanes, demo-e2e trace). Requirement cells untouched. | `make verify-docs` PASS; distinctness now **11/11** (was 4/11) |
| FD-2 | ToolTutor §1.5 now reads "at most two retries after a failed or uncertain attempt; the third failure creates an instructor hold, matching the StepGate rule in §7", removing the off-by-one against §7. | `make verify-docs` PASS; §1.5 ↔ §7 aligned |
| FD-3 | ToolTutor `TT-07` keeps the historical sentence verbatim and now defines the named boundary as the application service and internal-only gate command (§5.4/§7), explicitly assuming no SDK hook or interrupt API (§5.2); its verification cell is now a fail-first boundary test asserting zero state mutation. | `make verify-docs` PASS; ToolTutor distinctness now 7/11 |

**Remaining FD-1 scope:** verification cells in the other nine specifications (6–9 distinct cells each) remain as found; the §6 recommendations still apply portfolio-wide if desired.
