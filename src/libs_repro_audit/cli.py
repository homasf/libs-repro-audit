"""Command-line interface.

Usage:
    libs-audit examples/elsaeed2025_scirep.json          # console summary
    libs-audit myrecord.json -o report.html              # styled HTML report
    libs-audit myrecord.json -o report.md                # Markdown report
    libs-audit --worked-example --strict                 # CI gate
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .engine import (FAIL, INFO, NOT_INVERTIBLE, NOT_REPORTED, PASS,
                     REPORTED, load_record, render_markdown, run_audit)
from .htmlreport import render_html

_COLORS = {PASS: "\033[32m", REPORTED: "\033[32m", FAIL: "\033[31m",
           NOT_INVERTIBLE: "\033[31m", NOT_REPORTED: "\033[33m",
           INFO: "\033[36m"}
_RESET, _BOLD, _DIM = "\033[0m", "\033[1m", "\033[2m"


def _c(code: str, text: str, enable: bool) -> str:
    return f"{code}{text}{_RESET}" if enable else text


def _banner(color: bool) -> str:
    line = "─" * 62
    return (_c(_DIM, f"┌{line}┐\n", color)
            + _c(_DIM, "│ ", color)
            + _c(_BOLD, f"libs-repro-audit v{__version__}", color)
            + "  ·  CF-LIBS/LIPS reproducibility audit (A1–A5)"
            + _c(_DIM, " │\n", color)
            + _c(_DIM, f"└{line}┘", color))


def _worked_example_path() -> Path:
    source_tree = (Path(__file__).resolve().parents[2] / "examples"
                   / "elsaeed2025_scirep.json")
    if source_tree.exists():
        return source_tree
    return Path(__file__).resolve().with_name("elsaeed2025_scirep.json")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="libs-audit",
        description="Rerun the A1-A5 reproducibility checks on a "
                    "CF-LIBS/LIPS audit record (JSON of printed values).")
    ap.add_argument("record", nargs="?", help="path to an audit-record JSON")
    ap.add_argument("--worked-example", action="store_true",
                    help="audit the bundled worked-example record")
    ap.add_argument("-o", "--output",
                    help="write a report here (.html -> styled HTML, "
                         "otherwise Markdown)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any check is FAIL, NOT_INVERTIBLE or "
                         "NOT_REPORTED (useful in CI)")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args(argv)

    color = sys.stdout.isatty() and not args.no_color
    print(_banner(color))

    path = _worked_example_path() if (args.worked_example or not args.record) \
        else Path(args.record)
    if not args.record and not args.worked_example:
        print(_c(_DIM, f"(no record given — auditing bundled worked "
                       f"example: {path.name})", color))

    record = load_record(path)
    if "UNVERIFIED" in str(record.get("verification", "")):
        print(_c("\033[33m",
                 "⚠ this record is an UNVERIFIED DRAFT (LLM-extracted). "
                 "Verify every value against the PDF before citing this "
                 "report — see AGENT_GUIDE.md.", color))

    report = run_audit(record)

    title = report.paper.get("title", "(untitled)")
    print(f"\n{_c(_BOLD, 'Audited publication:', color)} {title}")
    print(_c(_DIM, "Scope: internal numerical reproducibility of the "
                   "printed record only.", color) + "\n")

    for r in report.results:
        pill = _c(_COLORS.get(r.status, ""), f"[{r.status:>14}]", color)
        print(f"  {r.checkpoint}  {pill}  {r.name}")
        print(f"      {_c(_DIM, r.detail, color)}")

    counts = report.counts()
    bad = report.failed()
    print(f"\n{_c(_BOLD, 'Summary:', color)} "
          + "  ".join(_c(_COLORS.get(s, ''), f"{s} {n}", color)
                      for s, n in counts.items()))
    print(f"{len(report.results)} checks run · "
          f"{len(bad)} reproducibility findings")

    if args.output:
        out = Path(args.output)
        text = render_html(report) if out.suffix.lower() in (".html", ".htm") \
            else render_markdown(report)
        out.write_text(text, encoding="utf-8")
        print(f"report written to {out}")

    return 1 if (args.strict and bad) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
