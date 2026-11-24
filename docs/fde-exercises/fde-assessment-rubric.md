# FDE Assessment Rubric — Cross-Session Decision Exercises

**Companion to:** `prompt-engineering-decision.md`, `llm-fundamentals-decision.md`,
`structured-output-model-decision.md`, `verified-agent-loop-decision.md`,
`model-technique-bakeoff-decision.md`, `open-weight-local-deployment-decision.md`,
`queue-harness-build-vs-buy-decision.md`.

Each of the seven decision exercises has its own per-exercise rubric, scoped to that
session's technical content. This document is the layer above those seven: a single,
reusable scale for the **FDE mindset itself** — the eight skills this course defines FDE
competence by — so an instructor scores the *mindset*, consistently, across all seven
exercises, not just each exercise's technical correctness.

This rubric extends the course's existing competency codes (`COMPETENCIES.md`) rather
than inventing a parallel system — every FDE skill below maps onto codes already in use
by the quizzes and interview-prep banks.

---

## The eight FDE skills, mapped to existing competency codes

| # | FDE skill | Primary competency code(s) | Why that mapping |
|---|---|---|---|
| 1 | Understand an ambiguous customer problem | C6, C2 | Requires reading a stakeholder's actual need, not just the stated request — customer delivery and architecture judgment together. |
| 2 | Identify where an LLM is useful and where it is not | C2, C1 | A solution-architecture judgment grounded in fundamentals (model call vs. rules vs. agent). |
| 3 | Scope a realistic POC | C2, C6 | Architecture plus the discipline to state what's in/out and what "done" means to a customer. |
| 4 | Make justified technical trade-offs | C2, C4 | Architecture decisions defended with evidence, not preference. |
| 5 | Integrate AI into existing software workflows | C3 | This course's own definition of Integration Engineering. |
| 6 | Validate quality and reliability | C4 | This course's own definition of Evaluation, Reliability & Security. |
| 7 | Explain costs, limitations, and risks | C5, C6 | Deployment/operations substance, delivered in customer-facing language. |
| 8 | Communicate recommendations to customer stakeholders | C6 | This course's own definition of Customer-Facing Technical Delivery. |

## Which exercise actually exercises which skill

| Skill | S00 (Prompt) | S03 (LLM Fundamentals) | S02 (Structured Outputs) | S01 (Agent Loops) | S04 (Bake-Offs) | S05 (Open-Weight/Local) | S06 (Queue Harnesses) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1. Ambiguous problem | ✅ (vague "reduce churn" ask) | — | ✅ (two stakeholders, conflicting vocabulary) | ✅ (two stakeholders, competing priorities) | ✅ (VP's stated want vs. the actual cost/risk question) | ✅ (account team's assumption vs. the actual residency constraint) | ✅ (lead's "faster to build" want vs. the actual unverified risk) |
| 2. LLM fit judgment | ✅ (prompt-only vs. a build) | — | — | ✅ (agent loop vs. rules/single-call) | — | — | — |
| 3. Scope a POC | ✅ (one-week, no budget) | — | — | — | — | — | — |
| 4. Justified trade-offs | — | ✅ (cost/latency/context levers) | ✅ (model A vs. B, evidence-based) | ✅ (autonomy level, risk-based) | ✅ (accuracy vs. volume-scaled cost) | ✅ (accuracy vs. cost/latency/memory/residency) | ✅ (build-vs-buy, verified vs. documented claims) |
| 5. Integrate into workflows | — | — | ✅ (downstream auto-routing contract) | ✅ (tool dispatch into existing harness) | — | — | ✅ (orchestration framework adoption decision) |
| 6. Validate quality/reliability | ✅ (naive vs. few-shot comparison) | — | ✅ (critical-error definition, model comparison) | ✅ (verification rules) | ✅ (routing-signal false-negative validation) | ✅ (topic-hint validation, hosted/local mismatch as bug) | ✅ (crash-simulation verification plan) |
| 7. Costs, limitations, risks | ✅ (caveat in the memo) | ✅ (this exercise's central subject) | — (caveat in recommendation) | ✅ (escalation/compliance risk) | ✅ (this exercise's central subject) | ✅ (this exercise's central subject) | ✅ (cost of a repeat incident) |
| 8. Communicate to stakeholders | ✅ (one-page memo) | ✅ (production-config memo) | ✅ (acceptance checklist) | ✅ (authorization design one-pager) | ✅ (recommendation-plus-validation-plan) | ✅ (constraint-first recommendation) | ✅ (build-vs-buy recommendation) |

No single exercise exercises all eight skills — that's deliberate. Across all seven,
every skill gets exercised at least once, and most at least twice, which is what lets an
instructor distinguish "this learner struggled once, in one context" from "this learner
consistently struggles with skill 4 regardless of session."

## The reusable 0–3 scale

Use this scale for **each of the eight skills**, scored against whichever exercise(s) a
learner has completed — not a new scale invented per exercise.

| Score | Observable behavior |
|---|---|
| **0 — Missing** | Skips the judgment call entirely, or answers a different, easier question than the one actually asked. |
| **1 — Emerging** | Names the right concept but gives a generic answer with no specific number, stakeholder, or constraint from the actual brief. |
| **2 — Competent** | Gives a specific, workable answer tied to the brief's actual details, with at least one limitation acknowledged. |
| **3 — Strong** | Adds a concrete trade-off, a named risk, or a stakeholder-specific framing that goes beyond what the exercise's prompts explicitly asked for. |

## Per-learner scoring sheet (reuse across all seven exercises)

| Skill | S00 score | S03 score | S02 score | S01 score | S04 score | S05 score | S06 score | Notes |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 1. Ambiguous problem | | n/a | | | | | | |
| 2. LLM fit judgment | | n/a | n/a | | n/a | n/a | n/a | |
| 3. Scope a POC | | n/a | n/a | n/a | n/a | n/a | n/a | |
| 4. Justified trade-offs | n/a | | | | | | | |
| 5. Integrate into workflows | n/a | n/a | | | n/a | n/a | | |
| 6. Validate quality/reliability | | n/a | | | | | | |
| 7. Costs, limitations, risks | | | n/a | | | | | |
| 8. Communicate to stakeholders | | | | | | | | |

### ⚠️ Red flags, across any exercise

- Treats a technically correct artifact (a valid contract, a working loop, a well-written
  prompt) as sufficient on its own, with no stakeholder framing or caveat attached.
- Picks the most impressive-sounding technical option (full agent autonomy, maximum
  context, the newest model) without evidence that the simpler option was even
  considered.
- Gives a recommendation with no stated assumption or limitation anywhere in it.
- Answers the technical question asked but never states what the customer should
  actually *decide* — the artifact reads as an engineering note, not a decision memo.

### ✅ What distinguishes a 3 from a 2, consistently

A "2" gets the mechanism right and names a limitation. A "3" does that **and** makes a
visible trade-off decision a reasonable person could disagree with, then defends it — the
difference between "here's an analysis" and "here's what I'd actually do, and why."

## How this complements, not replaces, existing assessment

- **Session quizzes** (`quiz.md`) test technical recall and mechanism — can the learner
  compute a cost, trace a loop, validate a contract. These seven exercises assume that
  layer is already solid and test judgment *on top of it*.
- **Interview-prep banks** (`interview-prep.md`) rehearse verbal reasoning and trade-off
  defense in a mock-interview format. These exercises produce a written artifact instead,
  under a tighter 10–15 minute timebox, closer to what an actual client engagement
  demands than an interview conversation is.
- **This rubric** is the one thing neither of those already provides: a *cross-session*
  view of whether the FDE mindset itself is developing, not just session-by-session
  technical competence.
