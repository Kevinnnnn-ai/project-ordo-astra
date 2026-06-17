# Decisions

User-made decisions from the package rewire and review work.

## Package layout

- **`src` as package root.** Run via `python -m src.main` from the repo root.
  Every package dir gets `__init__.py`; `genetic_algorithm/__init__.py`
  re-exports `runGA`; imports are package-relative (`from .utils...`,
  `from ..utils.log_util import Log`).
- `instance_util.py` belongs under `src/utils/` (it is a util), not under
  `genetic_algorithm/`.

## Naming / conventions (recorded in AGENTS.md)

- **Underscores:** variables NEVER take a leading underscore. Helper functions
  and helper classes MAY be underscore-prefixed (e.g. `_runOX`). Functions must
  still be verb-first even when prefixed (`_runTwoOptTopK`, not `_twoOptTopK`).
- SCREAMING_SNAKE_CASE is for constants only — per-instance `self.*` attributes
  are camelCase.
- Booleans take a prefix (`is`/`can`/`has`): `isImproved`, `isInTour`,
  `canShowAggConverge`, etc.
- Module-level boolean CONSTANTS like `NO_GIL` were left as-is (the boolean-prefix
  rule targets variables, not constants).
- The public function name `runGA` (uppercase acronym) is canonical and was kept;
  only the colliding `Run` method was renamed to `runGa` to disambiguate.

## stdout/runs protection

- Pre-existing run files in `stdout/runs/` are real results and MUST NOT be
  overwritten. Test runs must not clobber them. (Codified in CLAUDE.md.)
- A standalone smoke test should run a SINGLE small instance (e.g. berlin52) with
  a throwaway runNum — never the full `python -m src.main` sweep, which rewrites
  committed result files.

## Git

- Commit, do not push — the user pushes to `main` themselves.
- Separate logical changes into separate commits with descriptive messages
  (what / why / notes). Never use `--no-verify`.
