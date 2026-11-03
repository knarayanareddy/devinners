# Devinners remediation plan

Proposed work only; see [review](REVIEW.md). This plan is for a **documentation portfolio and spec handoff process**, not for a currently deployed app.

## 1. Phased roadmap with entry and exit criteria

| Phase | Purpose | Entry criteria | Exit criteria |
| --- | --- | --- | --- |
| P1. Portfolio boundary and ownership | Confirm what the repo may truthfully claim and who can authorize next use | Current docs snapshot available; owner names a portfolio maintainer | Docs-only boundary, acceptance owner, and “implementation-ready” usage rules are recorded |
| P2. Structural verification hardening | Prove the validator catches the intended documentation failures | P1 complete; validator source reviewed in full | Negative fixtures and repeatable checks demonstrate structural failures are detected without overstating assurance |
| P3. Selected-spec handoff gate | Approve one spec for downstream implementation review | P1 and P2 complete; one target `SPEC.md` chosen | One spec has substantive review notes, approved pilot boundary, and release/rollback/recovery rules for the docs artifacts that describe it |

## 2. Task dependency table

| Task | Depends on | Why |
| --- | --- | --- |
| DV-T1 | none | Establishes the truthful portfolio boundary and owner authority before stronger claims are made |
| DV-T2 | DV-T1 | Validator labels and fixtures should reflect the approved docs-only claim boundary |
| DV-T3 | DV-T1, DV-T2 | A spec should not be handed off as ready until both the owner boundary and structural verification bar are explicit |

## 3. Tasks

### DV-T1 — Confirm portfolio claim boundary and owner authority (DV-1, DV-2)

Prerequisites: none. Observed paths: `README.md`, `scripts/validate_specs.py`. Proposed paths: `docs/review/`, `docs/specs/README.md`.

1. Inspect the full portfolio index and current review docs to confirm whether “implementation-ready” means structural completeness only or substantive implementation feasibility.
2. Record who can approve: a) README/review wording changes, b) selection of a single `SPEC.md` for build handoff, and c) any move from synthetic/demo assumptions to real data or external contact.
3. Rewrite any ambiguous portfolio-facing language so the repository clearly distinguishes docs integrity from product readiness.

Expected deliverable: a portfolio-boundary decision note linked from the repo’s review material.

Verification: an independent reader should be able to answer, from the docs alone, whether the repo contains software, whether one spec or all 25 are approved for implementation, and who must authorize any real-data or pilot use.

- [ ] The docs-only boundary is explicit and consistent across README and review docs.
- [ ] The approval owner for spec selection and pilot boundary is named.
- [ ] “Implementation-ready” is defined or narrowed so it cannot be mistaken for shipped software.

### DV-T2 — Add regression-backed structural verification for the portfolio validator (DV-3)

Prerequisites: DV-T1. Observed path: `scripts/validate_specs.py`. Proposed paths: `tests/`, `fixtures/`, workflow or documented local verification path.

1. Extract the validator’s real invariants from source: heading presence, source-link coverage, acceptance-ID traceability, line-count floors, local links, placeholders, and portfolio totals.
2. Create isolated broken fixtures for at least missing heading, broken local link, changed source requirement text, and incorrect aggregate counts.
3. Add a repeatable verification path that runs the validator and fixture-based negative tests while explicitly labeling the outcome as document-structure assurance only.

Expected deliverable: regression fixtures plus documented verification instructions for structural portfolio checks.

Verification: intentionally break one fixture per invariant and confirm the relevant failure message appears; then restore the fixture and confirm the suite passes without changing the substantive claim boundary.

- [ ] Each key invariant has at least one negative fixture.
- [ ] Verification output distinguishes structural validation from feasibility/security assurance.
- [ ] Future maintainers can rerun the docs checks from documented instructions without guessing commands.

### DV-T3 — Gate single-spec handoff, docs release, rollback, and recovery (DV-1, DV-2)

Prerequisites: DV-T1 and DV-T2. Observed paths: selected `docs/specs/**/SPEC.md`, `docs/specs/README.md`, `docs/review/`. Proposed paths: implementation repo and handoff record for the chosen spec.

1. Choose one `SPEC.md` and review it in full against its source brief, README promises, and the owner-approved pilot boundary; record substantive open questions separately from structural ones.
2. Define the release gate for the documentation artifacts that advertise that spec: which files must be updated together, who approves the change, and what wording is allowed before implementation exists.
3. Define rollback and recovery for the portfolio artifacts themselves: how to revert an overstated README/spec claim, how to restore the last verified docs revision, and how to re-run structural checks after recovery.

Expected deliverable: a per-spec handoff record and a repository-level docs release/rollback/recovery procedure.

Verification: challenge the handoff with one unsupported claim from the chosen spec or README; the gate should block release until the claim is removed, narrowed, or evidenced. Then simulate a docs rollback by identifying the prior verified revision and confirming the recovery procedure returns the portfolio to that state.

- [ ] One chosen spec has substantive review notes, not just a validator pass.
- [ ] Docs release rules identify approver, affected files, and allowed claim scope.
- [ ] Rollback and recovery steps restore a prior verified documentation revision.

## 4. Dependency map

`DV-T1 → DV-T2 → DV-T3`

## 5. Acceptance checklist

This is a **portfolio acceptance checklist**, not a product go-live checklist.

- [ ] README, review docs, and validator messaging agree that this repo is documentation-only at the sampled SHA.
- [ ] One owner is accountable for approving spec-selection and pilot-boundary changes.
- [ ] Structural validation can be rerun and shown to fail on deliberately broken fixtures.
- [ ] At least one chosen spec has a substantive handoff review before being presented as ready for build.
- [ ] Any claim about real data, paid inference, external contact, or production pilot names the approving authority.

## 6. Changes requiring owner approval

- Selecting which of the 25 specs is next for implementation.
- Any wording that could be read as a claim of working software or deployment readiness.
- Any expansion from synthetic/demo assumptions to real data, external contact, paid inference, or pilot commitments.
- Any publication of a review or README update that changes readiness language.

## 7. Release, rollback, and recovery policy

**Release gate:** publish docs changes only after the portfolio boundary wording is reviewed, the structural verification path is rerun, and the changed README/spec/review files are checked together for consistent claims.

**Rollback:** if a docs revision overstates readiness or breaks portfolio integrity, revert to the last verified documentation revision rather than patching wording ad hoc in place.

**Recovery:** after rollback or accidental drift, restore the last verified docs revision, rerun the documented structural checks, and re-confirm owner approval before republishing the affected README/spec/review files.

## 8. Independent verification expectations

Negative tests must fail on purposefully broken fixtures. A green docs validator is not evidence that any future product is feasible, secure, accessible, or deployable. Any later implementation review must happen in the selected product repository, against actual code and runtime behavior, not by reusing this portfolio-only pass.
