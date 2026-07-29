"""Regenerate Figure 2 of the audit paper from printed values only.

Usage:
    python scripts/make_figure2.py [output.pdf|output.png]
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from libs_repro_audit.audit import load_printed_values, signed_relative_deviation  # noqa: E402


def main(outfile: str = "figures/figure2_signed_deviations.pdf") -> None:
    data = load_printed_values()
    elements = list(data["validation_table"]["elements"].keys())
    band = data["validation_table"]["stated_agreement_interval_percent"]

    d_ne, d_te = [], []
    for el in elements:
        v = data["validation_table"]["elements"][el]
        d_ne.append(signed_relative_deviation(v["ne_estimate"], v["icp_oes"]))
        d_te.append(signed_relative_deviation(v["te_estimate"], v["icp_oes"]))

    x = range(len(elements))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.axhspan(-band, band, color="#cde6cd", alpha=0.6, zorder=0,
               label=f"±{band:.0f}% interval stated in the case-study article")
    b1 = ax.bar([i - width / 2 for i in x], d_ne, width,
                color="#2b5d8a", label=r"$N_e$-based estimate", zorder=2)
    b2 = ax.bar([i + width / 2 for i in x], d_te, width,
                color="#c1502e", label=r"$T_e$-based estimate", zorder=2)

    for bars in (b1, b2):
        for rect in bars:
            h = rect.get_height()
            ax.annotate(f"{h:+.2f}",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3 if h >= 0 else -11),
                        textcoords="offset points",
                        ha="center", fontsize=8)

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(elements)
    ax.set_ylabel(r"Signed relative deviation from ICP-OES, $\delta$ (%)")
    ax.set_ylim(-9, 11)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    out = Path(outfile)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300)
    # always emit a PNG twin for quick viewing
    fig.savefig(out.with_suffix(".png"), dpi=200)
    print(f"wrote {out} and {out.with_suffix('.png')}")


if __name__ == "__main__":
    main(*sys.argv[1:])
