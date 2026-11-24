# FDE Decision Exercise — Model and Technique Bake-Offs

**Targets session:** S04 — Model and Technique Bake-Offs
**Run after:** the lab's Part 5 (tiered dispatch) numbers are on the screen — before the
learner has time to just trust the clean 100%-accuracy, 33%-cheaper result and move on.
**Timebox:** 10–15 minutes. **Artifact:** a recommendation-plus-validation-plan.

---

## 1. Customer situation

Northstar's VP of Support watched this session's trial: the agent-loop technique hit
100% against the single call's 50%, and tiered dispatch matched that 100% at roughly a
third less cost than running the agent loop on every ticket. The VP has already told the
board "we're moving every ticket to the agent loop — it's clearly more accurate." A
platform engineering lead has quietly flagged that at Northstar's documented volume of
50,000 tickets a day (the same figure from S03's decision exercise), tripling the
per-ticket cost is not a rounding error — and that the tiered-dispatch routing signal
that could avoid most of that cost has only ever been tested on the lab's 12 curated
tickets, never on real traffic.

## 2. Customer stakeholders

**The VP of Support** — under board pressure, focused on the accuracy number, not yet
thinking about infrastructure cost or the routing signal's reliability.
**A Platform Engineering lead** — owns the infrastructure budget and the on-call burden,
worried about both the 3x cost and an unvalidated routing decision shipping silently
wrong answers.

## 3. Business objective

Keep as much of the proven accuracy improvement as possible, without committing to its
full cost at real volume, and without presenting an unvalidated routing heuristic to the
board as if it were already proven in production.

## 4. Available information

- The 12-ticket trial numbers: single call 50% accurate at 1 cost-unit/ticket; agent
  loop 100% accurate at 3 cost-units/ticket; tiered dispatch 100% accurate at 1.4
  cost-units/ticket (assuming the routing signal is perfect).
- Northstar's documented volume: 50,000 tickets/day (from S03).
- The routing signal's design: a keyword heuristic that happened to cleanly separate all
  12 trial tickets.

## 5. Missing information and reasonable assumptions

- No measurement yet of what fraction of **real** Northstar traffic actually needs the
  account lookup — assume you don't know if it's closer to 5% or 60%, and that the
  trial's 50/50 split is not guaranteed to match it.
- No measurement yet of the routing signal's false-negative rate (tickets it wrongly
  keeps on the cheap path) on anything other than the 12 curated tickets it was designed
  against.
- No agreed cost ceiling yet from Platform Engineering — assume you'll need to propose
  one, framed in terms they can actually approve or reject, not just present a percentage.

## 6. Technical decision required

1. **A recommendation** — always single call, always agent loop, or tiered dispatch —
   with the cost math shown at Northstar's real volume, not just the trial's percentage.
2. **A validation plan for the routing signal specifically**, targeting its
   false-negative rate (the direction that silently ships a wrong decision), separate
   from validating either technique's own accuracy.
3. **An explicit fallback statement**: what happens, operationally, when the signal is
   later found to be wrong on a real ticket.

## 7. Expected learner artifact

A short recommendation-plus-validation-plan, in four parts:

- **Recommendation with volume math** — the approach you recommend, with daily cost at
  50,000 tickets/day for at least the recommended approach and one alternative.
- **Validation plan** — one concrete test targeting the signal's false-negative rate,
  run on representative/held-out traffic, not the original 12 tickets.
- **Fallback statement** — one or two sentences on what happens operationally when a
  misroute is found.
- **One caveat** — what this recommendation does not yet establish.

## 8. Evaluation rubric

| Criterion | What a passing answer shows | Points |
|---|---|---:|
| Recommendation is volume-scaled, not percentage-only | Shows actual daily cost-unit totals at 50,000 tickets/day, not just "33% cheaper" | 3 |
| Recommendation doesn't just agree with the VP | Engages with the real cost-at-volume consequence of "always agent," rather than deferring to the stakeholder's stated preference | 2 |
| Validation plan targets false negatives specifically | Names a held-out or shadow-sampling test aimed at the dangerous failure direction, not overall routing accuracy | 3 |
| Validation plan uses representative/larger data | Explicitly rejects the original 12-ticket trial as sufficient evidence | 2 |
| Fallback statement is concrete | States what happens operationally (e.g., escalation path, audit sampling), not just "we'll fix it if it happens" | 3 |
| Caveat is specific | Names a real open unknown (e.g., real lookup-needed rate, signal false-negative rate), not a generic disclaimer | 2 |
| **Total** | | **15** |

## 9. Instructor guidance

- **Timing:** 3 minutes to read the situation and the two stakeholders' positions, 8
  minutes to draft the four-part artifact, 3–4 minutes to compare recommendations across
  pairs/groups — expect real variation in the recommended approach, which is the point.
- **The teaching hook:** make explicit that the VP's instinct ("it's more accurate, use
  it everywhere") is exactly the capability-vs-default conflation this session's §2 and
  §7 warn about — this exercise is that warning, applied under stakeholder pressure
  instead of read as a bullet point.
- **Watch for:** learners who recommend tiered dispatch and treat the exercise as
  finished without a validation plan — the routing signal, not either technique, is the
  actual unproven part of that recommendation; learners who recommend "always agent" out
  of caution without doing the volume math that would show whether that caution is
  actually affordable; learners who propose a validation plan that just repeats the
  original 12-ticket trial with a few more items, missing that it needs to be
  representative, held-out, and targeted at false negatives specifically.
- **A reasonable canonical answer**, if you want one to anchor discussion: recommend
  tiered dispatch, with daily cost shown at an assumed-conservative 30% real
  lookup-needed rate (cost ≈ 0.7×1 + 0.3×3 = 1.6 units/ticket, ≈ 80,000 units/day, versus
  150,000 for always-agent); validation plan = shadow-sample a random 5% of
  "confident" decisions through the agent loop for the first month and report the
  disagreement rate before trusting the signal unsupervised; fallback = any shadow-
  sampled disagreement routes to a human reviewer, not just a logged warning.

## 10. Example of a strong answer

> **Recommendation:** Tiered dispatch, not always-agent. At our trial's 20%-lookup-needed
> rate, tiered dispatch costs ≈70,000 cost-units/day versus 150,000 for always-agent —
> roughly half the infrastructure cost for the same measured accuracy, *if* the routing
> signal holds up. If real traffic turns out closer to 50% lookup-needed, tiered
> dispatch still costs ≈100,000/day versus 150,000 — still a meaningful saving, just a
> smaller one. Either way, it beats committing to the full 150,000/day figure the VP is
> currently proposing, without giving up the accuracy win entirely.
>
> **Validation plan:** Before trusting the signal unsupervised, shadow-sample 5% of
> tickets it marks "confident" through the agent loop as well, blind to the signal's
> decision, for the first two weeks of real traffic. Report the disagreement rate
> specifically — not overall routing accuracy — since a disagreement here is a candidate
> false negative, the dangerous direction.
>
> **Fallback:** Any shadow-sampled disagreement during the validation window routes to a
> human reviewer and gets logged as a signal-improvement case, not silently resolved
> either way.
>
> **Caveat:** We don't yet know the real lookup-needed rate in Northstar's actual
> traffic — the 20% figure is this trial's assumption, not a measurement. The cost
> numbers above should be revisited once we have two weeks of real routing data.

**Why it works:** the recommendation shows its cost math at real volume and under a
sensitivity check (what if the rate is 50%, not 20%), rather than quoting the trial's
percentage as if it were final; the validation plan targets the specific dangerous
failure direction on representative data, not the original curated trial; the fallback
is operational and concrete, not a vague promise to "monitor it."

## 11. Example of an inadequate answer, and why it fails

> "The agent loop got 100% so let's use tiered dispatch since it's basically as good and
> cheaper. The routing logic worked great on our 12 tickets so it should be fine. If
> something goes wrong we'll catch it and fix the heuristic."

**Why it fails:**
- No volume math at all — "cheaper" is asserted, not shown at Northstar's actual
  50,000-ticket/day scale, which is exactly the number the VP and Platform Engineering
  need to make a real budget decision.
- Treats the 12-ticket trial's clean separation as sufficient evidence for production,
  exactly the small-sample-as-proof mistake this session (and S02 before it) explicitly
  warns against.
- "We'll catch it and fix it" is not a validation plan — it has no held-out test, no
  target failure direction, and no concrete fallback for what happens to the specific
  ticket that gets silently misrouted in the meantime.
