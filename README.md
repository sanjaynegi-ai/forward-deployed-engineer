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
| S00 | [Prompt Engineering Foundations](sessions/S00-prompt-engineering-foundations/handout.md) | A prompt as a specification, not a question; six reusable prompt patterns (Persona, Chain-of-Thought, Question Refinement, Few-Shot, Flipped Interaction, Semantic Filter + Recipe); naive-vs-patterned comparison; when a prompt-only workflow stops being enough |
| S01 | [Verified Agent Loops](sessions/S01-verified-agent-loops/handout.md) | Model calls vs. tool execution vs. agent loops; harness engineering; independent verification; when *not* to use an agent |
| S02 | [Structured Outputs and Model Selection](sessions/S02-structured-outputs-and-model-selection/handout.md) | Model vs. serving API vs. application; tokens, context, and cost; Pydantic contracts; schema validity vs. business correctness; task-first model comparison |
| S03 | [LLM Fundamentals](sessions/S03-llm-fundamentals/handout.md) | Tokens and tokenization; the full prompt-to-response path; embeddings and logits at an intuitive level; inference vs. training; the next-token generation loop vs. an agent loop; context windows; streaming vs. non-streaming; LLM vs. inference runtime vs. provider API |

S00, S01, S02, and S03 are all foundational and don't depend on each other. S00 stays
entirely inside prompt-only workflows; S01 goes deep on the agent loop/harness mechanism;
S02 goes deep on trusting a single structured decision; S03 goes one layer below all
three, into what actually happens inside a single model call. S00 is a natural starting
point since it needs no code; S03 is a natural starting point if you want the mechanism
before the engineering judgment calls the other three ask for. All four can be taken in
any order.

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

[`docs/fde-exercises/fde-assessment-rubric.md`](docs/fde-exercises/fde-assessment-rubric.md)
gives instructors a single, reusable scale for the FDE mindset itself, scored across all
four exercises rather than once per session.

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
