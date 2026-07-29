"""The generic engine, run on the worked-example record, must reproduce
every finding reported in the framework paper."""

from pathlib import Path

import pytest

from libs_repro_audit.engine import (
    FAIL, NOT_INVERTIBLE, NOT_REPORTED, PASS,
    load_record, render_markdown, run_audit,
)

RECORD = Path(__file__).resolve().parents[1] / "examples" / "elsaeed2025_scirep.json"


@pytest.fixture(scope="module")
def report():
    return run_audit(load_record(RECORD))


def _by_name(report, prefix):
    return {r.name: r for r in report.results if r.name.startswith(prefix)}


def test_validation_findings(report):
    v = _by_name(report, "validation:")
    for name, r in v.items():
        element = name.split(":")[1]
        expected = FAIL if element in ("Cd", "Zn") else PASS
        assert r.status == expected, name
    deltas = {r.name: r.values["delta_percent"] for r in v.values()}
    assert deltas["validation:Cd:Ne-based"] == pytest.approx(-6.61, abs=0.005)
    assert deltas["validation:Cd:Te-based"] == pytest.approx(8.88, abs=0.005)


def test_stark_findings(report):
    s = _by_name(report, "stark:")
    assert len(s) == 2
    for r in s.values():
        assert r.status == FAIL
        assert r.values["ratio"] == pytest.approx(1.15, abs=0.005)
        assert r.values["w_s_effective_nm"] == pytest.approx(0.044, abs=0.001)


def test_scale_findings(report):
    s = _by_name(report, "scale:")
    for r in s.values():
        # operative exponent is 16 but the article states 17 -> FAIL
        assert r.status == FAIL
        assert r.values["matching_exponents"] == [16]
    assert s["scale:Cd"].values["per_exponent_ppm"][16] == pytest.approx(65.03, abs=0.01)
    assert s["scale:Zn"].values["per_exponent_ppm"][16] == pytest.approx(136.95, abs=0.01)


def test_equation_findings(report):
    e = _by_name(report, "equation:")
    assert e["equation:Fe:Ne"].status == NOT_INVERTIBLE
    assert e["equation:Ni:Ne"].status == NOT_INVERTIBLE
    assert e["equation:Fe:Te"].status == NOT_INVERTIBLE
    assert e["equation:Cd:Ne"].status == PASS  # invertible counter-example


def test_qualitative_findings(report):
    q = _by_name(report, "qualitative:")
    assert len(q) == 5
    assert all(r.status == NOT_REPORTED for r in q.values())


def test_markdown_renders(report):
    md = render_markdown(report)
    assert "reproducibility-audit report" in md
    assert "FAIL" in md and "NOT_INVERTIBLE" in md


def test_html_renders(report):
    from libs_repro_audit.htmlreport import render_html
    html_out = render_html(report)
    assert html_out.startswith("<!DOCTYPE html>")
    assert "Reproducibility-audit report" in html_out
    assert "NOT INVERTIBLE" in html_out and "PASS" in html_out
    assert "<script" not in html_out  # self-contained, no scripts


def test_packaged_json_resources_match_repository_records():
    root = Path(__file__).resolve().parents[1]
    package = root / "src" / "libs_repro_audit"
    pairs = (
        (root / "data" / "printed_values.json", package / "printed_values.json"),
        (root / "examples" / "elsaeed2025_scirep.json",
         package / "elsaeed2025_scirep.json"),
        (root / "examples" / "template.json", package / "template.json"),
    )
    for source, bundled in pairs:
        assert bundled.read_bytes() == source.read_bytes()
