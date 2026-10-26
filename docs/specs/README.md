# Project specification portfolio

**Repository status:** documentation only; none of the 25 products is implemented by this repository.<br>
**Detailed specification baseline:** 2026-10-24<br>
**Validation:** run `make verify-docs` from the repository root.

This portfolio contains **25 standalone product specifications**. Each `SPEC.md` is designed to be handed to an implementation agent on its own. It includes product scope, fixed demo decisions, actors, workflows, state, domain records, invariants, architecture, API endpoints, agent/tool boundaries, deterministic policies, UI routes/components/states, accessibility, security, operations, seeded evaluation, implementation slices, acceptance traceability, and a weighted completion rubric.

The dated short briefs are retained for provenance. The detailed `SPEC.md` supersedes its corresponding short brief for implementation. A specification passing review is not evidence that the product, integration, deployment, or pilot exists.

## How to use a build specification

1. Choose **one** project and create a separate standalone repository for it. Do not combine all 25 products into one application.
2. Give the implementation agent only that project's `SPEC.md` initially. The document is self-contained; the linked short brief is historical, not an additional set of requirements.
3. Before coding, create the required acceptance matrix mapping every criterion to a module, test/manual procedure, expected result, and evidence artifact.
4. Build the deterministic domain kernel and offline vertical slice first. Use the real agent/tool/policy/state path with scripted model responses; do not bypass it with a demo controller.
5. Keep external effects sandboxed. Real provider calls, external contact, production data, and paid spend require separate authorization and live evidence.
6. Do not weaken tests, thresholds, fixture labels, security gates, or accessibility requirements to obtain a passing score.

## Completion labels

| Label | Meaning |
| --- | --- |
| **Specified** | The normative build document exists and passes repository documentation validation. This is the current state. |
| **Offline complete** | The clean-clone setup, verification, real browser demo, and evaluation pass with synthetic data and sandbox effects; all core criteria and hard gates pass. |
| **Integrated complete** | Required live/provider/MCP/hosting criteria also pass with retained, sanitized evidence. Never inferred from screenshots or fixtures. |
| **Pilot approved** | A named partner has separately approved real data, consent, policy/source ownership, retention, staffing, security, and rollback. Not granted by tests or a demo. |

The 100-point rubric in each specification cannot compensate for a non-compensable safety, privacy, authorization, provenance, or truthfulness failure.

## Independent agent products — 10

| # | Project | Detailed build specification | Original criteria | Primary build focus |
| --- | --- | --- | ---: | --- |
| 01 | GrantSnap | [Open `SPEC.md`](grantsnap/SPEC.md) | 12 | Evidence-grounded expense intake, deterministic money/rules, packet approval/export |
| 02 | VolunteerBalance | [Open `SPEC.md`](volunteerbalance/SPEC.md) | 11 | Private constraints, CP-SAT allocation, fairness explanations, individual consent |
| 03 | BridgeMentor | [Open `SPEC.md`](bridgementor/SPEC.md) | 11 | Approved public cards, deterministic eligibility/ranking, mutual consent |
| 04 | ToolTutor | [Open `SPEC.md`](tooltutor/SPEC.md) | 11 | Signed procedures, one-step evidence gate, hazard precedence |
| 05 | StreetVendor Radar | [Open `SPEC.md`](streetvendor-radar/SPEC.md) | 11 | Enumerated source monitoring, cited relevance, auditable rejection/freshness |
| 06 | UtilityShield | [Open `SPEC.md`](utilityshield/SPEC.md) | 11 | Reviewed clock rules, evidence triage, capacity-safe queue, human packets |
| 07 | LibraryLoop | [Open `SPEC.md`](libraryloop/SPEC.md) | 11 | Typed policies, historical replay, separate activation, verified internal effects |
| 08 | ColdWatch | [Open `SPEC.md`](coldwatch/SPEC.md) | 11 | Consent/activation gates, bounded sandbox outreach, human escalation |
| 09 | CenterSignal | [Open `SPEC.md`](centersignal/SPEC.md) | 11 | Exact provider readback, atomic status evidence, freshness and failure reports |
| 10 | SchoolNotice | [Open `SPEC.md`](schoolnotice/SPEC.md) | 10 | Source-grounded family cards, constrained translation, privacy and safe actions |

Historical index: [Agent project spec pack](2026-10-23-agent-project-spec-pack.md).

## Agentic Cinema alternate products — 15

The original event's submission period has closed. These are independent build blueprints, not contest entries or qualification claims. Partner requirements must be rechecked against current official resources before making any track claim. Offline and integrated completion are reported separately.

| # | Track | Project | Detailed build specification | Original criteria | Primary build focus |
| --- | --- | --- | --- | ---: | --- |
| 01 | IBM | StageLine | [Open `SPEC.md`](agentic-cinema/stageline/SPEC.md) | 9 | Rehearsal alignment, continuity candidates, human ledger |
| 02 | IBM | SecondUnit Match | [Open `SPEC.md`](agentic-cinema/secondunit-match/SPEC.md) | 10 | Pickup/reference evidence, editor dispositions, EDL correctness |
| 03 | IBM | CrewClock | [Open `SPEC.md`](agentic-cinema/crewclock/SPEC.md) | 10 | Constraint provenance, honest solver states, schedule approval |
| 04 | Grafana | PremiereWatch | [Open `SPEC.md`](agentic-cinema/premierewatch/SPEC.md) | 10 | Package matrix, Grafana MCP evidence, no false-green release |
| 05 | Grafana | SportsCaption SLO | [Open `SPEC.md`](agentic-cinema/sportscaption-slo/SPEC.md) | 10 | Accessible-track probes, SLO semantics, mitigation regression gates |
| 06 | Grafana | MixWatch | [Open `SPEC.md`](agentic-cinema/mixwatch/SPEC.md) | 10 | Infrastructure/content separation, deterministic audio checks, safe retry |
| 07 | Parallel | Fieldnote Desk | [Open `SPEC.md`](agentic-cinema/fieldnote-desk/SPEC.md) | 10 | Confidentiality-before-egress, public-claim search, cited scripts |
| 08 | Parallel | Rights Ledger | [Open `SPEC.md`](agentic-cinema/rights-ledger/SPEC.md) | 10 | Quote-grounded grants, exact scope matching, no legal verdict |
| 09 | Parallel | Archive Dossier | [Open `SPEC.md`](agentic-cinema/archive-dossier/SPEC.md) | 10 | Bounded research, extraction states, contradictions, coverage |
| 10 | ClickHouse | RunOfShow | [Open `SPEC.md`](agentic-cinema/runofshow/SPEC.md) | 10 | ClickHouse history, cue coverage, deterministic recovery planning |
| 11 | ClickHouse | Podcast Pulse | [Open `SPEC.md`](agentic-cinema/podcast-pulse/SPEC.md) | 9 | Aggregate retention metrics, delivery confounders, causal humility |
| 12 | ClickHouse | AssetFinder | [Open `SPEC.md`](agentic-cinema/assetfinder/SPEC.md) | 10 | Rights-filtered vector retrieval, grounded fit, deletion lineage |
| 13 | Replit | MuseumWorld | [Open `SPEC.md`](agentic-cinema/museumworld/SPEC.md) | 10 | Curator-authored graphs, grounded narration, isolated deterministic play |
| 14 | Replit | CaptionProof | [Open `SPEC.md`](agentic-cinema/captionproof/SPEC.md) | 10 | Evidence-bound caption suggestions, editor batches, valid exports |
| 15 | Replit | ScriptBudget | [Open `SPEC.md`](agentic-cinema/scriptbudget/SPEC.md) | 10 | Grounded screenplay breakdown, exact costs/schedules, no success prediction |

Historical index: [Agentic Cinema portfolio](agentic-cinema/README.md).

**ID note:** the two historical briefs for MixWatch and MuseumWorld both used `MW-01`–`MW-10`. Detailed specifications use `MW-*` for MixWatch and globally unique `MUS-*` for MuseumWorld, with an explicit source mapping in the MuseumWorld document.

## UI and UX quality baseline

Every project specification includes:

- A project-specific visual direction and semantic CSS token starter.
- Desktop/mobile information architecture, named routes, screen content, and primary actions.
- Component behavior for evidence, status, jobs, approvals, tables, and domain-specific interactions.
- Loading, empty, partial/unknown, error/offline, success, approval, and refusal states.
- Keyboard, screen-reader, 200%/400% zoom, reduced-motion, target-size, contrast, focus, and plain-language requirements.
- An **Impeccable / UI UX Pro Max-style craft review lens** covering hierarchy, typography, spacing, color, realistic content, interaction completeness, responsiveness, accessibility, and copy. These are design-review references, not dependencies or substitutes for the normative **WCAG 2.2 AA** checks.

## Repository validation

`make verify-docs` checks that:

- All 25 detailed specifications exist and contain every required section.
- All 258 historical acceptance statements are represented, with MuseumWorld's collision-safe ID mapping.
- Acceptance IDs are unique across the detailed portfolio.
- Each document has substantial UI, verification, evaluation, and completion-rubric content.
- Local Markdown links resolve and no unfinished placeholder markers are present.
- This index links every detailed specification.

See the [2026-10-26 end-to-end repository review](../review/2026-10-26-end-to-end-review.md) for current findings and next steps, and the [2026-10-24 review](../review/2026-10-24-end-to-end-review.md) for the original remediation history.
