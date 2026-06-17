# Agent Rules

## While Working in `.`

- Refer to `./.claude/AGENTS.md`

## While Working in `./stdout/runs/`

- Do not interfere with any pre-existing run files.
- Ensure that test runs will not interfere with any pre-existing run files.

## General Rules

- Understand the codebase and its conventions — the codebase is the source of truth. You should prefer reading source code over searching.
- Do not search web unless explicitly prompted. Web search does not help in general for this project.
- Write performant code. Always prefer performance over other aspects.
- Use `gh` CLI tool for fetching data from `github.com`.
- This is a Windows system, not a macOS or Linux Bash environment.

## Coding Conventions

- Write comments and documentations in English.
- Commit your work as frequent as possible using git. Do not use the `--no-verify` flag.
- Always describe commits — attach descriptions to all commits, addressing what was done, why it was done, and important points of interest.
- Prefer multiple smaller files over single larger files.