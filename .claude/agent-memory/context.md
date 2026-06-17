# Project Context

## What this is

- **Project Ordo Astra** — genetic algorithm (GA) implementations for the
  traveling salesman problem (TSP). Framed as space exploration: each node is a
  planet/moon/landmark, so a tour is an exploration route.
- Windows system. PowerShell is primary; a Bash tool is also available.

## Source layout (`src/`, a package with `src` as root)

- Run via `python -m src.main` from the repo root.
- `src/main.py` — entry point. `Run` class + `getInstanceNames`; the `__main__`
  driver reads `res/info/euc-2d-instances.txt` and runs the GA on every listed
  instance (78 of them, `NUM_RUNS = 10` each). First instance is `a280`.
- `src/genetic_algorithm/genetic_algorithm.py` — the GA core (numba-jitted
  kernels: pop init, fitness, tournament selection, order crossover, swap
  mutation, two-opt local search). Public entry is `runGA(instance, runNum)`.
- `src/genetic_algorithm/__init__.py` — re-exports `runGA`.
- `src/utils/` — `instance_util.py` (`Euc2D` loader), `log_util.py` (`Log`),
  `filter_util.py` (`Filter`), `plot_util.py` (`Plot`, analysis plots).
- Every package dir has `__init__.py`.

## Resources (`res/`)

- `res/tsplib/tsp/` — TSP instances (`.tsp`). NOTE: directory is `tsplib`, NOT
  `tsplib95` (that is only the PyPI package name).
- `res/info/euc-2d-instances.txt` — the EUC_2D instance list the driver reads.
- `res/info/opt-fits.txt` — known optimal fitnesses per instance.

## Outputs (`stdout/`)

- `stdout/runs/<instance>/<instance>_<runNum>.txt` — per-run logs (header, per-gen
  line, final tour, footer). The `plot_util.py` parsers depend on this format.
- `stdout/instance-plots/`, `stdout/analysis/` — generated plots.

## Environment

- Dependencies live in the `.env.local` virtualenv (a venv DIRECTORY, not an env
  file). Use `./.env.local/Scripts/python.exe`. The system `python` lacks the
  deps. `.env.local` is gitignored.
- Runtime deps (`requirements.txt`): tsplib95, numba, matplotlib, numpy, scipy.
- First GA run is slow (~10s) because numba JIT-compiles the kernels.

## Authoritative docs

- `.claude/CLAUDE.md` — auto-read each session.
- `.claude/AGENTS.md` — NOT auto-read; CLAUDE.md only points to it. Holds the
  coding-style conventions. Read it on demand when working in `.`.
