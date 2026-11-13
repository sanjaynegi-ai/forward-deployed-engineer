# Tooling setup

One-time environment setup, referenced by every session's lab instead of re-taught in
each one. You're assumed to be an experienced engineer who may simply never have used
these specific tools before — this is a translation layer, not a tutorial.

## Python projects with `uv`

If you know npm, Maven, or similar: `uv` plays the same role for Python — managing the
interpreter, dependencies, and a reproducible environment, in one tool.

| Command | What it does |
|---|---|
| `uv --version` | Confirm `uv` is installed |
| `uv init <name>` | Create a new project |
| `uv python pin 3.12` | Select the project's Python version |
| `uv add <package>` | Add a dependency |
| `uv add --dev <package>` | Add a development-only dependency |
| `uv sync` | Reconcile the local environment with the project's declared dependencies/lockfile |
| `uv run <command>` | Run a command inside the project's managed environment |
| `uv run pytest` | Run the test suite |
| `uv tree` | Inspect the dependency graph |

**Project files:** `pyproject.toml` declares dependencies; `uv.lock` records the exact
resolved versions (commit it, for a reproducible setup); `.venv/` is the local environment
(never commit it, and never commit `.env` secrets either).

## VS Code

Install the Python and Jupyter extensions, then select the project's `.venv` as the
interpreter/kernel when prompted. Each lab's own `README.md` has its exact quick-start
commands — this page only covers the parts common to all of them.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
