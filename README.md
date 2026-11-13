# AI-Focused Forward Deployed Engineering

A course for experienced software engineers (5+ years, any OOP language) moving into AI
engineering and Forward Deployed Engineering work. No general programming, git, or
command-line fundamentals are taught — the material assumes you have them and focuses on
what's specific to building and shipping AI agents for a customer.

## How to use this repo

Each session is self-contained: its own scenario, its own small project, its own
assessment. There is no running capstone threading the sessions together, so you can work
through them in order or jump to whichever topic you need. It works equally well read
async/self-paced or as material for a live, instructor-led session — nothing here assumes a
particular calendar.

## Sessions

| # | Session | What it covers |
|---|---|---|
| S01 | [Verified Agent Loops](sessions/S01-verified-agent-loops/handout.md) | Model calls vs. tool execution vs. agent loops; harness engineering; independent verification; when *not* to use an agent |
| S02 | [Structured Outputs and Model Selection](sessions/S02-structured-outputs-and-model-selection/handout.md) | Model vs. serving API vs. application; tokens, context, and cost; Pydantic contracts; schema validity vs. business correctness; task-first model comparison |

S01 and S02 are both foundational and don't depend on each other — S01 goes deep on the
agent loop/harness mechanism, S02 goes deep on trusting a single structured decision.
Take them in either order.

(More sessions land here as they're ready.)

Each session folder has the same shape:
- `handout.md` — the concept reference
- `quiz.md` — a short formative check
- `interview-prep.md` — a deeper, judgment-oriented self-study question bank
- `lab/` — a real, runnable project for the session's scenario

## Course resources

- [`GLOSSARY.md`](GLOSSARY.md) — terms this course defines itself, used across sessions
- [`COMPETENCIES.md`](COMPETENCIES.md) — the competency codes sessions tag questions with
- [`docs/TOOLING.md`](docs/TOOLING.md) — one-time environment/tooling setup (uv, etc.)

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software
engineers and technology leaders transition into high-value AI roles, including
**AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained
more than 1,100 experienced engineers.

<p align="center">
  <img src="assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60">
</p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center">
  <a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>
  &nbsp;&middot;&nbsp;
  <a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
</p>
