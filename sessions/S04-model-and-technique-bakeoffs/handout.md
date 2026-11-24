# S04 Learner Handout — Model and Technique Bake-Offs

**AI-Focused Forward Deployed Engineering · Session 04 · 90 minutes**
**Case study:** Northstar Support Systems (fictional) · Deciding which technique earns its cost
**Prerequisites:** **S01: Verified Agent Loops** and **S02: Structured Outputs and Model
Selection** — this session puts both of their techniques on the same task and measures
them, rather than teaching either mechanism from scratch.

Northstar now has two working techniques for the same ticket: a single structured call
(S02) and a verified agent loop with a lookup tool (S01). Both exist. The question this
session answers is the one neither prior session could: **for this task, is the loop
worth what it costs — and is it worth it for *every* ticket, or only some of them?**

## 🎯 What you will learn

By the end of this session, you should be able to:

1. Run the same labeled task through a single structured call and a tool-using agent loop, with every other variable held constant.
2. Measure both techniques on accuracy, cost, and latency — not accuracy alone.
3. Explain *why* an agent loop can be strictly more accurate on a task and still be the wrong default choice.
4. Design a confidence-gated **tiered dispatch**: route to the expensive technique only when a cheap signal says the cheap technique can't be trusted.
5. State, explicitly, what a tiered-dispatch recommendation still owes a customer before it ships: validation of the routing signal itself, not just the two techniques it routes between.

> [!NOTE]
> This session does not re-teach the agent loop's harness mechanics or the structured-
> output contract's validation rules — those are S01's and S02's scope. If either is
> unfamiliar, do those sessions first; they don't depend on each other, but this one
> depends on both.

## 1. 🧩 Recap: the two techniques, in one table

| | Technique 1 — single structured call (S02) | Technique 2 — verified agent loop (S01) |
|---|---|---|
| **Mechanism** | One model call, typed output contract, no tools | Model proposes, harness authorizes/executes a tool, independent verification, bounded retries |
| **Can it use new information mid-decision?** | No — only what's in the prompt | Yes — a tool call (e.g., an account lookup) can fetch what the prompt didn't include |
| **Cost shape** | One call's worth of tokens | Several calls' worth: the tool round trip, the decision, often a verification pass |
| **Where it structurally fails** | Any ticket that needs information outside the prompt | Nothing in this session's task — but it pays the multi-call cost on *every* ticket, including the ones that didn't need it |

Neither technique is "better" in the abstract. Each has a structural failure mode the
other doesn't share. That's what this session measures instead of assuming.

## 2. 🧩 Why measure instead of assume

It's tempting to reason: "the agent loop can do everything the single call can do, plus
tool use, so it should always win." That's true of *capability*. It says nothing about
*cost*, and nothing about whether a given ticket actually needed that extra capability.

A technique that structurally cannot solve part of the task will lose to one that can,
on raw accuracy, every time. That doesn't make the raw accuracy comparison the right
basis for a production recommendation — the real question is what fraction of real
traffic actually needs the capability the expensive technique adds, and whether you can
get most of its benefit without paying its full cost on every request.

> [!IMPORTANT]
> "The agent loop scored higher" and "the agent loop is the right default" are two
> different claims. The first is a measurement. The second is a cost-aware architecture
> decision that the measurement alone doesn't make for you.

## 3. 💻 One shared ticket set, two techniques

The lab builds 12 synthetic Northstar tickets, already labeled with a reference decision
(category, priority, `needs_human` — the same contract shape from S02). Six are
**self-contained**: everything needed to decide them correctly is in the ticket text.
Six need an **account lookup**: the ticket text alone is ambiguous or misleading, and the
correct decision depends on account facts the customer's wording doesn't reliably state
(a plan tier, a provisioning record, a compliance hold).

Both techniques see the exact same 12 tickets, the exact same contract, and the exact
same reference labels. Only the technique changes.

```python
class TicketDecision(BaseModel):
    category: Literal["billing", "technical", "access", "general"]
    priority: Literal["low", "medium", "high"]
    needs_human: bool
    summary: str
```

> [!TIP]
> **📎 Reminder:** this is the same contract shape S02 validated. Reusing it here isn't
> an accident — holding the output contract constant is part of what makes this
> comparison fair. See S02 §5's "Three separate questions" if you need the syntax/
> schema/semantics distinction refreshed.

## 4. 💻 Run both techniques, measure the same way

The lab's mock single-call technique answers correctly on the six self-contained
tickets — there's nothing it's missing — and is structurally wrong on the six
lookup-needed tickets, because it has no way to get the account fact it needs. The mock
agent technique calls a `lookup_account` tool (S01's pattern, generalized to a new
scenario) before every decision and gets all twelve right.

| Measurement | Technique 1 (single call) | Technique 2 (agent loop) |
|---|---:|---:|
| Correct / 12 | 6 (50%) | 12 (100%) |
| Illustrative cost per ticket | 1 call-unit | 3 call-units (lookup + decide + verify) |
| Illustrative seconds per ticket | ~1.0 s | ~3.0 s |

> [!WARNING]
> These are illustrative call-unit and second counts from this session's own mock
> harness, not a benchmark of any real provider or framework. The *shape* of the
> trade-off — more calls, more latency, for the technique that can reach more
> information — is the lesson, not the specific numbers.

Technique 2 wins on accuracy, on this task, by construction: six of the twelve tickets
are *designed* to be unsolvable without the lookup it has and the single call doesn't.
That's not a surprising result — it's the baseline the next section has to beat on cost
without losing it on accuracy.

## 5. 🧩 Tiered dispatch: pay for the loop only when you need it

Technique 2's accuracy didn't come from being generally smarter — it came from reaching
information Technique 1 structurally couldn't. If you can tell, cheaply, *which tickets
actually need that information*, you don't have to pay the agent-loop cost on the six
that don't.

**Tiered dispatch:** run the cheap technique first. If a cheap, fast signal says the
cheap technique's answer can be trusted, keep it. If that signal says it can't, escalate
to the expensive technique instead of returning the cheap answer. This is a single
confidence-gated routing decision between two techniques you already have — it does not
require a third model or a new contract.

```python
def tiered_dispatch(ticket, accounts):
    cheap = decide_single_call(ticket)
    if cheap["confident"]:
        return cheap
    return decide_with_agent(ticket, accounts)
```

In the lab's mock, a simple keyword signal ("does this ticket's wording reference
something only the account record can confirm — a plan tier, a provisioning count, an
offboarding status?") happens to flag exactly the six lookup-needed tickets and none of
the six self-contained ones. Tiered dispatch therefore matches Technique 2's 100%
accuracy while paying the 3-call-unit cost on only the six tickets that actually needed
it — roughly a third cheaper than sending every ticket through the agent loop.

> [!CAUTION]
> That clean separation is a **teaching simplification**, not a claim about real
> confidence signals. A real routing signal will sometimes be confidently wrong — it will
> wave a lookup-needed ticket through the cheap path, or escalate a ticket that didn't
> need it. The first kind of error is the dangerous one: it looks exactly like success
> until the ticket it silently mis-routed causes real harm. §7 and the lab's mini
> exercise make this concrete; never ship a routing signal whose false-negative rate you
> haven't measured on held-out data.

## 6. 🧩 This is a build-vs-cost decision, not a leaderboard

The practical sequence an FDE actually follows:

1. Measure both techniques on the real task, with real cost and latency, not just
   accuracy — same discipline S02 §5–§6 already established.
2. If the expensive technique only wins on a *subset* of cases, find out what
   distinguishes that subset — here, "does the ticket's correct answer depend on
   information outside the ticket text."
3. Design a cheap signal for that distinction, and **measure the signal itself** — not
   just "does tiered dispatch look cheaper on this trial," but "how often is the signal
   confidently wrong, and in which direction."
4. Recommend with the volume math shown, not just the percentage: a technique that's 3x
   more expensive per call is a very different decision at 50 tickets a day than at
   50,000.

## 🛠️ Forward Deployed Engineer Decision Challenge

**Customer scenario:** Northstar's VP of Support saw this session's trial numbers and
told the board "we're moving every ticket to the agent loop, it's more accurate." A
platform engineering lead is now worried about what that does to infrastructure cost and
latency at Northstar's real volume — and the tiered-dispatch signal that could avoid that
cost has only ever been tested on 12 curated tickets.

**Engineering decision:** What do you actually recommend — always-agent, always-single-
call, or tiered dispatch — with the cost math shown at real volume, and what has to be
validated about the routing signal itself before anyone trusts it in production?

**Your deliverable:** a recommendation-plus-validation-plan, ~10–15 minutes.

**Full exercise, rubric, and worked examples:**
[`docs/fde-exercises/model-technique-bakeoff-decision.md`](../../docs/fde-exercises/model-technique-bakeoff-decision.md)

## 7. 🔍 Common pitfalls

> [!WARNING]
> Watch for these five claims — each sounds reasonable and each is wrong.

- **"The agent loop is strictly better, so always use it."** It's strictly more capable
  on this task; capability and cost-justified default are different claims.
- **"A confidence signal that looks clean on 12 tickets is production-ready."** It's
  validated on 12 curated tickets. Its false-negative rate on real traffic is unmeasured.
- **"A confident-but-wrong routing decision is the same risk as a cautious-but-right
  one."** It isn't — a false "this is fine, keep the cheap answer" silently ships a wrong
  decision; a false escalation only costs extra money.
- **"Tiered dispatch means you never need the expensive technique's full accuracy
  story."** You still need Technique 2 to actually be correct on everything it's asked
  to handle — tiered dispatch changes *how often* you pay for it, not whether it works.
- **"Lower aggregate cost always means the right trade-off."** Not if the cases the cheap
  path gets wrong are the customer's highest-severity ones — reuse S02's critical-miss-
  rate discipline here, not just a blended cost number.

## ✅ Check your understanding

1. Technique 2 scores 100% and Technique 1 scores 50% on the same 12 tickets. Does that alone tell you which one to deploy? Why or why not?
2. What specifically does tiered dispatch change — accuracy, cost, or both — relative to always using Technique 2?
3. Why is a false "stay on the cheap path" routing error more dangerous than a false "escalate to the expensive path" one?
4. What piece of this session's lab result is a genuine finding, and what piece is a teaching simplification you should not generalize from?
5. At what point does the cost difference between always-single-call and always-agent stop being a rounding error and start being a real infrastructure decision?

<details>
<summary>Suggested answers</summary>

1. No. It tells you Technique 2 is more capable on this task's full range of tickets. It
   doesn't tell you what fraction of real traffic needs that extra capability, or what
   the cost difference is at real volume — both of which matter for the deployment
   decision.
2. Both, but asymmetrically: accuracy can match Technique 2's (if the routing signal is
   reliable), while cost drops because only the tickets that need the expensive
   technique actually pay for it.
3. A false "stay cheap" error returns a wrong decision that looks exactly like a correct
   one — nothing downstream flags it. A false "escalate" error just spends extra money on
   a ticket that didn't need it; the ticket still gets decided correctly.
4. Genuine finding: an agent loop with a lookup tool can resolve tickets a single call
   structurally cannot, at a measurable cost premium. Teaching simplification: the
   confidence heuristic's perfect separation on these 12 tickets — a real signal needs
   its own held-out validation.
5. Roughly, whenever ticket volume is high enough that the per-ticket cost delta,
   multiplied by volume, becomes a line item someone has to budget for — which is
   exactly the kind of volume-scaled math the decision challenge above asks you to do.

</details>

## 📚 Further reading

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — workflow-versus-agent trade-offs, including when added autonomy isn't worth its cost.
- This course's **S01: Verified Agent Loops** §2–§5 — the harness/verification mechanics this session's "Technique 2" assumes.
- This course's **S02: Structured Outputs and Model Selection** §5–§6 — the measurement discipline (critical-miss rate, fair comparison) this session reuses rather than re-derives.

---

> [!TIP]
> **Expected takeaways:** a more capable technique is not automatically the right
> default; the right default depends on what fraction of real traffic needs that
> capability and what a cheap, *validated* signal can tell you about which fraction that
> is. A clean trial result on a curated set is a hypothesis about that signal, not proof
> of it.

## 🗺️ What you have built, and what's next

**What you have built:** a shared, labeled Northstar ticket set run through both prior
sessions' techniques under identical conditions; a measured accuracy/cost/latency
comparison; and a working confidence-gated tiered dispatch between them.

**What limitations remain:** the routing signal's clean 12-ticket separation is a
teaching simplification — a real deployment needs the signal's own false-negative rate
measured on held-out, representative traffic before it's trusted. Neither technique's
underlying accuracy was re-validated at a larger scale here; that's still S02's
unresolved sample-size caveat, carried forward.

**What later sessions add:** **S05: Open-Weight, Local Models, and Token Economics in
Practice** extends this same measurement discipline to *which model* runs each
technique — including options that live outside a hosted API entirely. **S06: Queue
Harnesses: Orchestrating at Scale, Build vs. Buy** extends Technique 2 itself from
deciding one ticket to orchestrating an entire queue of them. Neither depends on this
session to be read first, but both build on the measurement habits practiced here.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
