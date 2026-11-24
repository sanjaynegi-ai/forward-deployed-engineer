# FDE Decision Exercise — Queue Harness Build vs. Buy

**Targets session:** S06 — Queue Harnesses: Orchestrating at Scale, Build vs. Buy
**Run after:** the handout's §5 (build vs. buy comparison table) — before the learner
has settled on a default preference either way.
**Timebox:** 10–15 minutes. **Artifact:** a build-vs-buy recommendation with a
verification plan.

---

## 1. Customer situation

A different team at Northstar already adopted a ready-made agent-orchestration
framework for a similar queue-processing job, specifically because it promised
"automatic retries" and let them ship in a fraction of the time a hand-rolled harness
would have taken. Last week, a mid-run crash during a deploy caused that framework to
restart its queue from an earlier checkpoint than expected — and it reprocessed 40
tickets that had already been correctly decided and escalated, triggering a second,
duplicate escalation for each of them. Nobody on that team had tested what the
framework actually does across a crash before putting it in front of real traffic.
Now Northstar's engineering lead wants to adopt the same framework for *this* project
too, "since it's faster to build with" — and is waiting on your recommendation.

## 2. Customer stakeholders

**The engineering lead** — focused on shipping velocity, has not yet connected the
recent incident to the specific guarantee this new project would also need.
**The on-call team that handled the incident** — has firsthand, specific knowledge of
exactly what went wrong, and would be the first to notice if it happened again.

## 3. Business objective

Decide whether to adopt the framework for this project, with a concrete plan to either
confirm it's safe or confirm it isn't — rather than either blocking the engineering
lead's request outright or approving it on the strength of "it's popular and well-
documented."

## 4. Available information

- The incident: a mid-run crash, an unexpected checkpoint rollback, and 40 duplicate
  escalations — a real, confirmed failure of exactly the no-lost-no-double-counted
  invariant this session's own hand-rolled harness was built to guarantee.
- The framework's own documentation states it "automatically retries failed steps."
- This project's hand-rolled alternative (this session's lab) has a tested, verified
  idempotency guarantee, at the cost of more code to write and maintain.

## 5. Missing information and reasonable assumptions

- No confirmation yet of *why* the framework's checkpoint rolled back further than
  expected — assume the root cause (a delayed-write checkpoint, a configuration issue,
  or something else) is not yet known.
- No test yet of whether the same failure mode is reproducible on demand, or was a rare
  edge case — assume you don't know which until you actually try to reproduce it.
- No confirmed business cost for this new project if the same incident recurred here —
  assume you'll need to state what that cost would be, not just that the incident was
  "bad."

## 6. Technical decision required

1. **A recommendation** — adopt the framework, hand-roll instead, or adopt it only
   after specific conditions are met — for this project specifically.
2. **A concrete verification plan**, if adoption is conditional: what test would
   actually confirm or rule out the same failure mode here.
3. **The cost of being wrong**, stated for this project's specific actions — not a
   generic "duplicates are bad" but what a duplicate escalation or decision would
   actually cost Northstar in this context.

## 7. Expected learner artifact

A short build-vs-buy recommendation, in four parts:

- **Recommendation** — adopt, hand-roll, or conditional adoption, stated plainly.
- **Verification plan** (if conditional) — the specific crash-simulation test you'd
  run, and what result would change your recommendation in either direction.
- **Cost of being wrong** — what a repeat of the incident would actually cost on this
  project, not a generic statement.
- **One caveat** — what even a successful verification test would not establish.

## 8. Evaluation rubric

| Criterion | What a passing answer shows | Points |
|---|---|---:|
| Doesn't treat the incident as a blanket argument against frameworks | Reasons about the specific guarantee that failed, not "frameworks are risky" in general | 2 |
| Doesn't treat "it's popular/documented" as sufficient evidence either | Requires a specific test before trusting the retry/checkpoint claim for this project | 2 |
| Verification plan is concrete and targeted | Names an actual crash-simulation test aimed at the exact failure mode from the incident | 3 |
| States a real cost of being wrong | Names a specific consequence for this project's actual actions, not a generic risk statement | 3 |
| Recommendation is conditional and falsifiable | States what result would change the recommendation, in either direction | 3 |
| Caveat is genuine | Names something even a passing test wouldn't establish (e.g., behavior under sustained load, rare failure modes) | 2 |
| **Total** | | **15** |

## 9. Instructor guidance

- **Timing:** 3 minutes to read the situation, 8 minutes to draft the four-part
  artifact, 3–4 minutes to compare recommendations across pairs/groups — expect genuine
  disagreement on where the line sits, which is the point.
- **The teaching hook:** make explicit that this incident is a real-world instance of
  the handout's §3 lesson (persisted vs. unpersisted state drifting apart after a
  restart) at the scale of a production framework, not just this lab's own small CLI
  bug — the mechanism is the same, only the blast radius is bigger.
- **Watch for:** learners who recommend "never use that framework again" without
  proposing any way it could regain trust — that's not a decision process, it's a
  grudge; also watch for learners who recommend adoption on the strength of "it's
  widely used" without engaging with the fact that the other team was *also* using it
  widely, right up until the incident.
- **A reasonable canonical answer**, if you want one to anchor discussion: conditional
  adoption — run a deliberate crash-simulation test against a realistic batch before
  this project goes live, specifically checking whether any item gets decided or
  escalated twice; if the test passes cleanly across multiple trials, adopt it; if it
  reproduces anything like the incident, hand-roll instead, since this project's
  escalations carry a real cost (a customer seeing a contradictory duplicate response)
  that isn't worth the time saved.

## 10. Example of a strong answer

> **Recommendation:** Conditional adoption. The framework isn't disqualified by one
> incident, but it hasn't yet demonstrated the specific guarantee this project needs.
>
> **Verification plan:** Run a crash-simulation test on a realistic batch of this
> project's own ticket volume: start a run, kill the process mid-batch at a few
> different points, restart, and check whether any ticket was decided or escalated
> twice. Run it enough times to catch a failure mode that might not reproduce on the
> first try. If it passes cleanly, adopt the framework; if it reproduces anything like
> the 40-ticket incident, hand-roll instead.
>
> **Cost of being wrong:** A duplicate escalation here means a customer-facing ticket
> gets two contradictory responses, and whoever handles the second one has to notice
> and clean up a mess the system itself should have prevented — a real trust cost with
> the customer, not just an internal inconvenience.
>
> **Caveat:** Even a clean result from this test wouldn't establish behavior under
> sustained production load over weeks, or guarantee the same checkpoint bug couldn't
> resurface under a different, untested crash timing.

**Why it works:** the recommendation is conditional and states exactly what would
change it in either direction; the verification plan targets the specific failure mode,
not a generic "test it more"; the cost of being wrong is concrete to this project, not
borrowed wholesale from the other team's incident; the caveat names a real, specific
limitation instead of a boilerplate disclaimer.

## 11. Example of an inadequate answer, and why it fails

> "Given what just happened, we should definitely not use that framework — we'll build
> our own instead, it's safer. If we ever do decide to use a framework, we'll just read
> the docs more carefully next time."

**Why it fails:**
- Treats one incident as a permanent disqualification without proposing any test that
  could ever change that conclusion — not a falsifiable recommendation, just a reaction.
- "Read the docs more carefully" is not a verification plan — the other team likely did
  read the "automatic retries" claim; the actual gap was never testing it against a real
  crash, which this answer doesn't propose doing either.
- Never states what a repeat of the incident would actually cost on *this* project —
  the recommendation to hand-roll is asserted as "safer" without grounding that in a
  concrete consequence specific to this context.
