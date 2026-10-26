# Devinners — implementation specification portfolio

This repository contains **25 standalone, implementation-ready product specifications** and an end-to-end review of the original documentation. It does not contain implementations of those products.

## Start here

- **[Project specification index](docs/specs/README.md)** — all 25 detailed build packs, completion labels, and UI/UX baseline.
- **[End-to-end repository review (2026-10-26)](docs/review/2026-10-26-end-to-end-review.md)** — current inventory, independent audit results, and open findings.
- **[Independent-spec deep review (2026-10-26)](docs/review/2026-10-26-independent-specs-deep-review.md)** — per-document strengths, gaps, and consistency findings for the index + 10 independent-agent specifications.
- **[End-to-end repository review (2026-10-24)](docs/review/2026-10-24-end-to-end-review.md)** — original findings, remediations, residual risks, and recommended rollout.
- **[Original independent-agent briefs](docs/specs/2026-10-23-agent-project-spec-pack.md)** and **[Agentic Cinema briefs](docs/specs/agentic-cinema/README.md)** — historical provenance.

## Use one specification

Choose one row in the index and hand its `SPEC.md` to an implementation agent. Each document is self-contained and includes:

- Product scope, actors, fixed synthetic-demo decisions, and non-goals.
- End-to-end journeys, lifecycle/state rules, aggregates, invariants, and persistence.
- Reference stack/repository layout, HTTP API semantics, background jobs, and integrations.
- Agent/tool/model boundaries and deterministic domain algorithms.
- Screen-by-screen UI planning, components, responsive behavior, and WCAG 2.2 AA requirements.
- Security/privacy/retention, observability, performance budgets, seed data, evaluation, and demo.
- Implementation slices, all original acceptance criteria, a 100-point rubric, and hard completion gates.

Build each product in a **new standalone repository**. The default path uses synthetic/licensed fixtures and sandbox effects. Real data, paid inference, external contact, and production pilots require separate authorization.

## Validate this documentation

```bash
make verify-docs
```

The validator uses only the Python standard library. It checks all 25 specifications, 258 inherited acceptance criteria, unique IDs, required sections, portfolio links, and unfinished placeholders.

## Repository layout

```text
docs/
├── review/
│   └── 2026-10-24-end-to-end-review.md
└── specs/
    ├── README.md                       # portfolio index
    ├── <project>/SPEC.md               # 10 independent products
    ├── 2026-10-23-*.md                 # original independent briefs
    └── agentic-cinema/
        ├── <project>/SPEC.md           # 15 cinema/media products
        └── [0-9][0-9]-*.md             # original cinema briefs
scripts/
└── validate_specs.py                   # standard-library documentation checks
```

**Current maturity:** specified, not implemented. Do not infer working software, live integrations, measured user impact, production readiness, legal/compliance correctness, or contest qualification from these documents.
