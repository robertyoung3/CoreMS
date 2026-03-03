## 1. Preparation

- [x] 1.1 Fetch latest upstream master: `git fetch upstream master`
- [x] 1.2 Save original fix commit SHAs for reference (to cherry-pick file changes from)

## 2. Rewrite PR branches

- [x] 2.1 Rewrite `fix/baseline-noise-none-check` (PR #25): create from `upstream/master`, checkout `corems/mass_spectrum/factory/MassSpectrumClasses.py` from original commit, commit, force-push
- [x] 2.2 Rewrite `fix/aromaticity-index-divide-by-zero` (PR #26): create from `upstream/master`, checkout `corems/molecular_formula/calc/MolecularFormulaCalc.py` from original commit, commit, force-push
- [x] 2.3 Rewrite `fix/masslist-parameter-source` (PR #27): create from `upstream/master`, checkout `corems/mass_spectrum/input/baseClass.py` from original commit, commit, force-push
- [x] 2.4 Rewrite `fix/kendrick-base-consistency` (PR #28): create from `upstream/master`, checkout `corems/molecular_formula/factory/MolecularFormulaFactory.py` and `corems/ms_peak/factory/MSPeakClasses.py` from original commit, commit, force-push
- [x] 2.5 Rewrite `fix/formula-kmd-rounding-method` (PR #29): create from `upstream/master`, checkout `corems/molecular_formula/calc/MolecularFormulaCalc.py` from original commit, commit, force-push

## 3. Verify PRs

- [x] 3.1 For each PR (#25–#29), verify diff on GitHub shows only the intended bug fix files (use `gh pr diff <number> --repo EMSL-Computing/CoreMS`)
- [x] 3.2 Verify fork master is unchanged (still has devcontainer/tooling commits ahead of upstream)

## 4. Add guardrails

- [x] 4.1 Create `CLAUDE.md` at project root with upstream contribution rules: branch from `upstream/master`, validate diff scope before pushing, pre-push check command
- [x] 4.2 Append upstream PR hygiene section to `AGENTS.md` with the same rules and validation command

## 5. Return to fork master and commit guardrails

- [x] 5.1 Switch back to fork `master` branch
- [ ] 5.2 Commit `CLAUDE.md` and updated `AGENTS.md` to fork master
- [ ] 5.3 Push fork master to origin
