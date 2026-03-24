# AGENTS.md

## Scope
This file applies to the entire repository.

## Project conventions
- Keep code modular (`ui`, `core`, `geometry`, `lbm`, `upscaling`, `visualization`, `io`).
- All core classes/functions should include type hints and docstrings.
- Use UTF-8 and avoid hard-coded personal paths.
- Prefer explicit placeholders with user-visible messages over silent no-op behavior.
- Keep GUI actions wired; unavailable features must show clear status/warning.
