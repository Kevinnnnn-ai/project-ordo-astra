# Notes

Operational gotchas learned while working in this repo.

## Running the code

- Use the venv interpreter: `./.env.local/Scripts/python.exe`. The system
  `python` is missing numba/scipy and will fail at `import numba`.
- `python -m src.main` runs ALL 78 instances x 10 runs — a long batch job, and it
  OVERWRITES committed files in `stdout/runs/`. Do not run it as a smoke test.
- For a quick end-to-end check, call `runGA` directly on one small instance with a
  throwaway runNum, then delete the artifact:
  `from src.utils.instance_util import Euc2D; from src.genetic_algorithm import runGA; runGA(Euc2D('berlin52'), 999)`.
- First run pays a ~10s numba JIT compile cost before any generations log.

## Verified working

- `python -m src.main` import chain resolves; the GA compiles and converges
  end-to-end (berlin52 -> valid tour). Both rewire bug-fixes confirmed by a real
  compiled run:
  - swap mutation uses a randint distinctness loop (numba nopython does NOT
    support `np.random.choice(..., replace=False)`).
  - `_runTwoOptTopK` uses `TWO_OPT_PERCENTILE = 10` so only the cheapest ~10% of
    tours get two-opt (minimization: lower fitness = better). The old
    `np.percentile(..., 100)` refined the whole population.

## Gotchas

- Directory is `res/tsplib/tsp`, NOT `res/tsplib95`. `tsplib95` is only the PyPI
  package name (`import tsplib95`).
- `.env.local` is a virtualenv directory, not a dotenv file. It is gitignored.
- The `Log` class output format is a contract: `plot_util.py` parsers read the
  `n:`, `computationTime:`, `percentError:`, and `tour:` lines. Don't change the
  log format without updating the parsers.
- `cat` via the Bash tool does NOT satisfy the Write tool's "must Read first"
  requirement — use the Read tool before editing a file.
- On Windows, git warns about LF->CRLF on these text files; harmless.

## How to verify code review here

- This codebase's conventions live in `.claude/AGENTS.md` (read it explicitly).
- Multi-agent audit + adversarial verify worked well: audits run against a stale
  file snapshot, so the verify pass MUST re-read the on-disk bytes — several
  "issues" were already-fixed false positives.
