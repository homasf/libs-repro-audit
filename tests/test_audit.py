"""Every assertion below checks a number printed in the audit paper.

If any test fails, the executable record no longer reproduces the
published tables - which is precisely the condition the framework is
designed to detect.
"""

import math

import pytest

from libs_repro_audit.audit import (
    LinearEquation,
    effective_stark_width,
    instrumental_fwhm,
    load_printed_values,
    ne_scale_check,
    quadrature_corrected_fwhm,
    signed_relative_deviation,
    stark_ne,
)
from libs_repro_audit.report import table1_rows, table2_rows


@pytest.fixture(scope="module")
def data():
    return load_printed_values()


# ---------------------------------------------------------------- A5 --

# (element, delta_Ne %, delta_Te %) as printed in Table 1 / Figure 2
TABLE1_EXPECTED = {
    "Cd": (-6.61, 8.88),
    "Zn": (-5.77, -4.59),
    "Fe": (-0.65, -0.65),
    "Ni": (0.23, 0.23),
}


def test_table1_signed_deviations(data):
    rows = {r["element"]: r for r in table1_rows(data)}
    for element, (d_ne, d_te) in TABLE1_EXPECTED.items():
        assert rows[element]["delta_ne_percent"] == pytest.approx(d_ne, abs=0.005)
        assert rows[element]["delta_te_percent"] == pytest.approx(d_te, abs=0.005)


def test_cd_zn_outside_stated_interval(data):
    rows = {r["element"]: r for r in table1_rows(data)}
    for element in ("Cd", "Zn"):
        assert abs(rows[element]["delta_ne_percent"]) > 1.0
        assert abs(rows[element]["delta_te_percent"]) > 1.0
    for element in ("Fe", "Ni"):
        assert abs(rows[element]["delta_ne_percent"]) <= 1.0
        assert abs(rows[element]["delta_te_percent"]) <= 1.0


def test_deviation_range_matches_conclusion(data):
    rows = table1_rows(data)
    magnitudes = [
        abs(v) for r in rows for v in (r["delta_ne_percent"], r["delta_te_percent"])
    ]
    assert min(magnitudes) == pytest.approx(0.23, abs=0.005)
    assert max(magnitudes) == pytest.approx(8.88, abs=0.005)


# ------------------------------------------------------------- A1/A2 --

def test_table2_stark_check(data):
    rows = {r["sample"]: r for r in table2_rows(data)}
    assert rows["S1-P1"]["ne_calc_1e16_cm-3"] == pytest.approx(2.01, abs=0.005)
    assert rows["S1-Ptest"]["ne_calc_1e16_cm-3"] == pytest.approx(1.77, abs=0.005)
    for r in rows.values():
        assert r["ratio_R"] == pytest.approx(1.15, abs=0.005)
    assert rows["S1-P1"]["w_s_effective_nm"] == pytest.approx(0.0438, abs=5e-5)
    assert rows["S1-Ptest"]["w_s_effective_nm"] == pytest.approx(0.0437, abs=5e-5)


def test_effective_width_near_0_044(data):
    stark = data["stark"]
    for s in stark["samples"].values():
        w_eff = effective_stark_width(s["fwhm_nm"], s["ne_comparison_1e16"] * 1e16)
        assert w_eff == pytest.approx(0.044, abs=0.001)


def test_instrumental_correction_is_negligible(data):
    instr = data["instrument"]
    w_inst = instrumental_fwhm(
        instr["diagnostic_wavelength_nm"], instr["conditioned_resolving_power"]
    )
    assert w_inst == pytest.approx(0.0086, abs=2e-4)  # ~0.0086 nm as stated
    for s in data["stark"]["samples"].values():
        corrected = quadrature_corrected_fwhm(s["fwhm_nm"], w_inst)
        change = (s["fwhm_nm"] - corrected) / s["fwhm_nm"] * 100
        assert change < 0.5  # "changes the displayed linewidths by < ~0.5%"


# ------------------------------------------------------------- A2/A4 --

def test_cd_scale_check_eq3_eq4(data):
    coeffs = data["ne_concentration_equations"]["S1"]["Cd"]
    eq = LinearEquation(coeffs["a"], coeffs["b"])
    ne = data["test_sample"]["ne_printed"]["value"]
    scales = ne_scale_check(eq, ne)
    assert scales[16] == pytest.approx(65.03, abs=0.01)     # Eq. (4)
    assert scales[17] == pytest.approx(4.05e3, rel=0.01)    # 1e17 fails


def test_zn_scale_check(data):
    coeffs = data["ne_concentration_equations"]["S1"]["Zn"]
    eq = LinearEquation(coeffs["a"], coeffs["b"])
    ne = data["test_sample"]["ne_printed"]["value"]
    scales = ne_scale_check(eq, ne)
    assert scales[16] == pytest.approx(136.95, abs=0.01)
    assert scales[17] == pytest.approx(7.4e2, rel=0.01)


# ---------------------------------------------------------------- A4 --

def test_fe_ni_equations_not_invertible(data):
    for element in ("Fe", "Ni"):
        coeffs = data["ne_concentration_equations"]["S1"][element]
        eq = LinearEquation(coeffs["a"], coeffs["b"])
        assert not eq.invertible
        with pytest.raises(ZeroDivisionError):
            eq.invert(1.54382)


def test_fe_ni_constants_mismatch_test_sample(data):
    ne_test = data["test_sample"]["ne_printed"]["value"]
    for element, const in (("Fe", 1.566), ("Ni", 1.563)):
        a = data["ne_concentration_equations"]["S1"][element]["a"]
        assert a == const
        assert not math.isclose(a, ne_test, rel_tol=1e-3)
    te_const = data["te_concentration_equations"]["S1"]["Fe"]["a"]
    assert te_const == 9118.16
    assert te_const != data["test_sample"]["te_reported_K"]


# ------------------------------------------------------------ basics --

def test_eq1_definition():
    assert signed_relative_deviation(65.02, 69.62) == pytest.approx(-6.607, abs=1e-3)
    assert signed_relative_deviation(100.0, 100.0) == 0.0
    with pytest.raises(ZeroDivisionError):
        signed_relative_deviation(1.0, 0.0)


def test_eq2_definition():
    # N_e = FWHM / (2 W_s) * 1e16
    assert stark_ne(0.0762, 0.0381) == pytest.approx(1e16)
