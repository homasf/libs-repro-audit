"""Executable reproducibility-audit record for CF-LIBS/LIPS quantification.

Implements the numerical checks of checkpoints A1-A5 from
Saeidfirozeh & Ferus and regenerates Tables 1-2, Figure 2, the
electron-density scale checks and the equation invertibility audit
from printed values only.
"""

from .htmlreport import render_html
from .engine import AuditReport, CheckResult, load_record, render_markdown, run_audit
from .audit import (
    LinearEquation,
    effective_stark_width,
    instrumental_fwhm,
    load_printed_values,
    ne_scale_check,
    quadrature_corrected_fwhm,
    signed_relative_deviation,
    stark_ne,
)

__all__ = [
    "LinearEquation",
    "effective_stark_width",
    "instrumental_fwhm",
    "load_printed_values",
    "ne_scale_check",
    "quadrature_corrected_fwhm",
    "signed_relative_deviation",
    "stark_ne",
    "AuditReport",
    "CheckResult",
    "load_record",
    "render_markdown",
    "run_audit",
    "render_html",
]

__version__ = "2.0.0"
