"""Core numerical functions for the CF-LIBS/LIPS reproducibility audit.

Each function implements one deterministic check from the five-checkpoint
framework (A1-A5) described in:

    Homa Saeidfirozeh and M. Ferus,
    "A reproducibility-audit framework for calibration-free LIBS/LIPS
    quantification: proposed minimum reporting requirements and a worked
    case study."

All equation numbers below refer to that article. The functions operate
only on printed values; no raw spectra are required.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Optional


# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------

def load_printed_values(path: Optional[str] = None) -> dict:
    """Load the machine-actionable record of printed input values.

    Parameters
    ----------
    path:
        Optional explicit path to a JSON record. When omitted, the
        packaged ``data/printed_values.json`` shipped with the repository
        is used.
    """
    if path is not None:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    # repository layout: <root>/data/printed_values.json
    root = Path(__file__).resolve().parents[2]
    candidate = root / "data" / "printed_values.json"
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    # installed-package fallback
    with resources.files("libs_repro_audit").joinpath("printed_values.json").open(
        "r", encoding="utf-8"
    ) as fh:  # pragma: no cover
        return json.load(fh)


# ----------------------------------------------------------------------
# A5 - validation: signed relative deviation, Eq. (1)
# ----------------------------------------------------------------------

def signed_relative_deviation(c_lips: float, c_icp: float) -> float:
    """Signed relative deviation delta in percent, Eq. (1).

    delta = (C_LIPS - C_ICP) / C_ICP * 100

    A single-point delta contributes to an assessment of observed
    agreement/trueness; it is not by itself a complete estimate of
    method bias.
    """
    if c_icp == 0:
        raise ZeroDivisionError("ICP-OES comparison value must be non-zero")
    return (c_lips - c_icp) / c_icp * 100.0


# ----------------------------------------------------------------------
# A1/A2 - Stark broadening, Eq. (2)
# ----------------------------------------------------------------------

def stark_ne(fwhm_nm: float, w_s_nm: float, exponent: int = 16) -> float:
    """Electron density from the printed Stark relation, Eq. (2).

    N_e ~ (delta_lambda_FWHM / (2 * W_s)) * 10**exponent   [cm^-3]

    Both widths in nm. The exponent is the normalization used in the
    quoted relationship (16 in the case-study article).
    """
    if w_s_nm <= 0:
        raise ValueError("Stark width parameter W_s must be positive")
    return fwhm_nm / (2.0 * w_s_nm) * 10.0**exponent


def effective_stark_width(fwhm_nm: float, ne_comparison: float,
                          exponent: int = 16) -> float:
    """W_s that would be required for Eq. (2) to reproduce ne_comparison.

    W_s_eff = fwhm / (2 * N_e_comp / 10**exponent)
    """
    ne_norm = ne_comparison / 10.0**exponent
    if ne_norm <= 0:
        raise ValueError("comparison electron density must be positive")
    return fwhm_nm / (2.0 * ne_norm)


def instrumental_fwhm(wavelength_nm: float, resolving_power: float) -> float:
    """Gaussian instrumental FWHM approximated as lambda / R (nm)."""
    if resolving_power <= 0:
        raise ValueError("resolving power must be positive")
    return wavelength_nm / resolving_power


def quadrature_corrected_fwhm(observed_fwhm_nm: float,
                              instrumental_fwhm_nm: float) -> float:
    """Observed FWHM corrected by Gaussian quadrature subtraction (nm).

    Valid only for a Gaussian-on-Gaussian idealization; included to
    quantify the *maximum* plausible instrumental correction, as in
    Section 4 of the audit paper.
    """
    if instrumental_fwhm_nm >= observed_fwhm_nm:
        raise ValueError("instrumental width exceeds observed width")
    return math.sqrt(observed_fwhm_nm**2 - instrumental_fwhm_nm**2)


# ----------------------------------------------------------------------
# A4 - empirical equations: inversion, invertibility, scale check
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class LinearEquation:
    """A printed empirical relation  y = a + b*C  (C in ppm).

    For N_e relations, y is the normalized density N_e / 10^16 cm^-3.
    For T_e relations, y is the temperature in K.
    """
    a: float
    b: float

    @property
    def invertible(self) -> bool:
        """A zero printed slope makes the equation non-invertible."""
        return self.b != 0.0

    def invert(self, y: float) -> float:
        """Concentration C = (y - a) / b. Raises if the slope is zero."""
        if not self.invertible:
            raise ZeroDivisionError(
                "printed slope is 0.0: equation returns a constant plasma "
                "parameter and cannot be inverted for concentration"
            )
        return (y - self.a) / self.b


def ne_scale_check(eq: LinearEquation, ne_value: float,
                   exponents: tuple[int, ...] = (16, 17)) -> dict[int, float]:
    """Concentration implied by each candidate electron-density exponent.

    ``ne_value`` is the mantissa (e.g. 1.54382). For each exponent p the
    normalized input to the printed relation (which carries its own
    1e16 normalization) is ne_value * 10**(p - 16).
    Returns {exponent: concentration_ppm}.
    """
    out: dict[int, float] = {}
    for p in exponents:
        y = ne_value * 10.0 ** (p - 16)
        out[p] = eq.invert(y)
    return out
