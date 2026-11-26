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

**This repo's own setup:** the repo root is itself a single uv project, and it's the
**only** dependency manifest in the whole course — no session's `lab/` has its own
`pyproject.toml`, `uv.lock`, or `.venv`. Every session's notebooks AND S01's and S06's
standalone CLI apps (`main.py` + `pytest`) all install from and run inside this one root
environment. There's deliberately only one flat dependency list, not a group per
session, so there's nothing to figure out:

| Command (run from the repo root) | What it gets you |
|---|---|
| `uv sync` | Everything, every session needs — JupyterLab/notebook support, `pandas`, `pydantic`, `openai`, `python-dotenv`, `transformers`, `accelerate`, `tiktoken`, `pytest` |
| `uv run jupyter lab` | Opens JupyterLab inside this managed environment |
| `uv run pytest` | Runs S01's or S06's test suite (scoped to whichever folder you run it from) |

One `uv sync` is enough for any session's `.ipynb`, including S01's two notebooks (which
need only the local `triage` package beyond this). Each session's own `lab/README.md`
still has the exact commands for that session, including a plain `pip install`/Colab
alternative where one is offered (S03 is designed to also run in Google Colab, which
doesn't use this local environment).

**Why every notebook and both CLI apps work from one root environment:** `uv run` walks
up from your current directory to find the nearest `pyproject.toml` — so running
`uv run python main.py` or `uv run pytest` from inside
`sessions/S01-verified-agent-loops/lab/` or `sessions/S06-queue-harnesses-build-vs-buy/lab/`
resolves to this root project automatically, while your working directory (and so each
app's relative data paths, and `pytest`'s default test discovery) stays exactly where you
ran it from. Jupyter does the equivalent for notebooks: it starts each notebook's kernel
with its working directory set to wherever that `.ipynb` file lives, regardless of which
directory you launched `jupyter lab` from — so `S01_Northstar_Triage_Notebook.ipynb` and
`Tool_Calling_From_Scratch.ipynb` can `import triage.core` and read
`sessions/S01-verified-agent-loops/lab/data/tickets.json` correctly even though the
kernel itself is this root environment. The root `pyproject.toml`'s
`[tool.pytest.ini_options]` adds both labs' folders to `pythonpath` and sets
`--import-mode=importlib`, so `uv run pytest sessions` from the root can collect both
labs' same-named `tests/test_core.py` in one run with no import collision.

## Secrets and `.env`

There is exactly **one** `.env.example` in the whole repo, at the **root** — no session's
`lab/` has its own. Copy it to `.env` (also at the root; never commit it) and fill in only
the keys you need. Every session's optional live-model notebook cell, and S01's and S06's
standalone CLI apps (`triage/live.py` already calls `load_dotenv()`), call python-dotenv's
`load_dotenv()`, which walks up the directory tree from wherever the code runs until it
finds a `.env` — so the root one is found automatically no matter which session's folder
you're running from.

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
