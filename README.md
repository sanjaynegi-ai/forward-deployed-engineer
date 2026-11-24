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

## Start here

New to this course? Work through the sessions in this order — it's the default reading
path, not a dependency chain (see **Sessions** below for why order doesn't actually
matter):

1. **[S00 — Prompt Engineering Foundations](sessions/S00-prompt-engineering-foundations/handout.md)**
   — no code required; start here if you want the judgment calls before the mechanism.
2. **[S01 — Verified Agent Loops](sessions/S01-verified-agent-loops/handout.md)**
   — the first real code lab; builds and verifies a tool-using agent loop.
3. **[S02 — Structured Outputs and Model Selection](sessions/S02-structured-outputs-and-model-selection/handout.md)**
   — typed contracts and choosing a model for a task, not a benchmark.
4. **[S03 — LLM Fundamentals](sessions/S03-llm-fundamentals/handout.md)**
   — one layer below the other three: what actually happens inside a single model call.

Two more sessions each build on a specific pair of the above, independently of each
other — do either, both, or neither, in whatever order their own prerequisites allow:

5. **[S04 — Model and Technique Bake-Offs](sessions/S04-model-and-technique-bakeoffs/handout.md)**
   — puts S01's and S02's techniques on the same task and measures which one actually
   earns its cost. **Requires S01 and S02 first.**
6. **[S05 — Open-Weight, Local Models, and Token Economics in Practice](sessions/S05-open-weight-local-models-and-token-economics/handout.md)**
   — the same measurement discipline applied to *which model* and *where it runs*,
   plus what trimming context really costs and saves. **Requires S02 and S03 first.**
7. **[S06 — Queue Harnesses: Orchestrating at Scale, Build vs. Buy](sessions/S06-queue-harnesses-build-vs-buy/handout.md)**
   — extends S01's one-ticket harness into one agent working an entire queue on its
   own, crash-safely. **Requires S01 first.**

Each session's `handout.md` is itself the entry point for that session — it links out to
that session's own `quiz.md`, `interview-prep.md`, and `lab/`.

**One-time environment setup:** this repo is a [uv](https://docs.astral.sh/uv/)-managed
Python project. From the repo root, `uv sync` gets you a working Jupyter environment, and
`uv sync --group s00` (or `s02`, `s03`) adds the one or two extra packages that session's
lab needs. See [`docs/TOOLING.md`](docs/TOOLING.md) for the full command reference,
including the plain-`pip`/Google Colab alternative each lab also offers. S01's lab is a
standalone Python application with its own separate uv project — see its own
`lab/README.md`.

## Sessions

| # | Session | What it covers |
|---|---|---|
| S00 | [Prompt Engineering Foundations](sessions/S00-prompt-engineering-foundations/handout.md) | A prompt as a specification, not a question; six reusable prompt patterns (Persona, Chain-of-Thought, Question Refinement, Few-Shot, Flipped Interaction, Semantic Filter + Recipe); naive-vs-patterned comparison; when a prompt-only workflow stops being enough |
| S01 | [Verified Agent Loops](sessions/S01-verified-agent-loops/handout.md) | Model calls vs. tool execution vs. agent loops; harness engineering; independent verification; when *not* to use an agent |
| S02 | [Structured Outputs and Model Selection](sessions/S02-structured-outputs-and-model-selection/handout.md) | Model vs. serving API vs. application; tokens, context, and cost; Pydantic contracts; schema validity vs. business correctness; task-first model comparison |
| S03 | [LLM Fundamentals](sessions/S03-llm-fundamentals/handout.md) | Tokens and tokenization; the full prompt-to-response path; embeddings and logits at an intuitive level; inference vs. training; the next-token generation loop vs. an agent loop; context windows; streaming vs. non-streaming; LLM vs. inference runtime vs. provider API |
| S04 | [Model and Technique Bake-Offs](sessions/S04-model-and-technique-bakeoffs/handout.md) | Measuring a single structured call (S02) against a verified agent loop (S01) on the same task — accuracy, cost, and latency together, not accuracy alone; confidence-gated tiered dispatch; validating a routing signal's false-negative rate before trusting it in production. **Requires S01 and S02.** |
| S05 | [Open-Weight, Local Models, and Token Economics in Practice](sessions/S05-open-weight-local-models-and-token-economics/handout.md) | Open-weight vs. closed-weight (a deployment question, not an accuracy one); hosted vs. local (cost/latency/memory, not accuracy); measuring real token savings from trimming context with a tokenizer, including a case where trimming *improves* accuracy; data residency as a hard constraint, not a cost line. **Requires S02 and S03.** |
| S06 | [Queue Harnesses: Orchestrating at Scale, Build vs. Buy](sessions/S06-queue-harnesses-build-vs-buy/handout.md) | Extending a single-item verified loop into a harness that works an entire queue on its own; a state machine where idempotency and crash-safety are structural, not bolted on; bounded retry vs. escalation for chronic failures; a real bug caught while building it; build vs. buy against a ready-made orchestration framework. **Requires S01.** |

S00, S01, S02, and S03 are all foundational and don't depend on each other. S00 stays
entirely inside prompt-only workflows; S01 goes deep on the agent loop/harness mechanism;
S02 goes deep on trusting a single structured decision; S03 goes one layer below all
three, into what actually happens inside a single model call. S00 is a natural starting
point since it needs no code; S03 is a natural starting point if you want the mechanism
before the engineering judgment calls the other three ask for. All four can be taken in
any order. S04, S05, and S06 are the exception to that independence: each is a synthesis
or extension session that assumes specific prerequisites — S04 needs S01+S02, S05 needs
S02+S03, S06 needs S01 — but S04, S05, and S06 don't depend on each other.

(More sessions land here as they're ready.)

Each session folder has the same shape:
- `handout.md` — the concept reference
- `quiz.md` — a short formative check
- `interview-prep.md` — a deeper, judgment-oriented self-study question bank
- `lab/` — a real, runnable project for the session's scenario

## FDE decision exercises

Each session includes a short "Forward Deployed Engineer Decision Challenge" — a
10–15-minute, customer-facing judgment call that follows the session's technical content,
with a full brief, rubric, and worked strong/weak examples in `docs/fde-exercises/`:

| Session | Exercise | Customer tension |
|---|---|---|
| S00 | [`prompt-engineering-decision.md`](docs/fde-exercises/prompt-engineering-decision.md) | Fund a larger engagement, or not, off a one-week prompt-only read |
| S01 | [`verified-agent-loop-decision.md`](docs/fde-exercises/verified-agent-loop-decision.md) | Broad autonomy vs. an unsigned-off compliance boundary |
| S02 | [`structured-output-model-decision.md`](docs/fde-exercises/structured-output-model-decision.md) | Two stakeholders, two conflicting ticket taxonomies |
| S03 | [`llm-fundamentals-decision.md`](docs/fde-exercises/llm-fundamentals-decision.md) | Predictable cost and latency at 50,000 tickets/day |
| S04 | [`model-technique-bakeoff-decision.md`](docs/fde-exercises/model-technique-bakeoff-decision.md) | A VP wants the more-accurate technique everywhere; Platform Engineering is worried about its cost at real volume and an unvalidated routing signal |
| S05 | [`open-weight-local-deployment-decision.md`](docs/fde-exercises/open-weight-local-deployment-decision.md) | A regulated-industry prospect's data-residency requirement rules out the model that won the trial, and the account team hasn't noticed yet |
| S06 | [`queue-harness-build-vs-buy-decision.md`](docs/fde-exercises/queue-harness-build-vs-buy-decision.md) | A ready-made framework double-escalated 40 tickets after a crash; engineering still wants to adopt it here "since it's faster" |

[`docs/fde-exercises/fde-assessment-rubric.md`](docs/fde-exercises/fde-assessment-rubric.md)
gives instructors a single, reusable scale for the FDE mindset itself, scored across all
seven exercises rather than once per session.

## Course resources

- [`GLOSSARY.md`](GLOSSARY.md) — terms this course defines itself, used across sessions
- [`COMPETENCIES.md`](COMPETENCIES.md) — the competency codes sessions tag questions with
- [`docs/TOOLING.md`](docs/TOOLING.md) — one-time environment/tooling setup (uv, etc.)
- [`docs/curriculum/`](docs/curriculum/) — curriculum planning, dependency mapping, and
  integration change logs (mentor/architect-facing, not learner-facing)

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
