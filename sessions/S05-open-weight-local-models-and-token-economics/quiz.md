# S05 Learner Quiz — Open-Weight, Local Models, and Token Economics in Practice

**AI-Focused Forward Deployed Engineering · Session 05**
**Scenario:** Northstar Support Systems (fictional); synthetic support-ticket triage
**Prerequisites:** S02: Structured Outputs and Model Selection, S03: LLM Fundamentals

## Purpose and administration

This assessment checks whether you can separate accuracy effects (which weights) from
cost/latency/memory effects (where they run), measure real token savings from context
trimming, explain *why* trimming can improve accuracy rather than just cost, and treat a
hard data-handling constraint as something that rules out candidates before cost is even
discussed.

- **Suggested time:** 25–35 minutes, answering each question before opening its answer.
- **Total:** 56 points, 10 questions. Partial credit is permitted where specified.
- **Primary competencies:** C2 (AI Solution Architecture), C5 (Deployment & Operations). **Secondary:** C1 (AI Engineering Fundamentals), C4 (Evaluation, Reliability, Security), C6 (Customer-Facing Technical Delivery).
- **Assumptions:** All Northstar tickets and knowledge-base text are synthetic. Cost and latency figures are illustrative units from this session's own mock, not real provider pricing or hardware benchmarks. Agent-loop mechanics (S01) and technique comparison (S04) are **not** in scope here.
- **How to take it:** Answer each question yourself before expanding its **Answer** section.

---

## Section 1 — Concepts (Q1–Q3)

### Q1. What open-weight actually controls (2 points)
**Difficulty:** Foundational · **Competency:** C2 · **Type:** Multiple choice

A model being open-weight rather than closed-weight primarily determines:

A. How accurate the model is on a given task.
B. Where you are allowed to deploy it, including entirely on your own infrastructure.
C. Whether the model costs anything at all to run.
D. Whether the model supports a typed output contract.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** B (2 points)

**Explanation:** Open-weight versus closed-weight is a licensing/deployment fact, not a
capability fact. An open-weight model can be run anywhere you have the hardware,
including fully on-premises; a closed-weight model can only be called through its
provider's API.

**Misconception:** "Open" implies either "better" or "free" — it implies neither.

</details>

### Q2. Same weights, different place (4 points)
**Difficulty:** Foundational · **Competency:** C5 · **Type:** Short answer

The same open-weight model is run once through a hosted provider and once locally. List
**two** things that should change between the runs, and **one** thing that should not.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Two changes, one constant (4 points)

**Should change (2 points, 1 each):** marginal cost per call (near zero locally versus
a provider's per-token rate), latency/throughput characteristics (no network hop
locally, but bounded by local hardware — often slower without a GPU), and/or memory
footprint (the model has to fit in local RAM/VRAM, which is nobody's problem on a hosted
call). Any two count.

**Should not change (2 points):** accuracy — it's the same weights, so a real accuracy
difference between the two runs is evidence of a bug (quantization, version mismatch,
serving-stack difference), not a deployment-location effect.

**Misconception:** Deployment location is itself a capability lever.

</details>

### Q3. Why measure, not estimate (4 points)
**Difficulty:** Intermediate · **Competency:** C1, C5 · **Type:** Short answer

A teammate estimates token savings from trimming a prompt by eyeballing word count
instead of running a tokenizer. What's the risk, specifically?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Word count is not token count (4 points)

Tokenization is model/tokenizer-specific and doesn't map 1:1 to words — punctuation, word
fragments, and formatting can all change the token count independent of word count
(S03 §1) (2). An eyeballed word-count estimate can be meaningfully off from the actual
billed/latent token count, which is what cost and context-window limits are actually
measured in, not words (2).

**Misconception:** "Fewer words" and "fewer tokens" are the same claim.

</details>

## Section 2 — Measurement and trimming design (Q4–Q7)

### Q4. Volume-scaled token savings (6 points)
**Difficulty:** Intermediate · **Competency:** C5, C1 · **Type:** Numerical interpretation

This session's lab measured full context at ~354.5 tokens/ticket and trimmed context at
~170.5 tokens/ticket, on the open-weight hosted configuration's $2-per-1,000-token
illustrative rate. At Northstar's documented volume of 50,000 tickets/day, compute daily
tokens and daily cost for full versus trimmed context.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** (6 points)

| Context | Daily tokens | Daily cost (illustrative units) |
|---|---:|---:|
| Full | 354.5 × 50,000 ≈ 17,725,000 | 17,725 × 2 ≈ 35,450 |
| Trimmed | 170.5 × 50,000 ≈ 8,525,000 | 8,525 × 2 ≈ 17,050 |

Daily savings ≈ 18,400 units, roughly **52%** — consistent with trimming removing
roughly half the context's tokens (3 for correct token totals, 3 for correct cost
totals and the savings figure).

**Misconception:** Per-ticket savings and volume-scaled savings are the same kind of
number — the per-ticket percentage is right, but only the volume-scaled total tells you
whether it's worth engineering effort to capture.

</details>

### Q5. Debug the trimming logic (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Debugging

A teammate wrote:

```python
def build_context(ticket, sections, general_rules):
    return general_rules + sections[ticket["topic_hint"]] + sections["technical"]
```

intending to send only the general rules plus the one relevant section. What's wrong,
and what does it cost?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** The technical section is always appended (6 points)

Regardless of `topic_hint`, the function unconditionally appends `sections["technical"]`
as well — for any ticket whose hint isn't `"technical"`, this silently sends two
sections instead of one, partially defeating the token/cost savings trimming exists to
provide (3). It also reintroduces exactly the context-dilution risk trimming was meant
to avoid, since an unrelated section's wording is back in context for every
non-technical ticket (3).

**Misconception:** A trimming function is correct as long as it includes the *right*
section — it also has to exclude every section it doesn't name.

</details>

### Q6. Why trimming fixed an error, not just a cost (6 points)
**Difficulty:** Intermediate · **Competency:** C4, C1 · **Type:** Failure analysis

Explain the specific mechanism by which the lab's trimmed context produced *higher*
accuracy than full context on the same ticket set, not just lower cost.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Removing the distracting section removes the distraction (6 points)

One ticket's text happened to contain a word ("401") that also appeared, in an unrelated
rule, inside a different category's knowledge-base section. With full context, that
section's text was present and a less capable model's keyword-sensitive behavior matched
on it, producing the wrong category (3). With trimmed context, that unrelated section
was never included for this ticket's topic hint, so the distracting text was never in
the prompt and the error couldn't occur (3) — the fix worked by removing the *source* of
the error, not by making the model work harder on the same material.

**Misconception:** Context size and accuracy trade off in one fixed direction (more
context, lower accuracy, always) — the real mechanism is relevance, not size; irrelevant
material is what caused the error, and removing exactly that material is what fixed it.

</details>

### Q7. Validate the topic hint (6 points)
**Difficulty:** Advanced · **Competency:** C4 · **Type:** Eval design

Context trimming in this lab assumed the customer-provided topic hint always matches the
correct category. Design one concrete test you'd run before trusting that assumption in
production.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Measure the hint's real disagreement rate (6 points)

On a representative, held-out sample of real tickets, compare the customer-provided
topic hint against the final, human-confirmed category, and measure how often they
disagree (3). For any disagreement, check whether trimming to the (wrong) hinted section
caused a wrong decision that the full-context version would have gotten right — that's
the real production risk trimming introduces, not just an abstract "the hint might be
wrong" concern (3).

**Misconception:** Because the topic hint is "free," it's automatically safe to trust
without checking how often it's actually right.

</details>

## Section 3 — FDE decisions (Q8–Q10)

### Q8. The data residency conversation (8 points)
**Difficulty:** Advanced · **Competency:** C6, C2 · **Type:** Customer communication

A regulated-industry prospect requires that ticket text never leave their own
infrastructure. Their trial used the closed, hosted configuration, which scored best on
accuracy. Write a **3–5 sentence** response to the account team, who are asking whether
this deal is still possible with "the good model."

<details>
<summary><strong>Answer</strong></summary>

**Example response (8 points):**

> "The data residency requirement rules out the closed model entirely — it can only be
> called through its provider's API, so there's no configuration of it that keeps ticket
> text on the customer's own infrastructure. We'd need to run the open-weight model
> locally instead, which is the same weights we already tested, just not the one that
> scored highest. That configuration matched the closed model on 8 of our 10 trial
> tickets and missed the one requiring cross-referencing two data sources — I'd want the
> customer to know that specific limitation up front, not discover it after signing."

**Rubric:** correctly rules out the closed model as a constraint, not a cost comparison
(2); identifies open-weight local as what's actually left to choose from (2); states the
real accuracy trade-off being accepted, with the specific limitation named (2); frank,
customer-facing tone with no overpromising (2).

**Common weak response:** "We'll just use the good model and keep the data secure some
other way" — ignoring that the requirement is architectural, not a security add-on you
can bolt onto a hosted API call.

</details>

### Q9. When local deployment isn't worth it (6 points)
**Difficulty:** Advanced · **Competency:** C2 · **Secondary:** C5

Under what conditions would you recommend *against* local deployment, even for a
customer who says they'd prefer it?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Two defensible conditions (6 points, 3 each)

If there is no actual hard data-residency requirement — just a stated preference — the
added latency, memory/hardware burden, and operational overhead of running and
maintaining a local deployment may not be worth it relative to a hosted option at a
similar accuracy. If the customer's volume or hardware budget can't support the memory
and throughput a local deployment needs at their real traffic, a hosted open-weight
configuration may be the only practical option regardless of stated preference.

**Misconception:** "Local" is categorically the safer or more sophisticated choice, so a
customer's preference for it should be accommodated by default.

</details>

### Q10. Hosted and local disagree in production (8 points)
**Difficulty:** Advanced · **Competency:** C4, C5 · **Type:** Troubleshooting

Three weeks after launch, someone notices the hosted and local deployments of what's
supposed to be the same open-weight model are producing different categories on the same
replayed tickets at a measurable rate. Describe your investigation.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Treat this as a configuration bug, not model variance (8 points)

First, confirm it actually is the same model version and the same quantization/precision
on both sides — a common real cause of this exact symptom is the local deployment
running a quantized variant while the hosted one doesn't, which is a genuine capability
difference disguised as a deployment-location one (3). Second, confirm both sides are
receiving the identical prompt/context — a serving-stack or client library difference
that silently alters formatting, truncation, or default parameters between the two paths
is another common cause (3). Only after ruling out both would "the same weights can
disagree due to non-determinism" be a reasonable conclusion, and even then the rate
should be small and worth quantifying, not shrugged off (2).

**Misconception:** Deployment location can legitimately explain an accuracy difference
on its own — per §2 of the handout, it shouldn't, and a real difference is evidence of a
specific, findable configuration mismatch.

</details>

---

## Submission checklist

- [ ] I separated accuracy effects (open vs. closed weight) from cost/latency/memory effects (hosted vs. local).
- [ ] I computed token and cost savings at real volume, not just as a per-ticket percentage.
- [ ] I explained the context-dilution mechanism, not just stated that trimming helped.
- [ ] I treated data residency as ruling out candidates, not as one more factor to weigh against cost.
- [ ] I investigated a hosted/local accuracy mismatch as a likely configuration bug, not as expected variance.

## Scoring overview

| Q | Difficulty | Competency | Format | Points |
|---|---|---|---|---:|
| 1 | Foundational | C2 | MCQ | 2 |
| 2 | Foundational | C5 | Short answer | 4 |
| 3 | Intermediate | C1, C5 | Short answer | 4 |
| 4 | Intermediate | C5, C1 | Numerical interpretation | 6 |
| 5 | Intermediate | C4 | Debugging | 6 |
| 6 | Intermediate | C4, C1 | Failure analysis | 6 |
| 7 | Advanced | C4 | Eval design | 6 |
| 8 | Advanced | C6, C2 | Customer communication | 8 |
| 9 | Advanced | C2 | Architecture | 6 |
| 10 | Advanced | C4, C5 | Troubleshooting | 8 |
| **Total** | | | | **56** |

## 🔍 Interpret your results

**Suggested self-assessment ranges (not certification thresholds):** 47–56 strong; 37–46
developing; 0–36 revisit relevant concepts. These are not empirically validated cut
scores.

**Diagnose by concept:**
- Q1, Q2, Q3: the open/closed and hosted/local distinctions themselves.
- Q4, Q5: real-token measurement and correct trimming implementation.
- Q6, Q7: the context-dilution mechanism and validating the hint that drives it.
- Q8, Q9: data residency and deployment-location architecture judgment.
- Q10: diagnosing an unexpected accuracy difference correctly.

**Coverage note:** This quiz assesses model/deployment selection and context-trimming
measurement — it does not re-test S02's contract validation or S04's technique-dispatch
mechanics.

> [!NOTE]
> Numerical results in Q4 come from this session's own lab notebook (a real tokenizer
> run on this lab's own knowledge-base text), not from any real provider's pricing or
> hardware benchmark.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
