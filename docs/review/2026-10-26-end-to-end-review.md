# End-to-end repository review — 2026-10-26

**Review date:** 2026-10-26<br>
**Reviewed baseline:** `40bef4a4137882230dd8d349c6ed945f99b4cffa` (merge of PR #1 into `main`)<br>
**Working branch:** `arena/4a7846ca-devinners`<br>
**Repository type:** documentation-only product-specification portfolio<br>
**Prior review:** [2026-10-24 end-to-end review](2026-10-24-end-to-end-review.md) (its claims are re-verified in §3)

## 1. Executive summary

The repository is a **documentation-only portfolio**: 25 standalone implementation specifications (13,117 lines), 25 historical briefs, two portfolio indexes, one root README, one standard-library validator, and the prior remediation review. There is no product code, dependency manifest, test suite, deployment, or CI — so, as before, this review assesses **documentation integrity, internal consistency, and implementation readiness**, not runtime behavior.

**Headline result: the pack is internally sound and its own validator passes.** `make verify-docs` passes (25/25 specs, 258/258 inherited criteria with globally unique IDs, 13,117 lines, 108 local links). An independent audit beyond the validator — structural ordering, table integrity, cross-section endpoint coherence, `§` cross-references, link anchors, citation indices, per-row index counts, cross-project name leakage, rubric/gate uniformity, and re-verification of the prior review's baseline measurements — found **no defects in the specifications themselves**.

Seven findings remain, none affecting spec correctness: the validator runs nowhere automatically (**E-01**), the GitHub repository description still says "Ten" products (**E-02**), acceptance-table verification text is partially templated in a handful of specs (**E-03**), two historical docs name an undefined external project "Harness-Zero" (**E-04**), no license/security policy exists on a public repo (**E-05**), 16 external contest links could not be revalidated from this environment (**E-06**), and the validator has some scope gaps that this review covered manually (**E-07**).

**Maturity remains `specified`, not implemented.**

## 2. Scope and method

### 2.1 What was executed or inspected

- `make verify-docs` — full validator run, result **PASS**.
- All 58 tracked files (55 Markdown, 1 Python, 1 Makefile, 1 `.gitignore`) and all 55 Markdown documents read or machine-scanned.
- Git history (deepened from the initial shallow clone to the full 4-commit history) and GitHub repository/PR metadata via `gh`.
- An independent standard-library audit script covering, beyond the built-in validator:
  - `## 1`–`## 15` section ordering and heading-level progression (no skipped levels, no duplicate headings).
  - Markdown table pipe-count consistency inside every spec.
  - Acceptance tables: no empty verification/evidence cells; row counts equal source-criterion counts.
  - API path coherence: every `` `/api/v1/…` `` path referenced in any section is defined in §5.4.
  - `§N` / `§N.M` cross-references all resolve to real sections; local Markdown anchors resolve to real headings.
  - Per-row criterion counts in both portfolio indexes match the linked source briefs and spec tables.
  - Cross-project product-name leakage inside specs (only hit: MuseumWorld's documented `MW-*` collision note).
  - Rubric uniformity: 7 categories summing to 100, `≥90/100` + 80%-floor score rule, and a non-compensable hard-gate section in all 25 specs.
  - Uniform presence of error-envelope/idempotency/audit/retention/kill-switch/OpenAPI/scripted-provider/prompt-injection terms in all 25 specs.
  - Placeholder scan across **all** Markdown, not only specs.
  - Cinema README citation indices `[1]`–`[16]`: all used citations are defined and vice versa.
  - Self-containment: each `SPEC.md` has exactly one local outbound link — its historical source brief.
- All 11 GitHub provenance links re-verified live via the GitHub API (all HTTP 200, repositories exist).
- Full read of representative specs (GrantSnap, StageLine) plus machine comparison of per-section similarity across projects.

### 2.2 What could not be inspected or executed

- **No product runtime exists**, so no statement is made about implemented behavior, performance, vulnerabilities, or accessibility of working software.
- **16 unique `devpost.com` URLs and the contest rules page were not revalidated**: this environment can reach only GitHub/npm/PyPI hosts. The docs already require rechecking partner/contest requirements before any claim; that requirement stands.
- **No third-party or partner SDK/contest claim was revalidated** — same boundary as the prior review.
- External link behavior (redirects, page content) beyond repository existence was not assessed.

## 3. Inventory and verification of the prior review

Current tracked inventory: **58 files — 55 `.md`, 1 `.py`, `Makefile`, `.gitignore`**; no non-text assets, no secrets, no large files. History is 4 commits (two original spec commits, one PR commit, one merge commit dated 2026-10-24).

Every reproducible numeric claim in the [2026-10-24 review](2026-10-24-end-to-end-review.md) was re-computed against its stated baseline commit `d249cdb…`:

| Claim in prior review | Re-computed | Result |
| --- | ---: | --- |
| 27 tracked files at baseline, all Markdown | 27, all `.md` | ✅ |
| 1,017 project-brief lines (excluding two indexes) | 1,017 | ✅ |
| Median brief 39 lines; min 30; max 72 | 39; podcast-pulse; grantsnap | ✅ |
| 258 historical criteria; 248 unique (`MW-*` collision) | 258; 248 | ✅ |
| Briefs averaged ≈41 lines | 1,017 / 25 = 40.7 | ✅ |
| 25 specs ≈520 lines, 13,117 total | 523–527 each; 13,117 | ✅ |
| Validator result: 108 local links | 108 | ✅ |

The prior review's baseline commit is a real ancestor of `main` (the initial clone was shallow and required `git fetch --depth=50` to reach it — an environment artifact, not a repository defect).

## 4. Automated validation result

```text
make verify-docs → PASS
  Projects:             25 detailed / 25 historical
  Acceptance criteria:  258 inherited, globally unique detailed IDs
  Detailed content:     13,117 lines
  Local links checked:  108 at baseline; 111 after this review added its own
                        README/index links
```

Independent audit results (this review):

| Check | Scope | Result |
| --- | --- | --- |
| 15-section contract, order, uniqueness | 25 specs | ✅ 25/25 |
| Heading-level progression / duplicate headings | 25 specs | ✅ 0 issues |
| Table column consistency | 25 specs | ✅ 0 issues |
| Acceptance rows: non-empty cells, count parity vs source | 258 rows | ✅ 0 issues |
| API paths defined in §5.4 for every reference | 25 specs | ✅ 0 undefined |
| `§N` / `§N.M` cross-references resolve | 25 specs | ✅ 0 broken |
| Local link + fragment-anchor resolution | all 55 docs | ✅ 0 broken |
| Index per-row criterion counts (both indexes) | 40 rows | ✅ all match |
| Rubric: 7 categories = 100, ≥90 rule, 80% floor, hard-gate section | 25 specs | ✅ 25/25 |
| Routes per spec (§8.2) | 25 specs | ✅ 7 each |
| Score-rule variants | 25 specs | ✅ 15 cinema + 10 independent, consistent by family |
| Cross-project name leakage | 25 specs | ✅ only documented `MW-*` note |
| Placeholder markers (all Markdown) | 55 docs | ✅ only validator's own marker list quoted in prior review |
| Cinema citation index `[1]`–`[16]` | 1 doc | ✅ complete both ways |
| Self-containment (one local link = source brief) | 25 specs | ✅ 25/25 |
| GitHub provenance links | 11 URLs | ✅ all live |
| Content distinctness (§7 policy similarity ≈0.23 between unrelated projects; structural sections 0.63–0.89) | sampled | ✅ project-tailored where it matters |
| Root/index claims (25 / 258 / 13,117 / 108) | README, index | ✅ match validator output |

## 5. Findings

| ID | Severity | Finding | Evidence | Recommendation |
| --- | --- | --- | --- | --- |
| E-01 | **Medium** | The validator runs only on manual command. There is no `.github/` directory, workflow, or pre-commit hook, so a future edit can silently break acceptance traceability, links, or section structure until someone remembers to run `make verify-docs`. | No CI config in tree; PR #1 has no checks. | Add a minimal GitHub Actions workflow that runs `make verify-docs` on pushes and pull requests. |
| E-02 | Low | GitHub repository description is stale: *"Ten standalone, human-centered agent project specifications"* while the repository now contains 25. External metadata disagrees with the root README. | `gh repo view` → `description`. | Update the repository description (and optionally add topics such as `specifications`, `agent`). |
| E-03 | Low | Acceptance-table **verification** text is partially templated. Portfolio-wide only 156/258 verification cells are distinct; worst case `streetvendor-radar` has 4 distinct cells across 11 criteria (several specs at 5/10). Requirement text is project-specific, but criterion-specific evidence instructions repeat generic "Domain, API, and browser integration tests…" phrasing, weakening per-criterion verifiability. | Independent audit of §13.2 tables. | Enrich verification cells in the worst-scoring specs with criterion-specific test/evidence names. Not blocking: each row still names a verification method, lane, and evidence class. |
| E-04 | Low | Two **historical** documents instruct readers not to build inside "Harness-Zero", an external project never defined or linked anywhere in this repository. Detailed specs do not carry the reference, so normative docs are unaffected, but a standalone reader of the briefs cannot resolve the name. | `2026-10-23-agent-project-spec-pack.md:30,104`; `agentic-cinema/README.md:48`. | Add a one-line provenance footnote (external repository of the portfolio owner) or drop the phrase from the cinema README. |
| E-05 | Low — owner decision | Public repository with `licenseInfo: null`, no `SECURITY.md`, no repository topics, and no contribution guidance. Carried forward unchanged from the prior review's R-11. | `gh repo view`. | Owner deliberately chooses documentation license and security-contact policy before external reuse. |
| E-06 | Informational | 16 unique `devpost.com` links (plus `agentic-cinema.devpost.com/rules`) could not be revalidated from this environment; link rot in contest provenance cannot be ruled out. The 11 GitHub repository links were revalidated and are live. | Host allowlist; GitHub API checks. | Recheck devpost links when the cinema provenance is next touched; docs already require revalidating contest/partner claims before use. |
| E-07 | Informational | Validator coverage gaps, all covered manually in this review and currently passing: placeholder scan limited to `SPEC.md` files (not indexes/review); no per-row index count check; no `§`-reference, anchor, table-column, heading-order, or rubric score-rule checks; no external-link checks; no CI (see E-01). The `criteria != 258` baseline is hard-coded — intentional as a drift tripwire, but it must be updated deliberately if briefs ever change. | `scripts/validate_specs.py` vs audit scope. | Optionally fold the highest-value checks (index row counts, `§` resolution, score-rule presence) into the validator. |

**No high-severity findings.** Nothing found contradicts the specification content, its traceability, or its stated maturity labels.

## 6. Qualitative assessment

1. **Contract discipline is unusually consistent.** All 25 specs share the same 15-section normative contract, the same completion labels, the same 100-point rubric with non-compensable gates, and the same truthful-lane vocabulary (`implemented-scripted` / `implemented-live` / `simulated` / `blocked-external` / `not implemented`). The two family-specific score-rule variants (cinema dual offline/integrated scores; independent optional live-model lane) are deliberate and uniformly applied.
2. **Self-containment holds.** Each spec's only local dependency is its historical brief, explicitly labeled "historical context only". Shared architecture is duplicated by design rather than split across documents an implementation agent would have to reconcile.
3. **Determinism and authority boundaries are concrete, not decorative.** Endpoint tables specify actor, semantics, and error behavior; §7 carries project-specific formulas (integer-cent reconciliation, CP-SAT models, frame/crop provenance, exact scope matching). Per-section similarity confirms real divergence exactly where it matters (§7 ≈0.23 between unrelated projects) while structural sections are intentionally parallel.
4. **The main documentation risks are at the edges, not the core**: stale external metadata (E-02), partially generic verification instructions (E-03), unverifiable external provenance links (E-06), and unenforced validation (E-01).
5. **Maturity labeling is honest throughout.** Every entry point repeats that specification ≠ implementation ≠ integration ≠ pilot. No document claims working software, measured impact, legal correctness, or contest qualification.

## 7. Residual risks (carried forward, still open)

| Risk | Required handling |
| --- | --- |
| Specifications are not implementations | Select one product, build its slices, retain real evidence before changing any completion label. |
| External providers/partners/contest rules unverified | Keep integration/qualification claims blocked until current official resources and live sanitized evidence exist. |
| Human-reviewed sources (rules, translations, rights, accessibility) | Named human/partner review remains a pre-pilot gate; never self-certify with a model. |
| Thresholds are baselines on synthetic corpora | Freeze labels before tuning; report every miss and denominator; version threshold changes. |
| No license / security policy on a public repo | Owner decision (E-05). |
| Building many products at once would dilute quality | Pick one spec; keep each build in a standalone repository. |

## 8. Recommended next steps

1. **Wire the validator into CI** (E-01) — a ~15-line workflow; highest leverage of all findings.
2. **Refresh external metadata** (E-02): repository description, optional topics.
3. **Decide on licensing and a security contact** (E-05) before the portfolio is reused externally.
4. **Optionally harden the validator** (E-07) with index row-count, `§`-reference, and score-rule checks from this review's audit.
5. **Optionally enrich the most templated verification cells** (E-03), starting with `streetvendor-radar` (4/11 distinct).
6. **Proceed to one evidence-led standalone implementation**, following the rollout sequence in the prior review — unchanged, and still the correct next major action.

## 9. Conclusion

Between the two reviews, the repository has gone from under-specified briefs to a validated, internally consistent, 25-product specification portfolio. This review re-verified every reproducible claim of the prior one and pushed past the built-in validator into structural, cross-referential, and external-metadata territory. The specifications themselves came through clean; what remains is operational hygiene (CI, metadata, licensing) and the still-open boundary between documentation and software.

**Validation status at review close: `make verify-docs` PASS; independent audit: 0 specification defects, 7 findings (1 medium, 3 low, 3 informational).**
