# Overview

- **Aim** — Developing genetic algorithm (GA) implementations to solve traveling salesman problem (TSP) instances.
- **Contextualization** — By thinking of each node in an instance as a planet in a star system, a moon in a planet system, or a landmark on a planet, the traveling salesman problem suddenly has appplications to space exploration.

# Coding Style

Keep all things short but descriptive. Try to not abbreviate unless it is common in the code base.

- **Variables** — Use camel case. Local iteration values should always be denoted with `i` or `j`. Local, short-lived, positional values should be denoted with letters from the alphabet, with the order they appear in corresponding to the order of the alphabet.
    - **Booleans** — Always start the variable with a boolean prefix (e.g., `can`, `has`, `is`, etc.).
    - **Constants** — Use screaming snake case.
- **Functions** — Use camel case. Always start the function with a verb (e.g., `run`, `calc`, etc.).
- **Classes** — Use pascal case.
- **Whitespace** — When separating functions, classes, or sections (e.g., `imports`, `variables`, `functions`, etc.), use 3 newlines. Otherwise, only deploy single newlines — and even then, use them sparingly.

# Debugging and logging

- Do not guess behavior. Verify assumptions by reading source, fixtures, and tests.
- Debug with logs when behavior is unclear.
- Write sufficient logs for debugging and operational troubleshooting.

# Git workflow

- Run `git commit` only after `git add`.
- Once changes are staged, commit without unnecessary delay so staged history is preserved.