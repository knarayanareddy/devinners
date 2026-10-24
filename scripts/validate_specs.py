#!/usr/bin/env python3
"""Validate the documentation-only project specification portfolio.

No third-party packages or network access are required. This validates document
structure and traceability; it does not claim that any specified product exists.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SPECS_ROOT = ROOT / "docs/specs"
INDEX = SPECS_ROOT / "README.md"

REQUIRED_HEADINGS = [
    "## 1. Product contract",
    "## 2. End-to-end workflows and state",
    "## 3. Functional requirements",
    "## 4. Domain model and persistence",
    "## 5. Technical architecture",
    "## 6. Agent, model, and tool boundary",
    "## 7. Deterministic domain and decision policy",
    "## 8. UI and UX build plan",
    "## 9. Security, privacy, and abuse controls",
    "## 10. Non-functional requirements and observability",
    "## 11. Seed data, evaluation, and demonstration",
    "## 12. Implementation sequence and ownership",
    "## 13. Verification and acceptance traceability",
    "## 14. Completion rubric and definition of done",
    "## 15. Pilot boundary and change control",
]

SOURCE_CRITERION = re.compile(r"^- \*\*([A-Z]+-\d+)[^*]*:\*\*\s*(.+)$", re.M)
SPEC_CRITERION_ROW = re.compile(r"^\| ([A-Z]+-\d+) \|", re.M)
LOCAL_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
PLACEHOLDER = re.compile(r"\b(?:TBD|TODO|FIXME|lorem ipsum)\b", re.I)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def source_files() -> list[Path]:
    general = sorted(SPECS_ROOT.glob("2026-10-23-*-spec.md"))
    cinema = sorted((SPECS_ROOT / "agentic-cinema").glob("[0-9][0-9]-*.md"))
    return general + cinema


def spec_files() -> list[Path]:
    general = sorted(p for p in SPECS_ROOT.glob("*/SPEC.md"))
    cinema = sorted((SPECS_ROOT / "agentic-cinema").glob("*/SPEC.md"))
    return general + cinema


def source_link(text: str) -> str | None:
    match = re.search(r"^\*\*Source brief:\*\* \[[^]]+\]\(([^)]+)\)", text, re.M)
    return match.group(1) if match else None


def section(text: str, start: str, end: str) -> str:
    try:
        return text.split(start, 1)[1].split(end, 1)[0]
    except IndexError:
        return ""


def validate_structure(specs: list[Path], sources: list[Path], errors: list[str]) -> tuple[int, int]:
    expected_sources = {p.resolve() for p in sources}
    linked_sources: set[Path] = set()
    all_new_ids: list[str] = []
    total_source_criteria = 0
    total_lines = 0

    if len(sources) != 25:
        fail(errors, f"Expected 25 historical project briefs, found {len(sources)}")
    if len(specs) != 25:
        fail(errors, f"Expected 25 detailed SPEC.md files, found {len(specs)}")

    for spec in specs:
        rel = spec.relative_to(ROOT)
        text = spec.read_text(encoding="utf-8")
        lines = text.splitlines()
        total_lines += len(lines)

        if len(lines) < 500:
            fail(errors, f"{rel}: only {len(lines)} lines; expected a complete build pack (>=500)")
        if text.count("```") % 2:
            fail(errors, f"{rel}: unbalanced fenced code blocks")
        if len(re.findall(r"^# ", text, re.M)) != 1:
            fail(errors, f"{rel}: expected exactly one document H1")
        for heading in REQUIRED_HEADINGS:
            if heading not in text:
                fail(errors, f"{rel}: missing heading `{heading}`")
        if PLACEHOLDER.search(text):
            fail(errors, f"{rel}: unfinished placeholder marker found")
        if "How to use this document" not in text or "sole normative" not in text:
            fail(errors, f"{rel}: missing standalone-use contract")
        if "Impeccable / UI UX Pro Max-style" not in text or "WCAG 2.2 AA" not in text:
            fail(errors, f"{rel}: missing design-review/accessibility baseline")

        link = source_link(text)
        if not link:
            fail(errors, f"{rel}: missing historical Source brief link")
            continue
        source = (spec.parent / link).resolve()
        linked_sources.add(source)
        if not source.is_file():
            fail(errors, f"{rel}: source brief does not exist: {link}")
            continue

        source_text = source.read_text(encoding="utf-8")
        criteria = SOURCE_CRITERION.findall(source_text)
        if not criteria:
            fail(errors, f"{rel}: no source criteria parsed from {source.relative_to(ROOT)}")
            continue
        total_source_criteria += len(criteria)
        spec_ids = SPEC_CRITERION_ROW.findall(text)
        all_new_ids.extend(spec_ids)

        for old_id, requirement in criteria:
            new_id = re.sub(r"^MW-", "MUS-", old_id) if spec.parent.name == "museumworld" else old_id
            if new_id not in spec_ids:
                fail(errors, f"{rel}: missing acceptance row {new_id} (source {old_id})")
            escaped_requirement = requirement.replace("|", "\\|")
            if escaped_requirement not in text:
                fail(errors, f"{rel}: source requirement text changed or omitted for {new_id}")

        ui = section(text, "### 8.2 Information architecture and screens", "### 8.3 Component and interaction specification")
        route_count = len(re.findall(r"^\| /", ui, re.M))
        if route_count < 5:
            fail(errors, f"{rel}: expected at least 5 concrete UI routes, found {route_count}")

        evaluation = section(text, "### 11.2 Evaluation contract", "### 11.3 Scripted end-to-end demo")
        metric_count = len(re.findall(r"^\| [^|]+ \| [^|]+ \|$", evaluation, re.M))
        if metric_count < 4:
            fail(errors, f"{rel}: expected at least 4 evaluation metrics, found {metric_count}")

        rubric = section(text, "### 14.1 Weighted score (100 points)", "**Score rule:**")
        weights = [int(value) for value in re.findall(r"^\| [^|]+ \| (\d+) \|", rubric, re.M)]
        if len(weights) != 7 or sum(weights) != 100:
            fail(errors, f"{rel}: rubric must have 7 categories totaling 100, found {weights}")

        if spec.parent.name == "museumworld" and "ID migration" not in text:
            fail(errors, f"{rel}: missing MW-to-MUS source ID migration note")

    missing_sources = expected_sources - linked_sources
    unknown_sources = linked_sources - expected_sources
    for source in sorted(missing_sources):
        fail(errors, f"No detailed spec links historical brief {source.relative_to(ROOT)}")
    for source in sorted(unknown_sources):
        fail(errors, f"Detailed specs link unexpected source {source}")

    duplicates = [key for key, count in Counter(all_new_ids).items() if count != 1]
    if duplicates:
        fail(errors, f"Acceptance IDs are not globally unique: {duplicates}")
    if len(all_new_ids) != total_source_criteria:
        fail(errors, f"Criteria count mismatch: {total_source_criteria} source vs {len(all_new_ids)} detailed rows")

    return total_source_criteria, total_lines


def resolved_markdown_links(document: Path) -> set[Path]:
    resolved: set[Path] = set()
    text = document.read_text(encoding="utf-8")
    for raw in LOCAL_LINK.findall(text):
        target = raw.strip().strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
            continue
        # No current document uses titles in local links; fail closed rather than
        # silently skipping an unusual target in the link validator below.
        resolved.add((document.parent / target).resolve())
    return resolved


def validate_links(index: Path, specs: list[Path], errors: list[str]) -> int:
    documents = list((ROOT / "docs").rglob("*.md")) + [ROOT / "README.md"]
    checked = 0
    for document in documents:
        if not document.is_file():
            continue
        for target in resolved_markdown_links(document):
            checked += 1
            if not target.exists():
                fail(errors, f"{document.relative_to(ROOT)}: broken local link {target}")

    index_links = resolved_markdown_links(index)
    expected = {p.resolve() for p in specs}
    linked_specs = {p for p in index_links if p.name == "SPEC.md"}
    for missing in sorted(expected - linked_specs):
        fail(errors, f"Portfolio index does not link {missing.relative_to(ROOT)}")
    for unexpected in sorted(linked_specs - expected):
        fail(errors, f"Portfolio index links unexpected spec {unexpected}")
    return checked


def main() -> int:
    errors: list[str] = []
    sources = source_files()
    specs = spec_files()
    criteria, lines = validate_structure(specs, sources, errors)
    links = validate_links(INDEX, specs, errors)

    if criteria != 258:
        fail(errors, f"Portfolio baseline changed unexpectedly: expected 258 source criteria, found {criteria}")

    if errors:
        print(f"Documentation validation FAILED with {len(errors)} issue(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Documentation validation passed.")
    print(f"  Projects:             {len(specs)} detailed / {len(sources)} historical")
    print(f"  Acceptance criteria:  {criteria} inherited, globally unique detailed IDs")
    print(f"  Detailed content:     {lines:,} lines")
    print(f"  Local links checked:  {links}")
    print("  Required sections:    product, state, data, architecture, API, agent, UI, security,")
    print("                        operations, evaluation, slices, acceptance, rubric, pilot")
    print("  Scope:                documentation integrity only; no product implementation claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
