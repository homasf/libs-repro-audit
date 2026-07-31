"""AI-assisted extraction agent (``cf-libs-audit-extract``).

Drafts an audit record from a paper's text using the Anthropic API, under
the strict extraction contract of AGENT_GUIDE.md. The agent NEVER judges
reproducibility — it only transcribes printed values into the record
schema. Every draft it writes is stamped ``"verification": "DRAFT —
UNVERIFIED"`` and ``cf-libs-audit`` refuses to treat such a record as final
until a human has checked each value against the PDF and replaced the
stamp with their name and date.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    pdftotext paper.pdf paper.txt          # or any text export
    cf-libs-audit-extract paper.txt -o draft_record.json
    #  -> verify every value against the PDF, fill 'verification'
    cf-libs-audit draft_record.json -o report.html

Requires the ``requests``-free standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

EXTRACTION_SYSTEM = """\
You are assisting with a reproducibility audit of a CF-LIBS/LIPS
publication. Fill the JSON template using ONLY values printed in the paper
text supplied by the user (tables, equations, figure axis labels,
accompanying text). Rules:
1. Never estimate, interpolate, round differently, or fill gaps from
   background knowledge. If a value is not printed, omit the field and list
   it under a top-level "missing" array instead.
2. For every block, fill the "source" field with the exact table, equation
   or section where the value appears.
3. Transcribe coefficients at full printed precision, including zero slopes
   (write 0.0, do not "fix" them).
4. If the paper states the same quantity with different exponents or units
   in different places, record each variant in a top-level "conflicts" array
   with locations; do not resolve the conflict.
5. For the "qualitative" block, set a flag true only if the diagnostic is
   explicitly reported with numerical inputs, not merely mentioned.
6. Respond with ONLY the completed JSON object — no preamble, no markdown
   fences."""


def _template() -> str:
    source_tree = (Path(__file__).resolve().parents[2] / "examples"
                   / "template.json")
    path = source_tree if source_tree.exists() else \
        Path(__file__).resolve().with_name("template.json")
    return path.read_text(encoding="utf-8")


def _call_api(api_key: str, paper_text: str) -> str:
    payload = {
        "model": MODEL,
        "max_tokens": 4000,
        "system": EXTRACTION_SYSTEM,
        "messages": [{
            "role": "user",
            "content": (
                "TEMPLATE:\n" + _template() +
                "\n\nPAPER TEXT:\n" + paper_text
            ),
        }],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return "".join(b.get("text", "") for b in data.get("content", [])
                   if b.get("type") == "text")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="cf-libs-audit-extract",
        description="Draft an audit record from paper text with an LLM. "
                    "The draft is UNVERIFIED until a human checks every "
                    "value against the PDF (see AGENT_GUIDE.md).")
    ap.add_argument("paper_text", help="plain-text export of the paper "
                                       "(e.g. from pdftotext)")
    ap.add_argument("-o", "--output", default="draft_record.json")
    args = ap.parse_args(argv)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("error: set the ANTHROPIC_API_KEY environment variable "
              "(the key is read from the environment and never stored).",
              file=sys.stderr)
        return 2

    text = Path(args.paper_text).read_text(encoding="utf-8", errors="replace")
    print(f"extracting printed values from {args.paper_text} "
          f"({len(text)} chars) with {MODEL} ...")
    raw = _call_api(api_key, text)
    raw = raw.strip().removeprefix("```json").removeprefix("```")
    raw = raw.removesuffix("```").strip()

    try:
        record = json.loads(raw)
    except json.JSONDecodeError as exc:
        Path(args.output + ".raw.txt").write_text(raw, encoding="utf-8")
        print(f"error: model output was not valid JSON ({exc}); raw output "
              f"saved to {args.output}.raw.txt for inspection.",
              file=sys.stderr)
        return 1

    record["verification"] = (
        "DRAFT — UNVERIFIED: a human must check every value against the "
        "PDF, then replace this field with 'verified by <name>, <date>'."
    )
    Path(args.output).write_text(json.dumps(record, indent=2),
                                 encoding="utf-8")
    print(f"draft written to {args.output}")
    print("NEXT STEP (required): verify every value against the paper — "
          "see the checklist in AGENT_GUIDE.md — before running "
          f"'cf-libs-audit {args.output}'.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
