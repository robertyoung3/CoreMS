## Why

Upstream maintainers (@kheal) requested that PRs #25–#29 on EMSL-Computing/CoreMS be culled to minimal diffs. Each PR currently includes ~27 extraneous files from our fork's Podman devcontainer migration, OpenSpec tooling, and Claude Code configuration — files that belong only in our fork. The actual bug fixes are 1–19 lines each but are buried in noise. The PRs must be rewritten to be accepted, and guardrails must be added to prevent this from recurring.

## What Changes

- **Rewrite 5 upstream PR branches** (`fix/baseline-noise-none-check`, `fix/aromaticity-index-divide-by-zero`, `fix/masslist-parameter-source`, `fix/kendrick-base-consistency`, `fix/formula-kmd-rounding-method`) so each contains only its bug fix file(s):
  - PR #25: `corems/mass_spectrum/factory/MassSpectrumClasses.py`
  - PR #26: `corems/molecular_formula/calc/MolecularFormulaCalc.py`
  - PR #27: `corems/mass_spectrum/input/baseClass.py`
  - PR #28: `corems/molecular_formula/factory/MolecularFormulaFactory.py`, `corems/ms_peak/factory/MSPeakClasses.py`
  - PR #29: `corems/molecular_formula/calc/MolecularFormulaCalc.py`
- **Force-push cleaned branches** to update the existing PRs in-place
- **Add upstream contribution guardrails** in CLAUDE.md and AGENTS.md to enforce clean PR hygiene for future upstream submissions

## Capabilities

### New Capabilities

- `upstream-pr-hygiene`: Rules and workflow for creating clean, minimal-diff PRs against upstream repositories — covering branch creation strategy, file filtering, and pre-push validation

### Modified Capabilities

(none)

## Impact

- **Git branches**: 5 branches on `origin` will be force-pushed with rewritten history (single commit each, based on `upstream/master`)
- **GitHub PRs**: PRs #25–#29 on EMSL-Computing/CoreMS will update automatically when branches are force-pushed
- **Developer workflow**: CLAUDE.md and AGENTS.md will gain new sections governing upstream PR creation, affecting how future contributions are prepared
- **No code changes**: The actual `corems/` bug fixes remain identical; only the branch history and surrounding files change
