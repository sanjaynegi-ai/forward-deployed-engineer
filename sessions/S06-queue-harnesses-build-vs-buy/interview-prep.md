# S06 Interview Preparation — Queue Harnesses: Orchestrating at Scale, Build vs. Buy

**Course:** AI-Focused Forward Deployed Engineering · Session 06
**Audience:** Experienced software engineers, architects, engineering managers, and technical product professionals who have completed S01.
**Scenario:** Northstar Support Systems, a fictional customer with a synthetic support-ticket queue
**Competencies:** C3 Integration Engineering (primary), C4 Evaluation/Reliability/Security (primary). **Secondary:** C1 AI Engineering Fundamentals, C2 AI Solution Architecture, C6 Customer-Facing Technical Delivery.

## How to use this bank

These interviews probe whether a candidate treats idempotency and crash-safety as
**design properties of a state machine**, not features you add after the fact or trust
a framework to provide by assertion. A candidate who can trace exactly what happens to
an in-flight item when the process dies mid-step gives a categorically stronger answer
than one who says "we'd just add retries."

**Formats**
- **15-minute screen:** Q1, Q4, Q7, plus one follow-up from each.
- **30-minute technical interview:** Q2, Q5, Q8, Q9.
- **45-minute FDE design interview:** Q3, Q6, Q10, Q11, Q12.

**Rating rubric (per question)**

| Rating | Observable behavior |
|---|---|
| **0 — Missing** | Treats "add retry logic" as sufficient without addressing idempotency or crash-safety. |
| **1 — Emerging** | Names the right concepts but no concrete state machine or test for them. |
| **2 — Competent** | Designs a correct state machine and identifies the key failure modes. |
| **3 — Strong** | Adds a concrete crash-simulation test, a real framework-verification plan, and customer-facing framing of the trade-off. |

> [!NOTE]
> Single-item decision/verification mechanics (S01, S02) are assessed in their own
> sessions, not here. This bank assumes S01's harness concepts are already solid.

---

## A. 🧩 Fundamentals

### Q1. Design the state machine
**Difficulty:** Foundational · **Competency:** C3 · **Secondary:** C4

**Prompt:** You need to process a queue of items, where the process might crash and
restart at any point. What states does each item need, and what has to be true of the
transitions between them?

**Expected strong answer:**
- At minimum: pending, done, and a terminal failure/escalation state.
- The critical property: once an item reaches a terminal state, no code path can move
  it anywhere else — that's what makes "rerun the whole thing after a crash" safe
  instead of dangerous.
- State must be persisted after every item, not just at the end, or a crash loses
  everything since the last checkpoint instead of just the item in flight.

**Weak answer to probe:** "Just catch exceptions and retry" — no state model, no
persistence, no answer for what happens to already-finished work after a restart.
**Probing follow-ups:** What happens if the crash occurs right after an item finishes
but before that fact is saved to disk? What's the minimum checkpoint frequency that's
actually safe?

### Q2. Transient versus chronic failure
**Difficulty:** Foundational · **Competency:** C4 · **Secondary:** C3

**Prompt:** Distinguish a transient failure from a chronic one in a queue-processing
context, and explain why treating them the same is a mistake in both directions.

**Expected strong answer:**
- Transient: a reasonable chance retrying succeeds (timeout, momentary unavailability).
  Chronic: retrying won't fix it (a fundamentally bad request, a missing permission).
- Treating a chronic failure as transient means retrying forever, or at least wasting
  attempts and delaying the human attention it actually needs.
- Treating a transient failure as chronic means escalating things a simple retry would
  have resolved, needlessly consuming human review capacity.

**Weak answer:** "Just retry a fixed number of times for everything" — which is close
to correct mechanically (a bounded attempt budget) but misses that the *number* and
the *eventual action* should reflect which kind of failure is likely, not be one-size-
fits-all by accident.
**Probes:** How would you tell, from the error itself, which kind you're looking at? What if you can't tell?

### Q3. Why isolate each item's context
**Difficulty:** Intermediate · **Competency:** C1 · **Secondary:** C3

**Prompt:** A teammate proposes one long-running agent conversation that works through
an entire queue, item by item, in a single context. What are the actual costs of this
design?

**Expected strong answer:**
- Cost grows with every item processed, regardless of that item's own difficulty,
  because the accumulated history gets resent on every call.
- One item's malformed or confused exchange can leak into how a later item gets
  decided, since they share context — isolation failure, not just cost.
- A single shared conversation is also a single point of failure for the entire run,
  rather than confining one item's failure to itself.

**Weak answer:** "It's simpler to write one conversation than many separate calls" —
true, and exactly the trade-off being made against cost and isolation.
**Probes:** What would you expect to see in a cost graph, item index on the x-axis, if this design were running in production?

---

## B. 🧩 Design and debugging

### Q4. Design the queue harness's core loop
**Difficulty:** Intermediate · **Competency:** C3 · **Secondary:** C4

**Prompt:** Sketch the core loop that advances a queue, given a `decide_fn(item_id)`
callable and a cap on how many items to process this call.

**Expected strong answer:**
- Iterate items, skip anything not `pending`, stop once the cap is reached.
- On success: mark done, record the result. On failure: increment an attempt counter;
  if attempts remain, leave it pending; otherwise, mark it for human review.
- The loop itself should enforce (ideally via an assertion) that every item ends up in
  exactly one bucket — done, needs review, or still pending — with none lost.

**Weak answer:** Describes retry logic without ever mentioning persistence or an
explicit invariant check.
**Probes:** Where exactly does your sketch write state to disk? What happens if the process dies one line after an item is marked "done" in memory but before that save happens?

### Q5. Debug a restart-sensitive bug
**Difficulty:** Intermediate · Code/debugging · **Competency:** C4

**Prompt:**

```python
def with_fault_injection(decide_fn, fail_first):
    seen = {}

    def wrapped(item_id):
        seen[item_id] = seen.get(item_id, 0) + 1
        if item_id in fail_first and seen[item_id] == 1:
            raise TransientError("simulated failure")
        return decide_fn(item_id)

    return wrapped
```

This passes a unit test that calls `wrapped` twice in the same test function. It
produces the wrong behavior in a CLI that restarts between calls. Why?

**Expected strong answer:**
- `seen` only lives for the process's lifetime — a CLI restart creates a fresh,
  empty `seen` dict, so "has this item already failed once" is forgotten.
- The fix: base the check on the harness's own persisted attempt count (loaded from
  disk), not a separate in-memory counter that doesn't survive a restart.
- The general lesson: code that passes a test within one process can still be wrong
  across a restart boundary — these are different claims, and only a test that actually
  restarts the process (or explicitly reconstructs state the way a restart would)
  catches the second one.

**Weak answer:** "The code looks right, maybe it's a timing issue" — missing that the
bug is structural (separate, unpersisted state), not intermittent.
**Probes:** How would you write a test that actually catches this, given that a single
test function doesn't naturally restart a process?

### Q6. What telemetry proves a queue harness is healthy?
**Difficulty:** Advanced · **Competency:** C4 · **Secondary:** C3

**Prompt:** Beyond "the queue eventually empties," what would you monitor to know a
production queue harness is behaving correctly?

**Expected strong answer:**
- The done/needs-review/pending invariant, checked continuously, not just at the end of
  a run — any violation is a bug, immediately.
- The rate at which items reach needs-review versus done, watched for drift — a rising
  escalation rate might mean a chronic upstream problem, not noise.
- Attempt counts per item over time, to catch an item retrying far more than expected
  (a sign the transient/chronic distinction is misclassifying something).

**Weak answer:** "Check that the queue is empty at the end of the day" — says nothing
about whether items were lost, double-processed, or wrongly escalated along the way.
**Probes:** How would this telemetry have caught the Q8-style incident (a crash that led to 40 reprocessed, double-escalated tickets) before a customer noticed?

---

## C. 🔍 Evaluation and validation

### Q7. Verify a framework's retry claim
**Difficulty:** Advanced · Evaluation design · **Competency:** C4, C2

**Prompt:** A framework's docs say it "automatically retries failed steps and resumes
after a crash." Design a test before you trust that for a production queue.

**Expected strong answer:**
- Run a known batch, kill the process mid-run, restart, and check: was anything decided
  twice, does the final count match reality, did a chronically-failing item eventually
  stop retrying and surface to a human.
- Specifically separate "retries failed steps" (a retry guarantee) from "resumes
  correctly after a crash without reprocessing finished work" (an idempotency
  guarantee) — a framework can have one without the other.
- Treat the documentation's claim as a hypothesis to test, not a fact to build on.

**Weak answer:** "If the docs say it retries automatically, that covers it."
**Probes:** What's the minimum crash-simulation test you'd consider sufficient before putting this in front of a real customer's data?

### Q8. The benchmark-fitness trap, applied to frameworks
**Difficulty:** Intermediate · **Competency:** C2 · **Secondary:** C4

**Prompt:** What's the version of "don't trust a public benchmark over a task-specific
test" that applies to choosing an orchestration framework?

**Expected strong answer:**
- A framework's general reputation, popularity, or feature list isn't evidence it
  provides the *specific* durability guarantee your use case needs — e.g., "no item
  double-processed after a crash."
- The equivalent of a task-specific evaluation here is a crash-simulation test against
  your own actual failure modes, not trusting the framework's own marketing or docs.
- A framework that's excellent for one team's requirements can still be wrong for
  another's, if their actual idempotency needs differ.

**Weak answer:** "It's a popular, well-maintained framework, so it's probably fine."
**Probes:** What would you want to see in a framework's own test suite, if you were evaluating whether to trust its crash-recovery claims?

---

## D. 🗺️ Forward-deployed engineering scenarios

### Q9. The build-vs-buy conversation after an incident
**Difficulty:** Advanced · Customer discovery · **Competency:** C6 · **Secondary:** C2

**Prompt:** A different team's framework-based queue reprocessed and double-escalated 40
tickets after a crash. Northstar's engineering lead still wants to adopt that same
framework here, "since it's faster to build with." Respond.

**Expected strong answer:**
- Acknowledges the real speed benefit without dismissing it outright.
- Reframes the incident as evidence about that framework's *specific, unverified*
  durability behavior, not a blanket argument against frameworks.
- Proposes a concrete verification step (a crash-simulation test against the exact
  failure mode from the incident) before committing either way.

**Weak answer:** Either "never use frameworks after that" or "it's probably fine, that
was a one-off" — both skip the actual verification step.
**Probes:** What specific test result would change your recommendation in either direction?

### Q10. Investigate the double-escalation incident
**Difficulty:** Advanced · Troubleshooting · **Competency:** C4 · **Secondary:** C3

**Prompt:** You're asked to find out exactly why the framework reprocessed 40 already-
handled tickets after a crash. Walk through your investigation.

**Expected strong answer:**
- Check whether completion was persisted durably *before* the crash, or only recorded
  in memory/a delayed batch — a completed-but-not-yet-persisted item looks "never
  attempted" on restart.
- Check whether the framework's retry logic can distinguish "never attempted" from
  "finished, but the completion record didn't make it to durable storage in time."
- Separately verify the escalation side effect's own idempotency — correct status
  tracking alone doesn't prevent a retried item from re-triggering a real action, the
  same category of problem S01's `create_escalation` solved for one item.

**Weak answer:** "The framework must have a bug — switch to a different one," without
identifying the specific mechanism.
**Probes:** If the root cause turns out to be a delayed-write checkpoint, what configuration or design change would you actually ask the framework (or your own code) to make?

### Q11. When would you recommend the framework anyway?
**Difficulty:** Advanced · **Competency:** C2 · **Secondary:** C6

**Prompt:** Given the incident, under what conditions would you still recommend the
ready-made framework over hand-rolling?

**Expected strong answer:**
- If the real-world cost of an occasional double-processed item is low (not an
  irreversible or costly action), the framework's speed advantage may be worth a risk
  that's cheap to tolerate.
- If the framework's durability behavior has since been verified against a real crash
  simulation and held up, the original incident becomes evidence about a problem that's
  been fixed or configured around, not a standing objection.
- The decision should track actual verified evidence about consequence and reliability,
  not a general stance for or against ready-made tools.

**Weak answer:** "Once bitten, never use that framework again, full stop."
**Probes:** What would you need to see change about the framework (or your own integration with it) to move from "no" back to "yes"?

### Q12. Scoping the verification plan under time pressure
**Difficulty:** Advanced · **Competency:** C6 · **Secondary:** C4

**Prompt:** You have one day to decide whether to approve the framework for this
project. What's the minimum verification you'd insist on, and what would you explicitly
flag as still unverified if you had to ship a recommendation today?

**Expected strong answer:**
- Minimum: one real crash-simulation run against a realistic batch size, checking the
  no-lost-no-double-counted invariant and the escalation side effect's idempotency
  specifically — not a full audit of the framework's internals.
- Explicitly flag what one day of testing can't establish: behavior under sustained
  production load, rare failure modes that didn't occur in a single simulated crash,
  and long-term operational burden.
- A time-boxed recommendation should name its own blind spots, not imply more
  confidence than one day of testing actually supports.

**Weak answer:** Either refuses to give any recommendation without unlimited testing
time, or gives one with no stated caveats at all.
**Probes:** How would you phrase the open risk to a stakeholder who wants a simple yes/no answer today?

---

## E. ✅ Self-assessment scoring sheet

| Dimension | Questions that provide evidence | Strong-answer indicators | Score (0–3) |
|---|---|---|---|
| State machine design | Q1, Q4 | Correct states, transitions, and persistence timing | ___ |
| Failure-mode classification | Q2, Q6 | Transient vs. chronic distinguished with a concrete action for each | ___ |
| Restart-sensitive debugging | Q5, Q10 | Identifies the specific persisted-vs-in-memory-state mismatch | ___ |
| Framework-verification discipline | Q7, Q8, Q12 | Concrete crash-simulation test, not trust in documentation | ___ |
| Build-vs-buy judgment | Q9, Q11 | Evidence-based, conditional recommendation in both directions | ___ |

**Suggested interpretation:** Average ~2 indicates practical readiness for S06's learning
objectives; ~3 indicates strong practical judgment within this session's scope. These
ratings are instructional heuristics, **not calibrated hiring cutoffs**.

### ⚠️ Red flags that justify deeper probing

- Proposes "just add retries" without addressing idempotency or crash-safety at all.
- Can't explain what happens to an in-flight item if the process dies mid-step.
- Trusts a framework's documented feature claim without proposing any way to verify it.
- Treats one framework's incident as a permanent, general argument against all
  ready-made orchestration tools — or dismisses it as a one-off without investigating.
- Gives a build-vs-buy recommendation with no stated verification step or caveat.

## 🗺️ Looking back across the course

Consider: **this session's state-machine discipline (every item in exactly one state,
transitions that structurally prevent reprocessing) is the same kind of rigor S01
applied to one item's tool authorization, S02 applied to one decision's contract, S04
applied to choosing between two techniques, and S05 applied to choosing a model and its
context.** Across all of them, the pattern is the same: name the failure modes
explicitly, design the mechanism so the dangerous ones are structurally hard to trigger,
and measure — don't assume — that a shortcut (a framework, a cheap signal, a smaller
prompt) actually delivers what it claims.

---

## 🛠️ Recommended learner practice

1. Rehearse Q1 and Q9 as concise whiteboard explanations — the state machine, and the
   build-vs-buy conversation under stakeholder pressure after a real incident.
2. Run the lab's CLI with `--fail-first` and `--fail-always` on different tickets, at
   different `--cap` values, and predict each run's task list before checking it.
3. Deliberately reintroduce the Q5 bug (an unpersisted counter) into the lab's fault
   injector, rerun the CLI across two process restarts, and watch the bug actually
   happen instead of just reading its explanation.
4. Use the S06 quiz for basic retention; use this bank to probe deeper design,
   verification, and build-vs-buy judgment.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
