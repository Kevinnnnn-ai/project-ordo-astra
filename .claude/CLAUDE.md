# Agent Rules

## While Working in `.`

- Read `./.claude/AGENTS.md` for project conventions, goals, and contextualization.
- Read `./.claude/agent-memory/*` for a decision log, list of concurrent project facts, and list of important notes left by other agents.

### While Working With `./.claude/agent-memory/context.md`

- Keep and update a running list of durable facts about the project, including noted future goals and the stated direction of the project.
- It should not be a history or log of changing facts; only keep concurrent information.

### While Working With `./.claude/agent-memory/decisions.md`

- This should be a log of both agentic and human choices made and why.
- Append logs with each decision.

### While Working With `./.claude/agent-memory/notes.md`

- This should be a list of scratch and or running observations and notes.
- Put information in here that would be beneficial for future agents and sessions to know.
- Remove irrelevant entries that no longer apply to this repository.

## While Working in `./stdout/runs/`

- Do not interfere with any pre-existing run files.
- Ensure that test runs will not interfere with any pre-existing run files.

## General Rules

- Understand the codebase and its conventions — the codebase is the source of truth. You should prefer reading source code over searching.
- Do not search web unless explicitly prompted. Web search does not help in general for this project.
- Write performant code. Always prefer performance over other aspects.
- Use `gh` CLI tool for fetching data from `github.com`.
- This is a Windows system, not a macOS or Linux Bash environment.

# Coding Conventions

- Write comments and documentations in English.
- Commit your work as frequent as possible using git. Do not use the `--no-verify` flag.
- Always describe commits — attach descriptions to all commits, addressing what was done, why it was done, and important points of interest.
- Prefer multiple smaller files over single larger files.

## Coding Style

Keep all things short but descriptive. Try to not abbreviate unless it is common in the code base.

- **Variables** — Use camel case. Local iteration values should always be denoted with `i` or `j`. Local, short-lived, positional values should be denoted with letters from the alphabet, with the order they appear in corresponding to the order of the alphabet. Never prefix a variable with an underscore.
    - **Booleans** — Always start the variable with a boolean prefix (e.g., `can`, `has`, `is`, etc.).
    - **Constants** — Use screaming snake case.
- **Functions** — Use camel case. Always start the function with a verb (e.g., `run`, `calc`, etc.). Prefix helper functions with an underscore (e.g., `_runOX`).
- **Classes** — Use pascal case. Prefix helper classes with an underscore.
- **Whitespace** — When separating sections (e.g., `imports`, `variables`, `functions`, etc.), use 3 newlines. Otherwise, only deploy single newlines — and even then, use them sparingly. However, with nested sections — unless lengthy — avoid applying this rule (e.g., `functions` in `classes`).
- **Multi-line Brackets** — When opening brackets or parentheses across multiple lines, open them up all the way, ensuring each hierarchy of bracket recieves its own line.

# Git Workflow

- Run `git commit` only after `git add`.
- Once changes are staged, commit without unnecessary delay so staged history is preserved.

# Debugging and Logging

- Do not guess behavior. Verify assumptions by reading source, fixtures, and tests.
- Debug with logs when behavior is unclear.
- Write sufficient logs for debugging and operational troubleshooting.