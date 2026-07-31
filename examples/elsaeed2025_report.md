# CF-LIBS/LIPS reproducibility-audit report

**Audited publication:** Calibration-free picosecond LIPS for quantifying heavy metals in soils near Egyptian industrial sites
**DOI:** 10.1038/s41598-025-04395-5  |  **Record transcribed by:** Homa Saeidfirozeh on 2026-07-29

This report tests only whether the published numerical chain can be reconstructed from the printed values supplied in the audit record. It does not assess raw data, true concentrations or author intent, and a FAIL is a reproducibility finding, not an allegation.

## Summary

- PASS: 5
- FAIL: 8
- NOT_INVERTIBLE: 3
- NOT_REPORTED: 5
- INFO: 3

## Findings

| Checkpoint | Check | Status | Detail |
|---|---|---|---|
| A5 | `validation:Cd:Ne-based` | **FAIL** | delta = -6.61% lies OUTSIDE the stated ±1.0% interval |
| A5 | `validation:Cd:Te-based` | **FAIL** | delta = +8.88% lies OUTSIDE the stated ±1.0% interval |
| A5 | `validation:Zn:Ne-based` | **FAIL** | delta = -5.77% lies OUTSIDE the stated ±1.0% interval |
| A5 | `validation:Zn:Te-based` | **FAIL** | delta = -4.59% lies OUTSIDE the stated ±1.0% interval |
| A5 | `validation:Fe:Ne-based` | **PASS** | delta = -0.65% lies within the stated ±1.0% interval |
| A5 | `validation:Fe:Te-based` | **PASS** | delta = -0.65% lies within the stated ±1.0% interval |
| A5 | `validation:Ni:Ne-based` | **PASS** | delta = +0.23% lies within the stated ±1.0% interval |
| A5 | `validation:Ni:Te-based` | **PASS** | delta = +0.23% lies within the stated ±1.0% interval |
| A1 | `stark:S1-P1` | **FAIL** | printed FWHM gives 1.15x the comparison N_e; an effective W_s of 0.0438 nm would be required instead of the printed 0.0381 nm |
| A1 | `stark:S1-Ptest` | **FAIL** | printed FWHM gives 1.15x the comparison N_e; an effective W_s of 0.0437 nm would be required instead of the printed 0.0381 nm |
| A1 | `instrument:width` | **INFO** | Gaussian instrumental FWHM ~ 0.0086 nm at R = 75000 |
| A1 | `instrument:correction:S1-P1` | **INFO** | quadrature instrumental correction changes the FWHM by 0.16% (upper bound; Gaussian idealization) |
| A1 | `instrument:correction:S1-Ptest` | **INFO** | quadrature instrumental correction changes the FWHM by 0.20% (upper bound; Gaussian idealization) |
| A2 | `scale:Cd` | **FAIL** | operative exponent is 10^16 (gives 65.03), but the article states 10^17 — factor-of-ten inconsistency |
| A2 | `scale:Zn` | **FAIL** | operative exponent is 10^16 (gives 136.95), but the article states 10^17 — factor-of-ten inconsistency |
| A4 | `equation:Fe:Ne` | **NOT_INVERTIBLE** | printed slope is 0.0 — equation returns a constant and cannot be inverted for concentration; moreover the constant 1.566 does not equal the operative test value 1.54382 |
| A4 | `equation:Ni:Ne` | **NOT_INVERTIBLE** | printed slope is 0.0 — equation returns a constant and cannot be inverted for concentration; moreover the constant 1.563 does not equal the operative test value 1.54382 |
| A4 | `equation:Fe:Te` | **NOT_INVERTIBLE** | printed slope is 0.0 — equation returns a constant and cannot be inverted for concentration; moreover the constant 9118.16 does not equal the operative test value 9136.3 |
| A4 | `equation:Cd:Ne` | **PASS** | inversion gives 65.03, reproducing the printed estimate 65.02 |
| A3 | `qualitative:lte_check_reported` | **NOT_REPORTED** | explicit LTE check (e.g. McWhirter with inputs): NOT found in the printed record |
| A3 | `qualitative:optical_thinness_or_self_absorption_reported` | **NOT_REPORTED** | optical-thinness / self-absorption diagnostic for analytical lines: NOT found in the printed record |
| A3 | `qualitative:atomic_data_provenance_reported` | **NOT_REPORTED** | atomic/broadening-data source, version and access date: NOT found in the printed record |
| A3 | `qualitative:instrumental_width_reported` | **NOT_REPORTED** | numerical instrumental width / line-shape treatment: NOT found in the printed record |
| A3 | `qualitative:full_precision_coefficients_available` | **NOT_REPORTED** | full-precision coefficients or machine-actionable record: NOT found in the printed record |

## Interpretation guide

PASS: the printed claim follows from the printed values. FAIL: it does not; possible explanations include typographical errors, rounding, unreported full-precision coefficients or an undocumented calculation pathway — any of which the authors could resolve by clarification. NOT_INVERTIBLE: a printed equation cannot be used as described. NOT_REPORTED: a minimum reporting item (Table 3 of the framework paper) is absent from the printed record.
