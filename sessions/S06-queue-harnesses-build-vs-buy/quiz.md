# S06 Learner Quiz — Queue Harnesses: Orchestrating at Scale, Build vs. Buy

**AI-Focused Forward Deployed Engineering · Session 06**
**Scenario:** Northstar Support Systems (fictional); synthetic support-ticket queue
**Prerequisites:** S01: Verified Agent Loops

## Purpose and administration

This assessment checks whether you can design a crash-safe, idempotent state machine
for orchestrating many items, explain why giving each item a fresh decision call
matters, distinguish transient from chronic failure, and weigh a hand-rolled harness
against a ready-made framework with a concrete verification plan, not a default
preference.

- **Suggested time:** 25–35 minutes, answering each question before opening its answer.
- **Total:** 56 points, 10 questions. Partial credit is permitted where specified.
- **Primary competencies:** C3 (Integration Engineering), C4 (Evaluation, Reliability, Security). **Secondary:** C1 (AI Engineering Fundamentals), C2 (AI Solution Architecture), C6 (Customer-Facing Technical Delivery).
- **Assumptions:** All Northstar tickets are synthetic. The queue harness's `decide_fn` is a deterministic stand-in, not a real model call — single-item decision correctness (S01, S02) is **not** in scope here.
- **How to take it:** Answer each question yourself before expanding its **Answer** section.

---

## Section 1 — Concepts (Q1–Q3)

### Q1. Why no separate duplicate check is needed (2 points)
**Difficulty:** Foundational · **Competency:** C3 · **Type:** Multiple choice

A queue harness only ever processes tickets whose status is `pending`; `done` and
`needs_review` tickets are skipped unconditionally. Why does this alone prevent a ticket
from being reprocessed after a restart?

A. Because the harness checks a separate log of previously processed ticket IDs.
B. Because the state transition itself removes a finished ticket from the set the loop ever looks at again — there's no code path back to it.
C. Because the decide_fn function remembers which tickets it has already seen.
D. Because tickets are deleted from the queue once finished.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** B (2 points)

**Explanation:** The loop's own condition (`if ticket.status != "pending": continue`) is
the entire guarantee — once a ticket leaves the `pending` state, nothing in the loop's
logic can select it again. No separate deduplication mechanism is needed because the
state machine's shape already prevents it.

**Misconception:** Idempotency requires an explicit "have I seen this before" check —
sometimes it does (S01's `create_escalation`), but here it's a free consequence of the
state machine's design.

</details>

### Q2. Transient versus chronic (4 points)
**Difficulty:** Foundational · **Competency:** C4 · **Type:** Short answer

Explain the difference between a transient failure and a chronic one, and what the
harness should do differently for each.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Retry vs. escalate (4 points)

A transient failure is one where trying again has a real chance of succeeding — a
timeout, a momentary unavailability — so the correct response is a bounded retry (2). A
chronic failure keeps failing for a reason that retrying won't fix; after a bounded
number of attempts, the correct response is to stop retrying and hand the item to a
human instead of looping forever (2).

**Misconception:** Every failure should either always retry or never retry — the
correct behavior depends on whether retrying has a real chance of succeeding, and a
bounded attempt budget is what turns an unknown into a decision either way.

</details>

### Q3. What a fresh subagent per item actually buys you (4 points)
**Difficulty:** Intermediate · **Competency:** C1, C3 · **Type:** Short answer

Give **two** concrete costs of letting one long conversation accumulate across an entire
queue, instead of giving each item its own independent decision call.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Two costs, 2 points each (4 points)

**Strong answer examples:** Cost grows with every item processed, independent of that
item's own difficulty, because the accumulated history gets resent on every call; one
item's malformed or confused exchange can leak into and corrupt how a later item gets
decided, since they share context; a single long conversation is also a single point of
failure for the whole run, instead of isolating each item's failure to itself. Any two
distinct, well-explained costs earn full credit.

**Misconception:** More context (the whole queue's history) can only help, never hurt or
cost more — this is the same "attach everything" fallacy S02 and S05 already warned
about, applied to an orchestration loop instead of a single prompt.

</details>

## Section 2 — Measurement and design (Q4–Q7)

### Q4. Trace the queue across capped runs (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Numerical interpretation

A queue starts with 20 pending tickets, no failures occur, and a run processes at most
`cap=7` tickets before saving state and stopping. Fill in `done` and `pending` after
each of three consecutive runs.

| Run | Done | Pending |
|---|---:|---:|
| 1 | | |
| 2 | | |
| 3 | | |

<details>
<summary><strong>Answer</strong></summary>

**Answer:** (6 points, 2 per row)

| Run | Done | Pending |
|---|---:|---:|
| 1 | 7 | 13 |
| 2 | 14 | 6 |
| 3 | 20 | 0 |

Run 3 only has 6 pending tickets left, so it processes all 6 even though `cap=7` would
allow one more — there's nothing left to process beyond what's actually pending.

**Misconception:** `cap` guarantees exactly that many tickets get processed every run —
it's a ceiling, not a target; a run processes `min(cap, pending_count)`.

</details>

### Q5. Debug the fault-injection bug (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Debugging

A teammate's retry-simulation helper tracks each ticket's attempt count in its own
dictionary, separate from the harness's own `ticket.attempts` field:

```python
def with_fault_injection(decide_fn, fail_first):
    seen = {}

    def wrapped(ticket_id):
        seen[ticket_id] = seen.get(ticket_id, 0) + 1
        if ticket_id in fail_first and seen[ticket_id] == 1:
            raise TransientError("simulated failure")
        return decide_fn(ticket_id)

    return wrapped
```

This works correctly inside a single test function, but produces the wrong behavior
when used in a CLI that restarts between runs. What goes wrong, and why?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** The counter resets on every process restart (6 points)

`seen` is a plain in-memory dictionary inside the closure — it only exists for the
lifetime of one process (3). A CLI that restarts between runs creates a fresh `wrapped`
function with an empty `seen` dict each time, so a ticket meant to fail once and then
succeed on the next run's retry instead sees `seen[ticket_id] == 1` again on that next
run and fails *again* — "fail once" silently becomes "fail every run" (3). The fix is to
base the check on the harness's own persisted attempt count (read from the same state
that was saved to disk), not a separate counter that doesn't survive a restart.

**Misconception:** Code that passes a test exercising it within one process is
necessarily correct for a CLI that restarts between invocations — passing a test and
surviving a restart are different claims, and this exact bug is the gap between them.

</details>

### Q6. A ticket vanishes from the report (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Debugging

After a code change, a queue's `done + needs_review + pending` total comes out one
short of the actual ticket count on some runs. What kind of bug produces this symptom,
and what check would have caught it immediately?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** A ticket silently skipped without a status update (6 points)

This symptom means some code path processed (or ignored) a ticket without recording any
resulting status for it — e.g., an exception escaping the per-ticket handling before the
status gets set, or an off-by-one in whatever iterates the ticket set (3). The fix the
lab's own `report()` function demonstrates: assert the invariant
(`done + needs_review + pending == total`) on every call, so this class of bug fails
loudly and immediately instead of surfacing later as "a customer's ticket just
disappeared" (3).

**Misconception:** This kind of bug will surface on its own eventually — without an
explicit invariant check, a silently dropped ticket can sit unnoticed until a human
notices a specific missing ticket days later.

</details>

### Q7. Verify a framework's durability claim (6 points)
**Difficulty:** Advanced · **Competency:** C4, C2 · **Type:** Eval design

A ready-made framework's documentation says it "automatically retries failed steps."
Design one concrete test you'd run before trusting that claim for a production queue.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Simulate a mid-run crash and inspect the result (6 points)

Start a run on a known set of items, kill the process partway through (or use the
framework's own crash-simulation tooling if it has one), restart it, and inspect the
final state (3). Specifically check: was any item decided twice, does its own account
of "how many items finished" match reality, and did a chronically-failing item
eventually stop retrying and surface to a human rather than looping or silently
vanishing (3). "Retries failed steps" and "is crash-safe and idempotent" are related but
separate claims — the documentation naming one doesn't confirm the other.

**Misconception:** A framework's stated feature list is sufficient evidence that it
provides the specific guarantee (idempotent, crash-safe resumption) your system actually
needs.

</details>

## Section 3 — FDE decisions (Q8–Q10)

### Q8. The build-vs-buy recommendation (8 points)
**Difficulty:** Advanced · **Competency:** C6, C2 · **Type:** Customer communication

After a different team's framework-based queue reprocessed and double-escalated 40
already-handled tickets following a crash, Northstar's engineering lead asks whether to
adopt that same framework for this project anyway, "since it's faster to build with."
Write a **3–5 sentence** response.

<details>
<summary><strong>Answer</strong></summary>

**Example response (8 points):**

> "Speed to build is real, but that incident shows the framework's retry/checkpoint
> behavior didn't match what we actually needed — no item should ever be decided twice,
> and theirs was. Before adopting it here, I'd want to specifically test its crash-
> recovery behavior against that exact failure mode, not just take 'automatic retries'
> at face value. If it can't demonstrably guarantee idempotent resumption, a hand-rolled
> harness — which gave us that guarantee directly, in code we fully control — is the
> safer default for this specific requirement, even if it costs more time upfront."

**Rubric:** acknowledges the real speed benefit without dismissing it (2); correctly
identifies the incident as a durability-guarantee failure, not an unrelated issue (2);
proposes a concrete verification step rather than a blanket yes/no (2); gives a
defensible conditional recommendation (2).

**Common weak response:** "We should never use frameworks after an incident like that"
— overgeneralizing from one framework's specific failure to all frameworks, rather than
treating it as evidence to verify against for this one.

</details>

### Q9. When hand-rolling is overkill (6 points)
**Difficulty:** Advanced · **Competency:** C2 · **Type:** Architecture

Under what conditions would you recommend the ready-made framework over hand-rolling
this session's harness, even knowing the incident described in Q8?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Two defensible conditions (6 points, 3 each)

If the actual business consequence of an occasional double-processed item is low (e.g.,
the action isn't something costly or irreversible, unlike Northstar's escalations), the
framework's convenience may outweigh a risk that's cheap to tolerate or clean up after.
If the team has already verified the framework's durability guarantees — through a test
like Q7's, not just documentation — and they hold up under a real crash simulation, the
original incident becomes evidence about *that* framework's actual behavior rather than
a reason to hand-roll by default.

**Misconception:** The Q8 incident proves hand-rolling is always the safer choice —
it's evidence about one framework's unverified behavior, not a general rule against
ready-made orchestration tools.

</details>

### Q10. Investigate the double-escalation incident (8 points)
**Difficulty:** Advanced · **Competency:** C4, C3 · **Type:** Troubleshooting

You're asked to investigate the Q8 incident directly: why did the framework reprocess
40 already-handled tickets after a crash? Describe your investigation.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Find where "done" and "persisted" diverged (8 points)

First, determine whether the framework actually persisted each item's completion
*before* or *after* whatever crashed — a framework that marks an item complete only in
memory, writing to durable storage on a delay or a batch, can lose exactly the items
that completed just before a crash, making them look "never processed" on restart (3).
Second, check whether the framework's own retry logic can distinguish "this item was
never attempted" from "this item finished but the completion record didn't make it to
disk in time" — if it can't, a crash at the wrong moment turns a completed item back
into a pending one, which is exactly the harness's own no-lost-no-double-counted
invariant failing silently on their side (3). Third, confirm the escalation side effect
itself (not just the status update) is idempotent — even with perfect status tracking, a
retried item that re-triggers a real side effect (an escalation, here) needs its own
duplicate-prevention, the same category of problem S01's `create_escalation` solved for
one ticket (2).

**Misconception:** "The framework says it has automatic retries" is itself an
explanation — the actual question is what, specifically, its checkpoint-and-retry
mechanism does and doesn't guarantee about already-completed work.

</details>

---

## Submission checklist

- [ ] I explained idempotency here as a consequence of the state machine, not a separate check.
- [ ] I correctly distinguished a cap as a ceiling, not a guaranteed per-run count.
- [ ] I identified the specific mechanism by which separate, unpersisted retry state drifts from the harness's own record.
- [ ] I designed a crash-simulation test for a durability claim, not just cited the claim.
- [ ] I gave a conditional, evidence-based build-vs-buy recommendation, not a blanket rule.

## Scoring overview

| Q | Difficulty | Competency | Format | Points |
|---|---|---|---|---:|
| 1 | Foundational | C3 | MCQ | 2 |
| 2 | Foundational | C4 | Short answer | 4 |
| 3 | Intermediate | C1, C3 | Short answer | 4 |
| 4 | Intermediate | C4 | Numerical interpretation | 6 |
| 5 | Intermediate | C4 | Debugging | 6 |
| 6 | Intermediate | C4 | Debugging | 6 |
| 7 | Advanced | C4, C2 | Eval design | 6 |
| 8 | Advanced | C6, C2 | Customer communication | 8 |
| 9 | Advanced | C2 | Architecture | 6 |
| 10 | Advanced | C4, C3 | Troubleshooting | 8 |
| **Total** | | | | **56** |

## 🔍 Interpret your results

**Suggested self-assessment ranges (not certification thresholds):** 47–56 strong; 37–46
developing; 0–36 revisit relevant concepts. These are not empirically validated cut
scores.

**Diagnose by concept:**
- Q1, Q2, Q3: the state-machine design itself and why a fresh subagent per item matters.
- Q4: tracing a capped run's progress correctly.
- Q5, Q6: finding the specific mechanism behind a restart-sensitive or invariant-violating bug.
- Q7, Q10: verifying (or investigating a failure in) a durability guarantee concretely.
- Q8, Q9: build-vs-buy judgment that depends on evidence, not a default preference either way.

**Coverage note:** This quiz assesses queue-orchestration design — it does not re-test
S01's single-item harness/verification mechanics or S02's contract validation.

> [!NOTE]
> Q5's bug and the handout's §3 warning both describe a real defect caught while
> building this lab's own CLI, not a hypothetical example.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
