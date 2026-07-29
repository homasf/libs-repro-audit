# libs-repro-audit

![audit-checks](https://github.com/homasf/libs-repro-audit/actions/workflows/ci.yml/badge.svg)
![python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-green)

Executable, machine-actionable record accompanying:

> Homa Saeidfirozeh and M. Ferus, *A reproducibility-audit framework for
> calibration-free LIBS/LIPS quantification: proposed minimum reporting
> requirements and a worked case study.*

The article proposes a five-checkpoint audit (A1–A5) for testing whether a
published CF-LIBS/LIPS calculation chain can be reconstructed from the
printed record, and its Table 3 asks quantitative studies to supply a
machine-actionable supplement. This repository is that supplement for the
audit paper itself: every numerical result in the paper is regenerated here
from printed values only, under automated tests.

**No raw spectra are used and no new measurements are made.** All inputs are
central values printed in the case-study article (El-Saeed et al., *Sci.
Rep.* 15 (2025) 19949) as transcribed in `data/printed_values.json`, with a
source annotation for each block. The audit concerns internal numerical
reproducibility of the published record only; it does not assess the true
sample concentrations or author intent.

## What is reproduced

| Paper item | Checkpoint | Where |
|---|---|---|
| Table 1 — signed relative deviations vs ICP-OES, Eq. (1) | A5 | `report.table1_rows`, `output/table1_signed_deviations.csv` |
| Figure 2 — deviation bar chart with ±1% band | A5 | `scripts/make_figure2.py` |
| Table 2 — Ca I 646.257 nm FWHM vs Stark Eq. (2), ratio *R* ≈ 1.15, effective *W*ₛ ≈ 0.044 nm | A1/A2 | `report.table2_rows`, `output/table2_linewidth_check.csv` |
| Instrumental-width bound at R = 75,000 (< 0.5% change) | A1 | `audit.instrumental_fwhm`, `audit.quadrature_corrected_fwhm` |
| Electron-density scale check, Eqs. (3)–(4): 10¹⁶ reproduces 65.03 / 136.95 ppm; 10¹⁷ does not | A2/A4 | `audit.ne_scale_check` |
| Fe/Ni zero-slope equations are non-invertible; constants mismatch the test-sample parameters | A4 | `audit.LinearEquation` |

## Quick start

```bash
git clone https://github.com/homasf/libs-repro-audit.git
cd libs-repro-audit
python -m pip install -e ".[dev]"

# regenerate all tables and checks
python -m libs_repro_audit

# run the assertion suite (every printed number in the paper)
pytest -v

# regenerate Figure 2
python scripts/make_figure2.py
```

`python -m libs_repro_audit` prints Tables 1–2, the scale check and the
invertibility audit to the console and writes CSV copies to `output/`.

## Design

- `data/printed_values.json` — the machine-actionable record: every printed
  input value with units, exponents and a provenance note. Changing a value
  here and re-running `pytest` shows exactly which published numbers depend
  on it.
- `src/libs_repro_audit/audit.py` — one small, documented function per
  deterministic check (Eq. (1) deviation, Eq. (2) Stark density, effective
  Stark width, instrumental-width bound, linear-equation inversion and
  invertibility, power-of-ten scale check).
- `tests/test_audit.py` — assertions pinning each recalculated value to the
  number printed in the paper. A failing test means the executable record no
  longer reproduces the published tables — precisely the condition the
  framework is designed to detect.
- CI (GitHub Actions) reruns the suite on every push on Python 3.9 and 3.12.

## Auditing ANY other CF-LIBS/LIPS paper (v2 engine)

The repository now contains a general, paper-independent audit engine with
a command-line interface:

```bash
# audit the bundled worked example
libs-audit --worked-example

# audit another paper: copy the template, fill it with printed values
cp examples/template.json mypaper.json
#   ... transcribe values from the paper's tables/equations ...
libs-audit mypaper.json -o mypaper_report.html   # styled, self-contained HTML
libs-audit mypaper.json -o mypaper_report.md     # plain Markdown

# in CI: exit non-zero if anything fails to reproduce
libs-audit mypaper.json --strict
```

The audit record (`examples/template.json`) is a JSON file of the paper's
*printed* values — validation points and stated tolerance, Stark
parameters and FWHMs, empirical-equation coefficients, candidate
exponents, and reported/not-reported flags for LTE, self-absorption and
atomic-data provenance. The engine reruns checkpoints A1–A5 and emits a
Markdown report in which every check is labelled PASS, FAIL,
NOT_INVERTIBLE or NOT_REPORTED, with the arithmetic shown.
`examples/elsaeed2025_report.md` is the report the engine generates for
the worked example; it reproduces all four findings of the framework
paper automatically.

A FAIL means "not reproducible from the printed record" — typographical
errors, rounding or unreported full-precision coefficients can all cause
one, and all are resolvable by author clarification. The report text says
this explicitly.

## AI-assisted extraction

Transcribing values from a PDF is the tedious step, and it is the one
place a language model helps. `AGENT_GUIDE.md` defines a strict two-stage
workflow: the `libs-audit-extract` command drafts the audit record from the paper's
text via the Anthropic API using a constrained extraction prompt (no estimation, conflicts recorded not resolved, source
note per value), a human verifies every number against the paper, and the
deterministic engine — never the model — renders the verdict. Drafts are
stamped UNVERIFIED and `libs-audit` prints a warning until a human replaces
the stamp with their name and date. Anyone can
rerun `libs-audit` on the same record and obtain the same report.

## Applying the audit to another study

The functions are generic. To audit a different CF-LIBS/LIPS paper, copy
`data/printed_values.json`, replace the printed inputs (keeping the
provenance notes), and rerun `python -m libs_repro_audit` and the relevant
checks. The JSON schema is intentionally minimal: validation table,
Stark parameters and linewidths, instrument resolving power, and the
empirical concentration equations.

## Citing

Cite the accompanying article and this software via the metadata in
`CITATION.cff`. Add the archived-release DOI here after Zenodo mints the
v2.0.0 record.

## License

MIT — see `LICENSE`.
