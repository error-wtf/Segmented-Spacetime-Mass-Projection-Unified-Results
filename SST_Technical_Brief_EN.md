# SST Technical Brief (Companion to README)

> Concise, candid overview of the Segmented Spacetime (SST) project for readers who want the “what, why, how to test” in one place.

## Why this file exists
This brief complements the README with a clear summary of claims, current evidence, known limitations, and concrete next steps. It is designed to set accurate expectations and make independent validation as frictionless as possible.

## One‑paragraph snapshot
**Segmented Spacetime (SST)** models spacetime as **discrete segments** rather than a smooth manifold. Gravity is modeled as an increase in local **segment density (N)**; redshift is treated **phenomenologically** via a **local projection factor (\(\alpha_{loc}\))** rather than explicit time dilation. In the weak‑field limit, the current code reproduces standard **PPN tests (\(\gamma=1, \beta=1\))** and classical observables (light bending, Shapiro delay, Mercury perihelion) to numerical identity with GR. On a specific redshift dataset (n=67), the SST projection fit outperforms a GR×SR baseline under a paired sign test (**p ≈ 9.22×10⁻¹⁹**). In strong fields, the project reports **shadow diameter predictions** (e.g., **Sgr A\* 53.255 µas; M87\* 39.689 µas**), noting dependence on spin, inclination, and emission model. **Open:** a complete field theory from an action/Lagrangian and independent, blinded replications.

## What SST proposes (at a glance)
- **Discrete spacetime:** dynamics expressed through an integer‑like segment count **N** (local segmentation density).
- **Phenomenological projection:** observable energies/frequencies encoded via **\(\alpha_{loc}\)** or **P(N, \(\varphi\))** at fixed \(\alpha_0\) (no blanket claim that nature’s constants intrinsically vary).
- **Weak‑field equivalence:** reproduces GR’s PPN predictions (\(\gamma=1, \beta=1\)) and classical tests to machine precision in current code.
- **Strong‑field deviations (testable):** specific shadow‑radius predictions intended for direct comparison with EHT data.

## What SST does **not** claim
- It does **not** claim peer‑reviewed status at this time.
- It does **not** present a finalized **Lagrangian or field equations** for segment dynamics (work in progress).
- It does **not** assert a universal, intrinsic variability of fundamental constants; the current public stance is **phenomenological projection on observables**.

## Current evidence & numerics (as reported in the repo artifacts)
- **Deterministic runs & logs:** fixed seeds, documented splits, Gaussian i.i.d. noise via MAD, Chauvenet outlier rule; reproducible terminal logs.
- **Redshift dataset (n = 67):** median absolute error improvement vs GR×SR baseline; **paired sign test p ≈ 9.22×10⁻¹⁹**.
- **PPN & classical tests:** `ssz_covariant_smoketest` returns **\(\gamma=1, \beta=1\)**; light bending, Shapiro delay, and perihelion advance match GR to 12+ decimals.
- **Black‑hole shadows:** example outputs **Sgr A\*: 53.255 µas; M87\*: 39.689 µas** with explicit dependence on \(a_\*\) (spin), **i** (inclination), and emission model.
- **Provenance:** example SHA256s recorded in logs (e.g., input CSV `c6b503e1…f717`; main module `e27fcdc3…a255`) to support auditability.

> **Important:** The dataset is modest in size; the above numbers are **encouraging but not definitive**. Blinded, preregistered re‑runs by independent groups are required.

## Open issues / scientific risks
- **No published action/Lagrangian:** without field equations for segment dynamics, the framework remains a **phenomenology**, not a complete theory.
- **Notation collisions:** internal “\(\beta\)” vs PPN \(\beta\); must be consistently disambiguated.
- **Historical sketches vs. consolidated model:** legacy speculative ideas (e.g., “radio‑reemergence” narratives) should be clearly archived to avoid confusion with the present core.
- **Generalization risk:** results shown on one curated dataset may not transfer; guard against implicit tuning.

## Reproducibility checklist (for external reviewers)
- Containerized environment (Docker/Apptainer) with pinned versions.
- One‑click script that: verifies checksums → runs pipelines → emits plots/logs → writes a machine‑readable summary (JSON/CSV).
- Publish all artifacts (logs, plots, metrics) with a **DOI**.
- Provide **READMEs** for data provenance, split rules, and outlier handling.
- Include **unit tests** covering formulas, I/O integrity, and numerical tolerances.

## Recommended preregistered tests
1. **Clock‑height gradient:** \(\Delta\alpha/\alpha \approx \kappa\,U/c^2 + O((U/c^2)^2)\) using state‑of‑the‑art optical clocks.
2. **Quasar many‑multiplet curves:** preregistered pipelines and blind fits across gravitational potentials.
3. **S‑stars (e.g., S2) redshift curves:** preregistered \(z(t)\) without post‑hoc tuning.
4. **EHT likelihood test (priority):** integrate SST forward model into the EHT imaging/likelihood stack; perform a **blinded, prior‑matched model comparison** (GR vs SST) across Sgr A\* and M87\*.

## How to run (short guide)
- **Weak‑field/PPN checks:** run the provided “covariant smoketest” script; verify that \(\gamma=\beta=1\) and classical observables match GR to machine precision.
- **Redshift study:** execute the unified redshift script on the supplied CSV; confirm MAE and sign‑test statistics reproduce published logs.
- **Shadow predictions:** run the shadow script grid over \(a_\*\), **i**, and emission parameters; export diameter posteriors for downstream likelihood evaluation.

## Communication & scope notes
- Be explicit when the project reports **phenomenology** vs **derived theory**.
- Label legacy hypotheses as **historical**; keep the consolidated model crisp.
- Always accompany single‑number claims with **assumptions, priors, and confidence intervals**.

## Citation
If you use this brief or replicate results, please cite the SST preprints and this repository. Replace with canonical references once journal publications appear.

---

*Maintainer note:* This brief is intentionally concise and practical. Keep it updated whenever scripts, datasets, or claims change. Add DOIs and container hashes as releases are minted.
