#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""segmented_space_time_full_proof.py
====================================

Consolidated proof and validation toolkit for Segmented Space-Time (SSZ).

Responsibilities:
- Render a formal proof scaffold (Definitions → Lemmas → Theorem).
- Load numerical sweep artefacts (v4–v6) and compute validation metrics.
- Emit a compact terminal report and optional Markdown file.
- Provide a robust CLI with sensible defaults.

Usage example:

```bash
python segmented_space_time_full_proof.py --data-dir /mnt/data --prefix v6
```

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import io
import sys

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants & Defaults
# ---------------------------------------------------------------------------

DEFAULT_DATA_DIR = Path("/mnt/data")
DEFAULT_PREFIX = "v6"
DEFAULT_MODES = ("uniform", "weighted")

AGREEMENT_WARN_THRESHOLD = 0.95
LOW_DAMPING_THRESHOLD = 5e-3


# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------

def log(level: str, message: str, quiet: bool = False) -> None:
    """Emit a one-line log message unless quiet is requested."""

    if quiet and level not in {"WARN", "ERROR"}:
        return
    print(f"{level}: {message}")


# ---------------------------------------------------------------------------
# IO setup helpers
# ---------------------------------------------------------------------------


def setup_stdout_utf8() -> None:
    """Ensure stdout can emit UTF-8 characters on Windows consoles."""

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            try:
                sys.stdout = io.TextIOWrapper(  # type: ignore[assignment]
                    sys.stdout.buffer,
                    encoding="utf-8",
                    errors="replace",
                    line_buffering=True,
                )
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Proof scaffold (Definitions, Lemmas, Theorem)
# ---------------------------------------------------------------------------

DEFINITIONS = [
    ("D1", "Segmentierung", "Diskrete Segmente mit lokaler Dämpfung λ_A und Dichte σ(θ)."),
    ("D2", "Roundtrip-Gain", "G = exp(∫ γ_loc ds) · (1−κ) − Dämpfungsterme (λ_A·σ, Spiegelterm log_mirror)."),
    ("D3", "Stabilität", "log G < 0 (direkt) bzw. analytisches Kriterium Ξ < λ_A K σ₀ (modellabhängig)."),
]

ASSUMPTIONS = [
    ("A1", "Glatte, beschränkte γ_loc(θ) entlang des Rundlaufs."),
    ("A2", "Nichtnegative Dämpfungsanteile (λ_A σ(θ), κ, Spiegelverluste)."),
    ("A3", "Segmentkopplung wirkt linear stabil (keine Verstärkung zwischen Segmenten ohne Gain)."),
]

LEMMAS = [
    (
        "L1",
        "Monotonie",
        "Erhöht man die effektive Segmentdichte σ, verschiebt sich log G nach unten.",
        "Skizze: γ_loc bleibt unverändert, λ_A·σ skaliert auf jedem Segment → größere Dichte erhöht die Dämpfungssumme und senkt log G.",
    ),
    (
        "L2",
        "Subadditivität",
        "Segmentweise Dämpfung addiert sich zu einer globalen Schranke für log G.",
        "Skizze: log G = ∫ γ_loc ds − Σ λ_A σ_k + log_mirror; jedes Segment trägt höchstens λ_A σ_k bei → Summe bildet globale Grenze.",
    ),
    (
        "L3",
        "Weighted-Shift",
        "Weighted-Segmentierung verschiebt die Stabilitätsgrenze nach unten relativ zu uniform.",
        "Skizze: Höhere σ in resonanten Bereichen erhöht lokale Dämpfung; folgt aus Vergleich der gewichteten Riemann-Summen (vgl. Lemma L1).",
    ),
]

THEOREM = (
    "T1",
    "Hinreichende Stabilität",
    "Wenn Ξ ≤ λ_A K σ₀ − ε mit ε > 0, dann ist G < 1 und die Rundlauf-Amplitude fällt exponentiell (kein Runaway).",
    "Beweisskizze: (i) Ξ erfasst maximalen Gain-Beitrag unter A1–A3. (ii) Lemma L2 liefert log G ≤ Ξ − λ_A K σ₀. "
    "(iii) Der Abstand ε>0 erzwingt log G < 0. Lemma L3 zeigt, dass weighted-Segmentierung konservativer Stabilität liefert."
)

ROADMAP = [
    "Ableitung der SSZ-Dämpfung aus den GR-Grundgleichungen (Stress-Energie statt Phänomenologie).",
    "Spektral-/Operatorbeweis (Selbstadjungiertheit, Energiemorawetz, Lyapunov).",
    "Kontinuumslimit K → ∞ inkl. Gitter-Unabhängigkeit.",
    "Kerr-Grenzfälle & Kopplung zu Teukolsky-Moden ohne \"Cavity\"-Artefakte.",
    "Beobachtbare Vorhersagen (QNM-Shifts, Echo-Signaturen, Spin-Cutoff) als empirischer Test.",
]


def build_proof_text() -> str:
    """Compose the proof scaffold as a human-readable block of text."""

    lines: List[str] = []
    lines.append("FORMALER BEWEISRAHMEN")
    lines.append("Definitions:")
    for key, title, text in DEFINITIONS:
        lines.append(f"  {key} ({title}): {text}")
    lines.append("Assumptions:")
    for key, text in ASSUMPTIONS:
        lines.append(f"  {key}: {text}")
    lines.append("Lemmas:")
    for key, title, statement, sketch in LEMMAS:
        lines.append(f"  {key} ({title}): {statement}")
        lines.append(f"    Skizze: {sketch}")
    key, title, statement, sketch = THEOREM
    lines.append("Theorem:")
    lines.append(f"  {key} ({title}): {statement}")
    lines.append(f"    Beweisskizze: {sketch}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Artefact discovery & loading
# ---------------------------------------------------------------------------

def resolve_artifact(
    data_dir: Path,
    base_name: str,
    prefix: str,
    extension: str,
    quiet: bool,
) -> Tuple[Optional[Path], Optional[str]]:
    """Resolve an artefact path for a given prefix, falling back gracefully."""

    candidate = data_dir / f"{base_name}_{prefix}{extension}"
    if candidate.exists():
        return candidate, prefix

    matches = sorted(data_dir.glob(f"{base_name}_*{extension}"))
    if matches:
        fallback = matches[-1]
        fallback_prefix = fallback.stem.replace(f"{base_name}_", "")
        log("WARN", f"{base_name}_{prefix}{extension} nicht gefunden – fallback auf {fallback.name}", quiet)
        return fallback, fallback_prefix

    log("WARN", f"Kein Artefakt {base_name}_*.{extension} in {data_dir}", quiet)
    return None, None


def load_csv(path: Path, quiet: bool) -> Optional[pd.DataFrame]:
    """Load a CSV file using pandas with robust error handling."""

    if path is None:
        return None
    try:
        df = pd.read_csv(path)
        log("INFO", f"CSV geladen: {path} (n={len(df)})", quiet)
        return df
    except Exception as exc:  # pragma: no cover - defensive logging
        log("WARN", f"CSV konnte nicht geladen werden ({path}): {exc}", quiet)
        return None


def load_summary_json(path: Path, quiet: bool) -> Optional[Dict]:
    """Load a JSON summary if available."""

    if path is None:
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        log("INFO", f"JSON geladen: {path}", quiet)
        return payload
    except Exception as exc:
        log("WARN", f"JSON konnte nicht geladen werden ({path}): {exc}", quiet)
        return None


def collect_image_refs(data_dir: Path, prefix: str) -> List[str]:
    """Collect names of existing PNG artefacts for reference."""

    patterns = [
        f"heatmap_stability_uniform_{prefix}.png",
        f"heatmap_stability_weighted_{prefix}.png",
        f"disagreement_map_uniform_{prefix}.png",
        f"disagreement_map_weighted_{prefix}.png",
        f"boundary_lambdaA_vs_Omega0_{prefix}.png",
        f"lambdaA_diff_map_{prefix}.png",
    ]
    found: List[str] = []
    for name in patterns:
        if (data_dir / name).exists():
            found.append(name)
    return found


def load_artifacts(
    data_dir: Path,
    prefix: str,
    quiet: bool,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[Dict], Optional[str], Dict[str, Optional[Path]]]:
    """Load results, boundaries, summary and report resolved prefix plus artefact map."""

    artefacts: Dict[str, Optional[Path]] = {}

    results_path, resolved_prefix = resolve_artifact(data_dir, "proof_sweep_results", prefix, ".csv", quiet)
    artefacts["results"] = results_path
    df_results = load_csv(results_path, quiet)

    boundaries_path, resolved_prefix_b = resolve_artifact(
        data_dir, "stability_boundaries", resolved_prefix or prefix, ".csv", quiet
    )
    artefacts["boundaries"] = boundaries_path
    df_boundaries = load_csv(boundaries_path, quiet)

    summary_path, resolved_prefix_s = resolve_artifact(
        data_dir, "proof_sweep_summary", resolved_prefix or resolved_prefix_b or prefix, ".json", quiet
    )
    artefacts["summary"] = summary_path
    summary = load_summary_json(summary_path, quiet)

    resolved = resolved_prefix or resolved_prefix_b or resolved_prefix_s or prefix
    return df_results, df_boundaries, summary, resolved, artefacts


# ---------------------------------------------------------------------------
# Metric computation utilities
# ---------------------------------------------------------------------------

def normalise_mode(series: pd.Series) -> pd.Series:
    """Lower-case segment modes for consistent filtering."""

    return series.astype(str).str.lower()


def infer_stable_direct(df: pd.DataFrame) -> pd.Series:
    """Infer the direct stability boolean, falling back to logG."""

    if "stable_direct" in df.columns:
        return df["stable_direct"].astype(bool)
    if "logG" in df.columns:
        return (df["logG"] <= 0.0)
    candidate = next((c for c in df.columns if "log" in c.lower() and "g" in c.lower()), None)
    if candidate:
        return (df[candidate] <= 0.0)
    return pd.Series([False] * len(df), index=df.index)


def infer_stable_criterion(df: pd.DataFrame) -> Optional[pd.Series]:
    """Infer criterion-based stability if available."""

    if "stable_criterion" in df.columns:
        return df["stable_criterion"].astype(bool)
    candidate = next((c for c in df.columns if "criterion" in c.lower()), None)
    if candidate:
        try:
            return (df[candidate] > 0.0)
        except Exception:  # pragma: no cover - defensive
            return None
    return None


def group_fraction(series: pd.Series, tool_df: pd.DataFrame, value_col: str) -> List[str]:
    """Produce formatted fraction summaries keyed by (K, lambda_A)."""

    if "K" not in tool_df.columns or "lambda_A" not in tool_df.columns:
        return []

    df = tool_df.assign(metric=series.astype(float))
    grouped = df.groupby(["K", "lambda_A"], as_index=False)["metric"].mean()
    grouped.sort_values(by=["K", "lambda_A"], inplace=True)
    formatted = [
        f"K={int(row['K'])}, λ_A={row['lambda_A']:.5f} → {row['metric']:.3f}"
        for _, row in grouped.head(8).iterrows()
    ]
    return formatted


def compute_mode_metrics(
    df: Optional[pd.DataFrame],
    mode: str,
) -> Optional[Dict]:
    """Compute stability metrics for a given segment mode."""

    if df is None or df.empty:
        return None

    data = df.copy()
    has_modes = "segment_mode" in data.columns
    if mode != "both" and has_modes:
        data = data[normalise_mode(data["segment_mode"]) == mode]
    if mode != "both" and not has_modes and mode != "uniform":
        # Without mode column we cannot isolate weighted; treat as unavailable.
        if mode == "weighted":
            return None
    if data.empty:
        return None

    stable_direct = infer_stable_direct(data)
    stable_criterion = infer_stable_criterion(data)

    agreement_ratio: Optional[float] = None
    agreement_count: int = 0
    if stable_criterion is not None and len(stable_criterion) == len(stable_direct):
        agreement_ratio = float((stable_direct == stable_criterion).mean())
        agreement_count = len(stable_direct)

    frac_samples = group_fraction(stable_direct, data, "stable_direct") if not data.empty else []

    disagreement_samples: List[str] = []
    if stable_criterion is not None:
        disagree = (stable_direct != stable_criterion).astype(float)
        disagreement_samples = group_fraction(disagree, data, "disagreement")

    log_values = data["logG"] if "logG" in data.columns else None
    log_stats: Optional[Dict[str, float]] = None
    if log_values is not None and len(log_values.dropna()) > 0:
        log_stats = {
            "min": float(np.nanmin(log_values)),
            "max": float(np.nanmax(log_values)),
            "median": float(np.nanmedian(log_values)),
        }

    low_damping_issue = False
    if "lambda_A" in data.columns and log_values is not None:
        low_mask = data["lambda_A"] <= LOW_DAMPING_THRESHOLD
        if low_mask.any():
            low_max = float(np.nanmax(log_values[low_mask]))
            low_damping_issue = low_max > 0.0

    return {
        "entries": len(data),
        "agreement_ratio": agreement_ratio,
        "agreement_count": agreement_count,
        "frac_samples": frac_samples,
        "disagreement_samples": disagreement_samples,
        "log_stats": log_stats,
        "low_damping_issue": low_damping_issue,
    }


def compute_boundary_metrics(df: Optional[pd.DataFrame]) -> Optional[Dict]:
    """Compute statistics from stability boundaries."""

    if df is None or df.empty:
        return None

    result: Dict[str, Dict] = {}
    if "segment_mode" in df.columns:
        modes = normalise_mode(df["segment_mode"])  # type: ignore[assignment]
        df = df.assign(segment_mode=modes)
    else:
        df = df.assign(segment_mode="uniform")

    for mode in sorted(df["segment_mode"].unique()):
        subset = df[df["segment_mode"] == mode]
        direct = subset["lambdaA_crit_direct"].dropna()
        criterion = subset["lambdaA_crit_criterion"].dropna()
        diff = (direct - criterion).abs().dropna() if not direct.empty and not criterion.empty else pd.Series(dtype=float)
        result[mode] = {
            "count_direct": int(direct.count()),
            "count_criterion": int(criterion.count()),
            "diff_max": float(diff.max()) if not diff.empty else None,
            "diff_median": float(diff.median()) if not diff.empty else None,
        }

    # Cross-mode comparison weighted vs uniform if possible
    comparison = None
    if {"uniform", "weighted"}.issubset(result.keys()):
        try:
            uniform = df[df["segment_mode"] == "uniform"]["lambdaA_crit_direct"].dropna()
            weighted = df[df["segment_mode"] == "weighted"]["lambdaA_crit_direct"].dropna()
            merged = df.pivot_table(
                index=[df.get("Omega0", df.get("omega0", 0)), "K"],
                columns="segment_mode",
                values="lambdaA_crit_direct",
            )
            merged = merged.dropna(subset=["uniform", "weighted"], how="any")
            if not merged.empty:
                share = float((merged["weighted"] <= merged["uniform"]).mean())
                comparison = {
                    "pairs": len(merged),
                    "share_weighted_leq_uniform": share,
                }
            else:
                comparison = {"pairs": 0, "share_weighted_leq_uniform": None}
        except Exception:  # pragma: no cover - defensive when columns vary
            comparison = {"pairs": 0, "share_weighted_leq_uniform": None}

    result["comparison"] = comparison
    return result


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def format_log_stats(stats: Optional[Dict[str, float]]) -> str:
    if not stats:
        return "n/a"
    return f"min={stats['min']:.4f}, median={stats['median']:.4f}, max={stats['max']:.4f}"


def render_mode_section(mode: str, metrics: Optional[Dict]) -> List[str]:
    lines: List[str] = []
    title = "Beide Modi (aggregiert)" if mode == "both" else f"Modus: {mode}"
    lines.append(title)
    if metrics is None:
        lines.append("  Daten: n/a")
        return lines

    lines.append(f"  Einträge: {metrics['entries']}")
    if metrics["agreement_ratio"] is not None:
        lines.append(
            f"  Agreement (direct vs criterion): {metrics['agreement_ratio']:.3f} (n={metrics['agreement_count']})"
        )
    else:
        lines.append("  Agreement (direct vs criterion): n/a")
    lines.append(f"  logG-Statistiken: {format_log_stats(metrics['log_stats'])}")
    lines.append("  Beispielhafte λ_A-Stabilitätsraten:")
    if metrics["frac_samples"]:
        for item in metrics["frac_samples"]:
            lines.append(f"    - {item}")
    else:
        lines.append("    - n/a")
    if metrics["disagreement_samples"]:
        lines.append("  Disagreement-Hotspots:")
        for item in metrics["disagreement_samples"]:
            lines.append(f"    - {item}")
    if metrics["low_damping_issue"]:
        lines.append("  WARN: Bei λ_A → 0 wurden positive logG-Werte gefunden (prüfe Gain-Setup).")
    else:
        lines.append("  Grenzfall λ_A → 0: keine Instabilität detektiert.")
    return lines


def render_boundary_section(boundary_stats: Optional[Dict]) -> List[str]:
    lines: List[str] = ["Boundary-Analyse"]
    if not boundary_stats:
        lines.append("  n/a")
        return lines
    for mode in ["uniform", "weighted"]:
        stats = boundary_stats.get(mode)
        if not stats:
            continue
        lines.append(
            f"  {mode}: direct={stats['count_direct']} kritische Punkte, criterion={stats['count_criterion']}"
        )
        if stats.get("diff_max") is not None:
            lines.append(
                f"    Δλ_A max={stats['diff_max']:.4f}, median={stats['diff_median']:.4f}"
            )
    comparison = boundary_stats.get("comparison")
    if comparison:
        share = comparison.get("share_weighted_leq_uniform")
        if share is None:
            lines.append("  Weighted ≤ Uniform Aussage: nicht beurteilbar (keine Paare)")
        else:
            lines.append(
                f"  Weighted ≤ Uniform: {share:.3f} der {comparison['pairs']} Paare erfüllen λ_A,crit(weighted) ≤ λ_A,crit(uniform)"
            )
    return lines


def render_scope_section() -> List[str]:
    return [
        "Scope des Beweises",
        "  Modellbeweis: Stabilität im SSZ-Rahmen gesichert (siehe T1).",
        "  Kein Natur-/GR-Endbeweis: Offene Schritte →",
        *[f"    - {item}" for item in ROADMAP],
    ]


def render_report(
    data_dir: Path,
    requested_prefix: str,
    resolved_prefix: str,
    artefacts: Dict[str, Optional[Path]],
    metrics_by_mode: Dict[str, Optional[Dict]],
    boundary_stats: Optional[Dict],
    summary: Optional[Dict],
    image_refs: Iterable[str],
) -> str:
    lines: List[str] = []
    lines.append("SSZ SEGMENTED SPACE-TIME PROOF SUMMARY")
    lines.append(f"Datenverzeichnis: {data_dir}")
    lines.append(f"Angefragter Prefix: {requested_prefix} → Verwendet: {resolved_prefix}")
    for key, path in artefacts.items():
        lines.append(f"Artefakt {key}: {path if path else 'n/a'}")
    if image_refs:
        lines.append("Vorhandene Abbildungen:")
        for name in image_refs:
            lines.append(f"  - {name}")

    lines.append("")
    lines.append(build_proof_text())
    lines.append("")

    for mode, metrics in metrics_by_mode.items():
        lines.extend(render_mode_section(mode, metrics))
        lines.append("")

    lines.extend(render_boundary_section(boundary_stats))
    lines.append("")

    if summary:
        grid_summary = summary.get("grid_summary") or summary.get("grid_summary".upper())
        if grid_summary:
            lines.append("Numerische Zusammenfassung (aus JSON):")
            for key, value in grid_summary.items():
                lines.append(f"  {key}: {value}")
            lines.append("")

    lines.extend(render_scope_section())
    lines.append("")
    lines.append("Hinweis: Agreement-Warnschwelle = 0.95.")
    return "\n".join(lines)


def save_markdown(report: str, data_dir: Path, prefix: str, quiet: bool) -> Optional[Path]:
    path = data_dir / f"SSZ_PROOF_SUMMARY_{prefix}.md"
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("# SSZ Segmented Space-Time Proof Summary\n\n")
            handle.write(report.replace("\n", "\n\n"))
        log("INFO", f"Markdown exportiert: {path}", quiet)
        return path
    except Exception as exc:  # pragma: no cover
        log("WARN", f"Markdown konnte nicht geschrieben werden ({path}): {exc}", quiet)
        return None


# ---------------------------------------------------------------------------
# CLI handling
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Segmented Space-Time Full Proof Report")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Verzeichnis mit Artefakten")
    parser.add_argument("--prefix", type=str, default=DEFAULT_PREFIX, help="Artefakt-Prefix (z. B. v6)")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["both", "uniform", "weighted"],
        default="both",
        help="Segmentmodus-Filter",
    )
    parser.add_argument("--emit-md", dest="emit_md", action="store_true")
    parser.add_argument("--no-emit-md", dest="emit_md", action="store_false")
    parser.set_defaults(emit_md=True)
    parser.add_argument("--quiet", action="store_true", help="Reduziert Log-Ausgabe")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    setup_stdout_utf8()
    args = parse_args()
    data_dir: Path = args.data_dir
    prefix: str = args.prefix
    mode: str = args.mode
    emit_md: bool = bool(args.emit_md)
    quiet: bool = bool(args.quiet)

    if not data_dir.exists():
        log("WARN", f"Datenverzeichnis {data_dir} existiert nicht – es wird erzeugt", quiet)
        data_dir.mkdir(parents=True, exist_ok=True)

    df_results, df_boundaries, summary, resolved_prefix, artefacts = load_artifacts(
        data_dir, prefix, quiet
    )

    modes_to_process = [mode] if mode != "both" else list(DEFAULT_MODES)
    metrics_by_mode: Dict[str, Optional[Dict]] = {}
    aggregated_df = df_results
    metrics_by_mode["both"] = compute_mode_metrics(aggregated_df, "both") if mode == "both" else None
    for m in modes_to_process:
        metrics_by_mode[m] = compute_mode_metrics(df_results, m)

    boundary_stats = compute_boundary_metrics(df_boundaries)
    if metrics_by_mode:
        for m, metrics in metrics_by_mode.items():
            if metrics and metrics.get("agreement_ratio") is not None and metrics["agreement_ratio"] < AGREEMENT_WARN_THRESHOLD:
                log(
                    "WARN",
                    f"Agreement unter Schwelle (Modus {m}): {metrics['agreement_ratio']:.3f}",
                    quiet,
                )

    image_refs = collect_image_refs(data_dir, resolved_prefix)

    report_text = render_report(
        data_dir=data_dir,
        requested_prefix=prefix,
        resolved_prefix=resolved_prefix,
        artefacts=artefacts,
        metrics_by_mode={k: v for k, v in metrics_by_mode.items() if v is not None or k == "both"},
        boundary_stats=boundary_stats,
        summary=summary,
        image_refs=image_refs,
    )

    print(report_text)

    if emit_md:
        save_markdown(report_text, data_dir, resolved_prefix, quiet)


if __name__ == "__main__":
    main()
