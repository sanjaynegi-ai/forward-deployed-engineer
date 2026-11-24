# S04 Interview Preparation — Model and Technique Bake-Offs

**Course:** AI-Focused Forward Deployed Engineering · Session 04
**Audience:** Experienced software engineers, architects, engineering managers, and technical product professionals who have completed S01 and S02.
**Scenario:** Northstar Support Systems, a fictional customer with synthetic support tickets
**Competencies:** C2 AI Solution Architecture (primary), C4 Evaluation/Reliability/Security (primary). **Secondary:** C1 AI Engineering Fundamentals, C5 Deployment & Operations, C6 Customer-Facing Technical Delivery.

## How to use this bank

These interviews probe whether a candidate treats "more accurate" and "the right
production choice" as the same claim — and if not, what they actually check before
separating them. Strong answers quantify cost at real volume and name a concrete
validation step for any routing/dispatch logic, not just the two techniques it chooses
between.

**Formats**
- **15-minute screen:** Q1, Q4, Q7, plus one follow-up from each.
- **30-minute technical interview:** Q2, Q5, Q8, Q9.
- **45-minute FDE design interview:** Q3, Q6, Q10, Q11, Q12.

**Rating rubric (per question)**

| Rating | Observable behavior |
|---|---|
| **0 — Missing** | Treats accuracy alone as sufficient for a deployment decision. |
| **1 — Emerging** | Mentions cost or latency, but no concrete measurement or validation plan. |
| **2 — Competent** | Gives a workable comparison/dispatch design and names its main limitation. |
| **3 — Strong** | Adds volume-scaled cost math, a concrete signal-validation test, and customer-facing framing. |

> [!NOTE]
> Harness authorization internals (S01) and output-contract validation (S02) are
> assessed in their own sessions, not here. This bank assumes both are already solid.

---

## A. 🧩 Fundamentals

### Q1. Does a capability win settle a deployment decision?
**Difficulty:** Foundational · **Competency:** C2 · **Secondary:** C4

**Prompt:** An agent loop scores 100% and a single call scores 50% on the same labeled
set. A stakeholder says, "Done — we're switching everything to the agent." Respond.

**Expected strong answer:**
- The result shows a *capability* difference on this task, not a *cost-justified
  default*.
- Before recommending, you need: what fraction of real traffic needs the capability the
  expensive technique adds, what it costs at real volume, and whether a cheaper
  blended approach (tiered dispatch) captures most of the accuracy gain.
- The techniques' structural failure modes differ — one can't reach outside information,
  the other pays a multi-call cost on everything, including tickets that didn't need it.

**Weak answer to probe:** "More accurate, ship it," with no cost or volume discussion.
**Probing follow-ups:** What changes about your answer if real traffic is 2% lookup-needed versus 60%? What's the cost shape difference between the two techniques, mechanically?

### Q2. Why does the agent loop cost more, mechanically?
**Difficulty:** Foundational · **Competency:** C1 · **Secondary:** C5

**Prompt:** Explain the cost difference between a single structured call and a verified
agent loop in terms of what actually executes, not "it's more complex."

**Expected strong answer:**
- Single call: one model call's tokens, once, per item.
- Agent loop: at minimum, a model call to decide on a tool, a tool round trip, another
  model call to produce the final decision, often a verification pass — multiple
  billable/latent steps per item, by mechanism, not by model choice.
- This cost shape holds even if the agent loop uses a cheaper model than the single
  call does.

**Weak answer:** "Agents just cost more because they're fancier."
**Probes:** Would a cheaper model change this comparison's conclusion? What happens to this math if the agent makes two tool calls instead of one on a hard ticket?

### Q3. What must stay constant in this kind of comparison?
**Difficulty:** Intermediate · **Competency:** C4 · **Secondary:** C2

**Prompt:** You're comparing a single-call technique against an agent-loop technique on
the same task. What has to be held constant for the comparison to mean anything?

**Expected strong answer:**
- Same tickets, same reference labels, same output contract, same scoring rule.
- Only the technique (and, separately, only the model) varies at a time — changing both
  at once confounds which one caused a result.
- Record exact configuration, date, and settings for each run — this is S02's fair-
  comparison discipline, reused rather than re-derived.

**Weak answer:** "Just run both and see which number is bigger."
**Probes:** What would you say to a teammate who changed the prompt for only one technique mid-comparison because it "wasn't being fair to that one"?

---

## B. 🧩 Design and debugging

### Q4. Design a tiered dispatch
**Difficulty:** Intermediate · **Competency:** C2 · **Secondary:** C4

**Prompt:** You have a cheap technique and an expensive, more capable one. Design a
dispatch mechanism that uses the expensive one only when needed.

**Expected strong answer:**
- Run the cheap technique first; use a fast, cheap signal (not a second expensive call)
  to decide whether its answer can be trusted.
- If trusted, return it; if not, escalate to the expensive technique and return *that*
  answer — the expensive technique must not run unconditionally regardless of the
  signal, or the cost savings disappear.
- The signal itself needs its own validation, independent of validating either
  technique — see Q7.

**Weak answer:** Describes running both techniques every time and picking "whichever
seems right," which is strictly more expensive than always using the expensive one.
**Probes:** What would unconditionally calling both techniques before checking the
signal do to your cost savings?

### Q5. Debug this dispatch function
**Difficulty:** Intermediate · Code/debugging · **Competency:** C4

**Prompt:**

```python
def tiered_dispatch(ticket, accounts):
    cheap = decide_single_call(ticket)
    expensive = decide_with_agent(ticket, accounts)
    if cheap["confident"]:
        return cheap
    return expensive
```

What's wrong, and what does it cost in production?

**Expected strong answer:**
- `decide_with_agent` executes unconditionally, before the confidence check — every
  ticket pays the expensive technique's cost regardless of which answer is returned.
- The function still *looks* correct (it returns the right answer), which makes this an
  easy bug to miss in code review — cost regressions like this one don't show up as a
  wrong output, only as a bigger bill.
- Fix: move the expensive call inside the `else` branch.

**Weak answer:** "It returns the right thing, so it's fine."
**Probes:** How would you catch this kind of bug before it reaches production — in a code review, or with a cost-per-ticket metric that would have flagged it?

### Q6. What do you log for a production dispatch system?
**Difficulty:** Advanced · **Competency:** C5 · **Secondary:** C4

**Prompt:** Design the minimum telemetry you'd want from a tiered-dispatch system
running in production, beyond the final decision itself.

**Expected strong answer:**
- Per ticket: which path was taken, the confidence signal's raw value, cost and latency
  actually incurred, and (where feasible) the shadow-sampled comparison result from Q7's
  validation design.
- Aggregate: the real observed lookup-needed rate in traffic (it may drift from the
  rate measured at launch), and the signal's false-negative rate specifically, not just
  overall routing accuracy.
- Enough to recompute the volume-scaled cost math from real traffic, not just the
  original trial.

**Weak answer:** "Just log the final decision — that's what the customer cares about."
**Probes:** How would you notice, from telemetry alone, that the real lookup-needed rate had drifted from 20% to 50% since launch?

---

## C. 🔍 Evaluation and validation

### Q7. Validate the signal, not the techniques
**Difficulty:** Advanced · Evaluation design · **Competency:** C4

**Prompt:** Your routing signal cleanly separates a 12-ticket trial set. What do you do
before trusting it in production?

**Expected strong answer:**
- Shadow-sample: route a blind, random subset of "confident" tickets through the
  expensive technique anyway, and compare — any disagreement is a candidate false
  negative.
- Measure that rate on representative, larger, held-out traffic, not the original
  curated trial.
- Distinguish the two failure directions (Q8 below) and weight validation toward the
  dangerous one.

**Weak answer:** "Re-run the same 12 tickets a few more times."
**Probes:** How large a held-out sample would you want before setting a production threshold? What would make you distrust a signal that still looks clean at that scale?

### Q8. Which routing failure is worse?
**Difficulty:** Intermediate · **Competency:** C4 · **Secondary:** C2

**Prompt:** A routing signal can falsely keep a lookup-needed ticket on the cheap path,
or falsely escalate a self-contained ticket to the expensive path. Which is worse?

**Expected strong answer:**
- Falsely staying cheap returns a wrong decision indistinguishable from a correct one —
  nothing downstream catches it, since the signal itself was the thing that should have.
- Falsely escalating only costs extra call-units; the ticket is still decided correctly.
- A validation plan should weight toward catching the first kind, even if it's rarer.

**Weak answer:** "Both are just accuracy loss on the routing step."
**Probes:** How would a false "stay cheap" error actually surface in production, if it surfaces at all?

### Q9. Benchmark fitness versus task fitness, one level up
**Difficulty:** Intermediate · **Competency:** C2 · **Secondary:** C4

**Prompt:** S02 warned against trusting a public benchmark over a task-specific
comparison. What's the equivalent trap in *this* session's material?

**Expected strong answer:**
- Trusting this session's own 12-ticket trial numbers — or the clean routing-signal
  separation — as if they were production evidence, the same category of mistake as
  trusting a public leaderboard over a task-specific test.
- The trial establishes a *mechanism* (tiered dispatch can work) and a *method*
  (how to measure it), not a validated production number.
- Representative, larger, held-out evaluation is still owed before any of these numbers
  back a real recommendation.

**Weak answer:** "This session's numbers are from our own course material, so they're
more trustworthy than a public benchmark."
**Probes:** What would you tell a stakeholder who quoted this session's exact 33%-cheaper figure as Northstar's actual expected savings?

---

## D. 🗺️ Forward-deployed engineering scenarios

### Q10. The VP wants to switch everything to the agent loop
**Difficulty:** Advanced · Customer discovery · **Competency:** C6 · **Secondary:** C2, C5

**Prompt:** Northstar's VP of Support saw the trial and wants every ticket moved to the
agent loop immediately, citing the accuracy number. What do you say in the next five
minutes of that conversation?

**Expected strong answer:**
- Acknowledge the real accuracy win, then immediately reframe to cost-at-volume: what
  does tripling the cost on every ticket mean at Northstar's real traffic, including the
  majority that didn't need the capability driving the accuracy gain.
- Propose tiered dispatch as the way to keep most of the accuracy win without the full
  cost, with an explicit caveat that the routing signal needs validation before launch.
- Ask for (or propose collecting) the real lookup-needed rate in production traffic —
  the trial's 50/50 split is not guaranteed to match it.

**Weak answer:** Agrees immediately, or argues purely on engineering elegance without
addressing the VP's actual accuracy concern.
**Probes:** What number would you want in hand before this conversation, that you don't have yet? What if the VP asks "how do we know the cheap path is really cheap enough to matter"?

### Q11. A silent misroute reaches production
**Difficulty:** Advanced · Troubleshooting · **Competency:** C4 · **Secondary:** C6

**Prompt:** A compliance-hold access ticket was silently auto-answered via the cheap
path and no human ever saw it. Walk through your response.

**Expected strong answer:**
- Blast radius first: search for other tickets matching the same pattern that may have
  been silently misrouted the same way, before anything else.
- Treat this as a real, confirmed false negative — use it as a concrete new test case
  for the signal, rather than just raising a threshold with no evidence of what it
  should be.
- Communicate transparently to the customer what happened and what's changing, and run
  the shadow-sampling validation (Q7) that should have preceded launch.

**Weak answer:** Fixes the one ticket and moves on without checking for others, or
immediately disables tiered dispatch entirely without first understanding the specific
failure.
**Probes:** How would you distinguish "this signal needs a better feature" from "this
signal needed held-out validation it never got"?

### Q12. When is building tiered dispatch not worth it?
**Difficulty:** Advanced · **Competency:** C2 · **Secondary:** C5

**Prompt:** Under what conditions would you recommend *against* building tiered
dispatch, even with a clear accuracy gap between techniques?

**Expected strong answer:**
- If almost all real traffic needs the expensive technique's capability, the cheap path
  captures little volume — the engineering and validation cost of the dispatch logic
  may exceed what it saves.
- If total volume is low enough that the cost delta is immaterial to the budget, "always
  use the more capable technique" is a simpler, equally defensible recommendation.
- The decision should follow measured traffic composition and volume, not a general
  preference for more sophisticated architecture.

**Weak answer:** "Tiered dispatch is always worth building because it's strictly
cheaper for equal accuracy."
**Probes:** What would you need to measure, in the first week of a new deployment, before recommending tiered dispatch versus a simpler always-one-technique approach?

---

## E. ✅ Self-assessment scoring sheet

| Dimension | Questions that provide evidence | Strong-answer indicators | Score (0–3) |
|---|---|---|---|
| Capability vs. cost-justified default | Q1, Q2, Q9 | Separates measured capability from deployment recommendation | ___ |
| Dispatch design and implementation correctness | Q4, Q5 | Correct conditional execution; names the easy-to-miss cost bug | ___ |
| Signal validation discipline | Q7, Q8, Q11 | Concrete held-out test targeting false negatives specifically | ___ |
| Volume-scaled cost reasoning | Q2, Q6, Q10 | Real numbers at real volume, not percentages alone | ___ |
| Customer-facing architecture judgment | Q10, Q11, Q12 | Requirements and traffic data first, defensible trade-offs | ___ |

**Suggested interpretation:** Average ~2 indicates practical readiness for S04's learning
objectives; ~3 indicates strong practical judgment within this session's scope. These
ratings are instructional heuristics, **not calibrated hiring cutoffs**.

### ⚠️ Red flags that justify deeper probing

- Treats a measured capability gap as a finished deployment decision.
- Proposes a dispatch design without separately validating the routing signal itself.
- Doesn't distinguish the two directions a routing signal can fail, or treats them as
  equally costly.
- Quotes this session's own trial numbers (or any small curated trial) as production
  evidence.
- Recommends the more sophisticated architecture by default, without checking whether
  real traffic composition justifies it.

## 🗺️ Bridge to later sessions

Consider: **"The lookup tool solved this task's hard tickets. What if Northstar needed to
run this same decision process, at scale, on a model hosted on its own infrastructure
instead of a provider's API — because a customer's data can't leave their premises?"**

That's a model-and-deployment question, not a technique question — **S05: Open-Weight,
Local Models, and Token Economics in Practice** extends this same measurement
discipline to open-weight and local models. **S06: Queue Harnesses: Orchestrating at
Scale, Build vs. Buy** extends the agent-loop technique itself from deciding one ticket
to orchestrating an entire queue of them. Neither depends on this session being read
first, but both build on the comparison habits practiced here.

---

## 🛠️ Recommended learner practice

1. Rehearse Q1 and Q10 as concise whiteboard explanations — capability versus
   cost-justified default, under real stakeholder pressure.
2. Run the lab's mini exercise (a 13th ticket designed to fool the confidence
   heuristic) and narrate, out loud, which failure direction it demonstrates.
3. Redo Q4's volume math with a different assumed lookup-needed rate (5%, 50%) and
   notice how much the recommendation changes.
4. Use the S04 quiz for basic retention; use this bank to probe deeper architectural and
   validation judgment.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
