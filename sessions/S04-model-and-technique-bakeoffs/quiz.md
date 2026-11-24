# S04 Learner Quiz — Model and Technique Bake-Offs

**AI-Focused Forward Deployed Engineering · Session 04**
**Scenario:** Northstar Support Systems (fictional); synthetic support-ticket triage
**Prerequisites:** S01: Verified Agent Loops, S02: Structured Outputs and Model Selection

## Purpose and administration

This assessment checks whether you can measure a single structured call against a
verified agent loop on the same task, reason about cost and latency alongside accuracy,
design and critique a confidence-gated tiered dispatch, and communicate a volume-scaled
recommendation to a customer.

- **Suggested time:** 25–35 minutes, answering each question before opening its answer.
- **Total:** 56 points, 10 questions. Partial credit is permitted where specified.
- **Primary competencies:** C2 (AI Solution Architecture), C4 (Evaluation, Reliability, Security). **Secondary:** C1 (AI Engineering Fundamentals), C5 (Deployment & Operations), C6 (Customer-Facing Technical Delivery).
- **Assumptions:** All Northstar tickets and accounts are synthetic. Cost and latency figures are illustrative call-unit counts from this session's own mock, not real provider pricing. Tool-authorization mechanics (S01) and contract validation (S02) are **not** re-tested here.
- **How to take it:** Answer each question yourself before expanding its **Answer**
  section.

---

## Section 1 — Concepts (Q1–Q3)

### Q1. Capability versus default (2 points)
**Difficulty:** Foundational · **Competency:** C2 · **Type:** Multiple choice

An agent loop with a lookup tool scores 100% on a labeled set; a single structured call
scores 50% on the same set. Which conclusion is justified by that result alone?

A. The agent loop should become the production default for this task.
B. The agent loop is more capable on this task's full range of cases; whether it should be the default is a separate, cost-aware decision.
C. The single call's contract must be broken, since it scored lower.
D. The two techniques are not comparable because one uses a tool.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** B (2 points)

**Explanation:** The accuracy gap shows a capability difference on this specific task. It
says nothing about cost, latency, or what fraction of real traffic needs that capability
— all required before "more accurate" becomes "the right default."

**Misconception:** A capability win on a labeled set is automatically a deployment
decision.

</details>

### Q2. Where the cost actually comes from (4 points)
**Difficulty:** Foundational · **Competency:** C1, C5 · **Type:** Short answer

Explain, in your own words, *why* the agent-loop technique costs more per ticket than
the single-call technique, in terms of what actually happens at the model/tool level —
not just "it's more complex."

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Multiple model/tool round trips per ticket (4 points)

The single call technique spends one model call's worth of tokens per ticket. The agent
loop technique spends at least one model call to decide whether/what to look up, one
tool round trip to execute the lookup and return an observation, and typically another
model call (and a verification pass) to produce the final decision — each of those is
billable/latent, so the cost and latency scale with the number of round trips, not with
how "smart" the technique is.

**Misconception:** Cost differences between techniques are about model choice, not about
how many calls the technique's mechanism requires per item.

</details>

### Q3. Why measure cost and latency, not just accuracy (4 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Short answer

A teammate says: "We already know which technique is more accurate — that settles it."
Give **two** reasons this doesn't settle a production recommendation.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Two reasons, 2 points each (4 points)

**Strong answer examples:** Cost and latency differences, multiplied by real traffic
volume, can be a budget-breaking or SLA-breaking decision even when accuracy is higher;
the accuracy gap may be driven by a minority subset of traffic, meaning most tickets
don't need the expensive technique at all; the comparison was run on a small, curated
set, so the accuracy gap itself may not generalize; a cheaper alternative (tiered
dispatch) might capture most of the accuracy gain without the full cost. Any two
distinct, well-explained reasons earn full credit.

**Misconception:** "More accurate" and "correct production choice" are the same claim.

</details>

## Section 2 — Measurement and dispatch design (Q4–Q7)

### Q4. Volume-scaled cost math (6 points)
**Difficulty:** Intermediate · **Competency:** C4, C5 · **Type:** Numerical interpretation

A larger, representative holdout (not the 12-ticket trial) found that **20% of real
Northstar tickets** actually need the account lookup; the other 80% are self-contained.
Using this session's illustrative call-unit costs (single call = 1 unit, agent loop = 3
units) and assuming a **perfect** routing signal for tiered dispatch, fill in daily cost
at Northstar's documented volume of **50,000 tickets/day** (from S03) for each approach,
and the number of tickets each gets wrong:

| Approach | Cost per ticket (units) | Daily cost (units) | Tickets wrong per day |
|---|---:|---:|---:|
| Always single call | | | |
| Always agent loop | | | |
| Tiered dispatch (perfect signal) | | | |

<details>
<summary><strong>Answer</strong></summary>

**Answer:** (6 points)

| Approach | Cost per ticket | Daily cost | Tickets wrong per day |
|---|---:|---:|---:|
| Always single call | 1 unit | 50,000 | 10,000 (the 20% needing lookup) |
| Always agent loop | 3 units | 150,000 | 0 |
| Tiered dispatch | 0.8×1 + 0.2×3 = 1.4 units | 70,000 | 0 (signal assumed perfect) |

**Rubric:** correct per-ticket cost for each row (3, 1 each); correct daily totals (2);
correct wrong-ticket counts (1).

**Misconception:** Tiered dispatch's cost advantage over always-agent is fixed — it
actually scales with how rare the lookup-needed subset is in real traffic, which must be
measured, not assumed to match the 12-ticket trial's 50/50 split.

</details>

### Q5. Debug the dispatch function (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Debugging

A teammate wrote:

```python
def tiered_dispatch(ticket, accounts):
    cheap = decide_single_call(ticket)
    expensive = decide_with_agent(ticket, accounts)
    if cheap["confident"]:
        return cheap
    return expensive
```

Identify the defect and explain its practical consequence at production volume.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Both techniques always run (6 points)

`decide_with_agent` is called unconditionally, before the confidence check, so every
ticket pays the expensive technique's cost regardless of the routing decision — tiered
dispatch's entire cost advantage is silently discarded while still returning the right-
looking answer (3). The fix is to call `decide_with_agent` only inside the `else`
branch, so the expensive path only executes when the cheap path is actually not
confident (3).

**Misconception:** A tiered dispatch function is correct as long as it *returns* the
right technique's answer — but if it also *executes* the technique it didn't choose,
the cost savings it exists to provide never materialize.

</details>

### Q6. Which routing error is worse (6 points)
**Difficulty:** Intermediate · **Competency:** C4, C2 · **Type:** Failure analysis

A routing signal can fail in two directions: it can mark a lookup-needed ticket
"confident" (wrongly staying on the cheap path), or mark a self-contained ticket "not
confident" (wrongly escalating to the expensive path). Which direction is more dangerous,
and why? What does the *other* direction cost you?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** False "stay cheap" is the dangerous direction (6 points)

A false "confident" on a ticket that actually needed the lookup returns a wrong decision
that looks exactly like a correct one — nothing downstream flags it, since the signal
itself was what should have caught it (3). The other direction — wrongly escalating a
self-contained ticket — only costs the extra call-units of the expensive technique; the
ticket still gets decided correctly, just at higher cost (3).

**Misconception:** Both directions of a routing signal's error are an equal "accuracy
loss" — they aren't; one hides a wrong answer and the other merely overspends.

</details>

### Q7. Validate the signal, not just the techniques (6 points)
**Difficulty:** Advanced · **Competency:** C4 · **Type:** Eval design

The lab's confidence heuristic cleanly separates all 12 trial tickets. Design one concrete
test you would run **before** trusting this signal in production, specifically targeting
its false-negative rate (Q6's dangerous direction).

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Shadow-sample the "confident" path (6 points)

Route a small, random, blind sample of tickets the signal marks "confident" through the
expensive technique anyway, without telling the signal or short-circuiting on its
answer, and compare the two outputs (3). Any disagreement on that sample is a candidate
false negative — measure its rate on a representative volume of real (or realistically
varied) traffic, not the original 12 curated tickets, before setting a production
confidence threshold (3). Accept partial credit for other concrete held-out validation
designs that specifically target false negatives rather than overall accuracy.

**Misconception:** Re-running the same 12-ticket trial with a slightly larger N counts as
validating the signal.

</details>

## Section 3 — FDE decisions (Q8–Q10)

### Q8. The volume-scaled recommendation (8 points)
**Difficulty:** Advanced · **Competency:** C6, C5 · **Type:** Customer communication

Using Q4's numbers, write a **3–5 sentence recommendation** to Northstar's VP of Support,
who currently wants to move every ticket to the agent loop because "it's more accurate."

<details>
<summary><strong>Answer</strong></summary>

**Example stakeholder response (8 points):**

> "The agent loop is genuinely more accurate on this task, but moving every ticket to it
> would roughly triple our daily AI infrastructure cost, even though most tickets don't
> need the account lookup that's driving the accuracy gain. I recommend a tiered design
> that only escalates tickets our data shows actually need it, which gets us most of the
> accuracy improvement at a fraction of the added cost. Before we rely on that routing
> decision in production, we need to measure how often it wrongly keeps a ticket on the
> cheap path when it shouldn't — that's the failure mode that would hide a wrong decision
> rather than just costing us more."

**Rubric:** names the real trade-off, not just "agent is better" (2); gives the
volume-scaled cost consequence (2); recommends tiered dispatch as the resolution (2);
explicitly flags the signal-validation caveat (2).

**Common weak response:** "The agent loop is more accurate, so let's just use it
everywhere — we can afford it."

</details>

### Q9. When tiered dispatch isn't worth building (6 points)
**Difficulty:** Advanced · **Competency:** C2 · **Type:** Architecture

Under what real-traffic conditions would you recommend **against** building tiered
dispatch at all, even though the agent loop measurably outperforms the single call?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Two defensible conditions (6 points, 3 each)

If nearly all real traffic needs the lookup (the "cheap path" subset is tiny), the
routing logic adds engineering and operational complexity for little cost saving over
simply always using the agent loop. If the volume is low enough that the cost
difference between always-agent and tiered dispatch is immaterial to the budget, the
added complexity and the signal-validation burden may not be worth it either — "always
agent" is a legitimate, simpler recommendation in that case.

**Misconception:** A more sophisticated architecture is always the more defensible
recommendation.

</details>

### Q10. A silent misroute reaches production (8 points)
**Difficulty:** Advanced · **Competency:** C4, C6 · **Type:** Troubleshooting

Three months after launch, a customer escalates: a compliance-hold access-restoration
ticket was auto-answered by the cheap path as a routine, low-priority request and no
human ever saw it. Describe your investigation and remediation plan.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Blast-radius-first investigation (8 points)

First, establish blast radius: search recent "confident" decisions for the same
ticket-text pattern (plan/account-history references like this one) to see whether this
was a one-off or systematic, and whether any other tickets were silently misrouted the
same way (3). Second, do not simply raise the confidence threshold without evidence —
determine specifically what signal would have caught this case, using the real
(now-confirmed) false negative as a new, concrete test case (3). Third, communicate to
the customer and to Northstar what happened, what's being checked, and what changes
before the signal is trusted again — treating this as the shadow-sampling validation
(Q7) that should have run before launch, not as a one-off bug (2).

**Misconception:** Fixing the one ticket that surfaced is the same as fixing the signal
that let it through.

</details>

---

## Submission checklist

- [ ] I treated an accuracy win as a capability finding, not a deployment decision by itself.
- [ ] I computed cost at real volume, not just on the trial set.
- [ ] I distinguished the two directions a routing signal can fail, and named which is more dangerous.
- [ ] I designed a validation test that specifically targets false negatives, not overall accuracy.
- [ ] I gave a customer-facing recommendation with a volume-scaled number, not just a percentage.

## Scoring overview

| Q | Difficulty | Competency | Format | Points |
|---|---|---|---|---:|
| 1 | Foundational | C2 | MCQ | 2 |
| 2 | Foundational | C1, C5 | Short answer | 4 |
| 3 | Intermediate | C4 | Short answer | 4 |
| 4 | Intermediate | C4, C5 | Numerical interpretation | 6 |
| 5 | Intermediate | C4 | Debugging | 6 |
| 6 | Intermediate | C4, C2 | Failure analysis | 6 |
| 7 | Advanced | C4 | Eval design | 6 |
| 8 | Advanced | C6, C5 | Customer communication | 8 |
| 9 | Advanced | C2 | Architecture | 6 |
| 10 | Advanced | C4, C6 | Troubleshooting | 8 |
| **Total** | | | | **56** |

## 🔍 Interpret your results

**Suggested self-assessment ranges (not certification thresholds):** 47–56 strong; 37–46
developing; 0–36 revisit relevant concepts. These are not empirically validated cut
scores.

**Diagnose by concept:**
- Q1, Q2, Q3: capability versus cost-justified-default reasoning.
- Q4, Q8: volume-scaled cost math and communicating it.
- Q5: implementation correctness of the dispatch mechanism itself.
- Q6, Q7, Q10: the routing signal's own failure modes and how to validate against them.
- Q9: recognizing when the more sophisticated architecture is *not* the right call.

**Coverage note:** This quiz assesses the comparison and dispatch-design layer built on
top of S01 and S02 — it does not re-test harness authorization (S01) or contract
validation (S02) mechanics.

> [!NOTE]
> Numerical results in Q4 are fictional exercise data built on this session's own mock
> lab, not observations from a real provider or production system.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
