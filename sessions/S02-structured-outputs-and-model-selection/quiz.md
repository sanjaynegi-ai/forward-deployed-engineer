# S02 Learner Quiz — Structured Outputs and Choosing a Model

**AI-Focused Forward Deployed Engineering · Session 02 of 7**
**Scenario:** Northstar Support Systems (fictional); synthetic support-ticket triage

## Purpose and administration

This assessment checks whether experienced software professionals can distinguish a
model, a model-serving API, and an application; reason about tokens, context, and
provider-specific cost behavior; design and validate typed response contracts; run a fair
small-scale model comparison; and communicate quality/latency/cost trade-offs to a
customer.

- **Recommended use:** 30–40 minutes independently after class; can be assigned as homework.
- **Total:** 74 points, 15 questions. Partial credit is permitted where specified.
- **Primary competencies:** C1 (AI Engineering Fundamentals), C4 (Evaluation, Reliability, Security). **Secondary:** C2 (AI Solution Architecture), C3 (Integration Engineering), C5 (Deployment & Operations), C6 (Customer-Facing Technical Delivery).
- **Assumptions:** All Northstar support tickets are synthetic. Do not assume that model-generated explanations are faithful internal reasoning traces. Agent execution loops and harness implementation are **not** in scope here — see S01.
- **How to take it:** Answer Part A before opening the solutions in Part B. For code questions, explain the behavior; you do not need API credentials or a live model.

---

# Part A — Assessment

## Section 1 — Concepts (Q1–Q5)

### Q1. Responsibilities (2 points)
**Difficulty:** Foundational · **Competency:** C1, C4 · **Type:** Multiple choice

A customer ticket is assigned `priority="low"` even though the customer's agreed rubric
requires `"high"`. The result is valid JSON and passes schema validation. Which component
is responsible for ensuring the business error is detected?

A. The tokenizer
B. The model-serving API, because it returned valid JSON
C. The application's task evaluation and business validation layer
D. Pydantic, because it validates the response

**Answer:** ______

### Q2. Distinguish the layers (4 points)
**Difficulty:** Foundational · **Competency:** C1, C2 · **Type:** Matching

Match each responsibility to the most appropriate layer: **LLM**, **model-serving
API/gateway**, or **Northstar application**.

| Responsibility | Layer |
|---|---|
| a. Generate a candidate category and priority from supplied context | |
| b. Authenticate model API requests and report provider usage | |
| c. Enforce the customer's escalation policy | |
| d. Decide what the end user sees after a failed model call | |

### Q3. Context window (4 points)
**Difficulty:** Foundational · **Competency:** C1, C2 · **Type:** Short answer

A developer says: "Our model has a large context window, so we should attach every
knowledge-base article to every ticket." Identify **two engineering concerns** with this
proposal, even if the request fits within the model's supported limit.

**Response:**

### Q4. Reasoning effort (2 points)
**Difficulty:** Intermediate · **Competency:** C1, C2 · **Type:** Multiple choice

Configuration B uses higher reasoning effort than Configuration A. Which claim is
justified **without task-specific test results**?

A. B is always more correct.
B. B always costs exactly twice as much.
C. B may change quality, latency, or cost; the trade-off must be measured.
D. B removes the need for a validation schema.

**Answer:** ______

### Q5. Prompt caching (4 points)
**Difficulty:** Intermediate · **Competency:** C1, C5 · **Type:** Short answer

Two consecutive requests include the same 1,500-token instructions followed by different
support tickets. Why **might** the second call cost less, and what evidence would you need
before claiming the saving occurred?

**Response:**

---

## Section 2 — Code and contracts (Q6–Q9)

### Q6. Predict the output (4 points)
**Difficulty:** Foundational · **Competency:** C1, C4 · **Type:** Code interpretation

Assume `pydantic>=2` is installed:

```python
from typing import Literal
from pydantic import BaseModel, Field

class TicketDecision(BaseModel):
    category: Literal["billing", "technical", "access", "other"]
    priority: Literal["low", "medium", "high"]
    needs_human: bool
    summary: str = Field(min_length=1)

record = {
    "category": "access",
    "priority": "urgent",
    "needs_human": True,
    "summary": "SSO sign-in fails"
}

result = TicketDecision.model_validate(record)
print(result.priority)
```

What happens? Explain why this is *not* evidence that the model made the wrong business
decision.

**Response:**

### Q7. Debug the metric (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Debugging

A teammate wrote:

```python
def accuracy(predictions, labels):
    valid = [p for p in predictions if p is not None]
    correct = sum(p["category"] == y["category"]
                  for p, y in zip(valid, labels))
    return correct / len(valid)
```

The model returned `None` for the second ticket. Identify **two distinct defects** and
explain how they distort reporting. You may provide corrected pseudocode.

**Response:**

### Q8. Structural versus semantic correctness (4 points)
**Difficulty:** Intermediate · **Competency:** C1, C4 · **Type:** Applied validation

The schema accepts:

```json
{
  "category": "billing",
  "priority": "low",
  "needs_human": false,
  "summary": "Customer cannot sign in during a critical rollout"
}
```

Give one **schema-level test** and one **semantic/business-level test** that should be
applied. Why must the tests remain separate?

**Response:**

### Q9. Design a better contract (6 points)
**Difficulty:** Intermediate · **Competency:** C1, C3 · **Type:** Code writing

Northstar needs the category, priority, and an escalation flag. Write a Pydantic v2 model with:

- `category` restricted to `billing`, `technical`, `access`, or `other`;
- `priority` restricted to `low`, `medium`, or `high`;
- `needs_human` as a boolean;
- a nonempty `summary` no longer than 240 characters.

Then show **one invalid object** that the model should reject. Do **not** claim this
contract proves the classification is correct.

```python
# Your implementation:
```

---

## Section 3 — Measurement and FDE decisions (Q10–Q15)

### Q10. Calculate quality (6 points)
**Difficulty:** Intermediate · **Competency:** C2, C4 · **Type:** Numerical interpretation

In a **10-ticket synthetic pilot**, two model configurations produce these results. All 10
tickets have agreed reference labels.

| Metric | Configuration A | Configuration B |
|---|---:|---:|
| Attempts | 10 | 10 |
| Schema-valid outputs | 10 | 9 |
| Correct **category and priority** | 8 | 8 |
| Critical `high → low` priority errors | 1 | 0 |
| Total API cost | $0.02 | $0.05 |
| Median request latency | 1.1 s | 1.8 s |

Calculate each configuration's **end-to-end task agreement** (correct/attempted) and
**schema success rate** (schema-valid/attempted). Which configuration would you recommend
*if the customer has zero tolerance for high-to-low misses in this pilot*? State one
qualification.

**Response:**

### Q11. Fair comparison (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Multiple select (choose all that apply)

Which practices make a comparison of two model configurations more defensible?

- [ ] A. Evaluate on the same tickets and reference labels.
- [ ] B. Change the prompt and schema for each model until one wins, then compare raw scores as if the setup were controlled.
- [ ] C. Record exact model/version, settings, date, and scoring rules.
- [ ] D. Exclude refusals and invalid responses from the denominator.
- [ ] E. Analyze consequential errors separately from aggregate accuracy.
- [ ] F. Use only the public benchmark's top-ranked model, without task evaluation.

### Q12. Small sample risk (6 points)
**Difficulty:** Advanced · **Competency:** C4 · **Type:** Eval design

A model scores 9/10 on the workshop tickets. Your stakeholder says, "Great — it's 90%
accurate in production." Explain why that conclusion does not follow. Suggest **two
improvements** to the evaluation plan.

**Response:**

### Q13. Find the failure mode (6 points)
**Difficulty:** Intermediate · **Competency:** C4, C2 · **Type:** Failure analysis

Configuration A produces a schema-valid response for every call, but it repeatedly
classifies urgent access failures as `low` priority. Configuration B sometimes fails to
return usable output, but its valid outputs classify urgent tickets correctly.

How would you report these two failure modes separately, and how should the application
behave on unusable output?

**Response:**

### Q14. Customer-facing recommendation (8 points)
**Difficulty:** Advanced · **Competency:** C6, C2 · **Type:** Customer communication

Northstar wants faster triage while avoiding missed urgent cases. Write a **3–5 sentence
recommendation** to a non-ML stakeholder that:

1. States what was actually measured.
2. Acknowledges that the sample is small.
3. Gives a next-step recommendation without claiming production readiness.
4. Mentions at least one quality-versus-latency/cost trade-off.

**Response:**

### Q15. When to stop at a workflow (6 points)
**Difficulty:** Advanced · **Competency:** C2 · **Type:** Architecture

The current Northstar feature reads a support ticket and returns a typed category/priority
decision. All steps are predetermined, and no new tool or action is chosen by the model. A
teammate proposes replacing it immediately with a multi-tool autonomous agent.

Would you accept the proposal? Explain what evidence or changing requirements would
justify moving to an agent — and point to where that mechanism is actually taught in this
course. (This is a forward-looking architecture question.)

**Response:**

---

## Submission checklist

- [ ] I distinguished schema validity from decision correctness.
- [ ] I counted failures against the attempted-call denominator.
- [ ] I identified a consequence-sensitive metric, not just overall agreement.
- [ ] I justified architectural/model choices using customer requirements.
- [ ] I explicitly labeled what the small synthetic pilot cannot establish.

The solutions are included below for self-assessment. Finish Part A before continuing.

---

# Part B — Solutions and explanations

> [!WARNING]
> Complete Part A before reading further.

## Scoring overview

| Q | Difficulty | Competency | Format | Points |
|---|---|---|---|---:|
| 1 | Foundational | C1, C4 | MCQ | 2 |
| 2 | Foundational | C1, C2 | Matching | 4 |
| 3 | Foundational | C1, C2 | Short answer | 4 |
| 4 | Intermediate | C1, C2 | MCQ | 2 |
| 5 | Intermediate | C1, C5 | Short answer | 4 |
| 6 | Foundational | C1, C4 | Code interpretation | 4 |
| 7 | Intermediate | C4 | Debugging | 6 |
| 8 | Intermediate | C1, C4 | Applied validation | 4 |
| 9 | Intermediate | C1, C3 | Code writing | 6 |
| 10 | Intermediate | C2, C4 | Numerical interpretation | 6 |
| 11 | Intermediate | C4 | Multiple select | 6 |
| 12 | Advanced | C4 | Eval design | 6 |
| 13 | Intermediate | C4, C2 | Failure analysis | 6 |
| 14 | Advanced | C6, C2 | Customer communication | 8 |
| 15 | Advanced | C2 | Architecture | 6 |
| **Total** | | | | **74** |

**Scoring:** Award partial credit on open responses for technically correct reasoning. For
Q11, award 2 points for each correct selection, with 0 for the question if any incorrect
option is selected (or adjust the policy consistently before class).

### Q1 — C (2 points)
**Explanation:** The application or its evaluation/business-validation components must
detect incorrect prioritization against the agreed rubric. Schema validation checks shape
and allowed values, not task correctness.
**Misconception:** "Valid JSON means a valid business result."

### Q2 — a: LLM; b: model-serving API/gateway; c: Northstar application; d: Northstar application (4 points)
**Explanation:** The model produces candidate values; the service exposes model inference
and may meter use; the application owns domain rules and user-facing error paths. Some
platform responsibilities vary by provider, but this separation is a sound architectural
starting point.
**Misconception:** Treating model, provider endpoint, and end-user product as the same component.

### Q3 — Two concerns, 2 points each (4 points)
**Strong answer examples:** Increased input cost and latency; irrelevant context burying
useful information; access-control/data-exposure risks; truncation or remaining
output-budget constraints; harder provenance and debugging. Reward any two distinct
well-explained issues.
**Misconception:** "Fits in the context window" implies the material is relevant or safe to include.

### Q4 — C (2 points)
**Explanation:** Effort is model/provider-specific and must be compared empirically on the
task. Higher effort does not guarantee a better classification.
**Misconception:** Reasoning effort works like a monotonic accuracy knob.

### Q5 — Provider-specific prompt caching (4 points)
**Expected:** The repeated eligible prefix may be reused, reducing billable/reported input
processing (2 points); verify provider documentation, actual caching eligibility/usage
metrics, and invoices or usage reports for those calls (2 points). Do not promise a fixed
discount or universal automatic caching.
**Misconception:** Any repeated words always receive a cache discount.

### Q6 — ValidationError, no `print` (4 points)
`"urgent"` is outside `Literal["low", "medium", "high"]`.
`TicketDecision.model_validate(record)` raises `pydantic.ValidationError` before `print`
executes (2 points). This proves a contract violation, not semantic misclassification; the
intended business priority could still be high, and that needs separate evidence (2
points).
**Misconception:** A schema error itself proves whether the customer would have been triaged correctly.

### Q7 — Two separate bugs (6 points)
1. **Denominator bias:** Filtering out `None` treats failed attempts as if they never
   happened, exaggerating end-to-end success (3 points).
2. **Alignment corruption:** `zip(valid, labels)` pairs later predictions with earlier
   labels after a missing item, yielding invalid comparisons (3 points).

**Better pattern:** Preserve one result slot per ticket, ideally keyed by stable ticket ID;
score `None` as unsuccessful and report schema success separately.

```python
def end_to_end_agreement(predictions, labels):
    if len(predictions) != len(labels):
        raise ValueError("One result slot required per attempted ticket")
    if not labels:
        return None
    correct = sum(
        p is not None
        and p.get("category") == y["category"]
        and p.get("priority") == y["priority"]
        for p, y in zip(predictions, labels)
    )
    return correct / len(labels)
```

**Misconception:** Removing invalid outputs is harmless data cleaning.

### Q8 — Two tests and their distinction (4 points)
**Schema-level:** Parse against allowed category/priority, boolean `needs_human`, and
nonempty bounded summary (2 points). **Semantic/business-level:** Compare priority and
category with an approved ticket rubric or reviewed label, perhaps requiring human
escalation for critical account-access incidents (2 points). Schema validity is necessary
for integration but insufficient for correctness.
**Misconception:** Semantic rules can be fully enforced with generic JSON Schema types.

### Q9 — Example implementation (6 points)

```python
from typing import Literal
from pydantic import BaseModel, Field

class TicketDecision(BaseModel):
    category: Literal["billing", "technical", "access", "other"]
    priority: Literal["low", "medium", "high"]
    needs_human: bool
    summary: str = Field(min_length=1, max_length=240)

invalid = {
    "category": "access",
    "priority": "urgent",   # not an allowed value
    "needs_human": True,
    "summary": "SSO blocked",
}
```

**Rubric:** correct constrained category and priority (2); boolean field (1); bounded
nonempty summary (2); valid invalid-case demonstration and correct explanation (1).
`model_validate` or equivalent is fine. A candidate may choose `extra="forbid"` as an
enhancement; not required.
**Misconception:** Pydantic automatically verifies the ticket decision against the original incident.

### Q10 — Both agreement 80%; schema success 100% and 90% (6 points)
- **A:** agreement 8/10 = **80%**; schema success 10/10 = **100%**.
- **B:** agreement 8/10 = **80%**; schema success 9/10 = **90%**.
- Under the stated **zero-tolerance pilot criterion**, **B is the only configuration
  without the observed critical high→low miss**, but it is not production-ready and its
  unusable output needs a fallback/escalation path. On 10 tickets, neither model
  establishes a meaningful production risk guarantee.

**Rubric:** agreement calculations (2); schema calculations (2); conditional
recommendation and limitation (2).
**Misconception:** Equal overall accuracy means equivalent business risk, or 0 observed misses means 0 future misses.

### Q11 — A, C, E (6 points)
**Explanation:** Control the task and rubric, record configuration details, and examine
consequential errors. B confounds experimental variables; D causes survivorship bias; F
mistakes general benchmarking for task validity.
**Misconception:** A top public benchmark ranking substitutes for held-out customer-task evaluation.

### Q12 — Inference too broad (6 points)
**Expected:** A 10-example synthetic sample is not representative and has huge
uncertainty; the observed 9/10 is sample agreement, not demonstrated production accuracy
(2). Improvements (2 each): larger representative labeled set; distinct development and
held-out test sets; repeated runs; stratification by difficulty, type, and critical cases;
subject-matter review of labels; clear treatment of failures and uncertainty. Any two
thoughtful improvements count.
**Misconception:** A point estimate with a small denominator proves performance for all customers.

### Q13 — Two failure channels plus fallback (6 points)
**Expected:** Report **schema/response availability** (valid response rate,
error/refusal/incomplete rate) separately from **semantic quality** (reference agreement
and high→low miss rate) (4). Fail closed or route to a human/known deterministic fallback
when output is unusable; don't silently assign a safe-looking default priority (2).
**Misconception:** An invalid output and a valid-but-harmful priority are identical kinds of failure.

### Q14 — Example stakeholder response (8 points)

> "We compared two configurations on the same small set of synthetic support tickets and
> measured agreement with reviewed priorities, critical misses, response latency, and API
> cost. Those results are useful for an initial shortlist but are not representative
> enough to establish production accuracy. I recommend retaining the option that avoids
> observed urgent-to-low misclassifications while adding a manual fallback for unusable
> outputs, then testing a larger customer-reviewed holdout set. It may be slower or more
> expensive per ticket, so we should confirm your acceptable response time and error
> thresholds before selecting it."

**Rubric:** grounded measurements (2); sample limitation (2); concrete next step (2); clear
trade-off and stakeholder-oriented tone (2).
**Common weak response:** "Model B is 100% safe and should be deployed immediately."

### Q15 — No immediate agent justification (6 points)
**Expected:** Retain the simpler deterministic workflow when all steps are fixed and
single-call typed classification satisfies the requirements (3). Consider an agent later
if the ticket genuinely requires **model-directed selection among tools/actions**,
iterative investigation, and evidence that such flexibility improves task outcomes enough
to justify higher latency, expense, operational complexity, and control requirements — the
mechanics for that are covered in **S01: Verified Agent Loops** (3).
**Misconception:** The presence of an LLM, tools, or a business process automatically implies agent architecture.

---

## 🔍 Interpret your results

**Suggested bands (formative, not certification thresholds):** 63–74 strong; 50–62
developing; 0–49 revisit relevant concepts. These are proposed instructional thresholds,
not empirically validated cut scores.

**Diagnose by concept:**
- Q1, Q2, Q6: layer boundaries and terminology.
- Q4, Q5, Q11: operations/cost judgment and fair comparisons.
- Q8, Q9: contract design and implementation.
- Q7, Q10, Q12: evaluation rigor and small-sample risk.
- Q13, Q14, Q15: customer-facing architecture decisions.

> [!TIP]
> **Recommended debrief:** Ask "Which metric would your customer reject even when overall
> agreement looks strong?" and "Where is the authorization and fallback logic actually
> implemented?" Invite one learner to defend keeping the fixed workflow instead of adding
> an agent.

**Coverage note:** This quiz assesses model/application separation, structured-output
contracts, and task-first model comparison — not production-grade orchestration or
statistically robust evaluation design; those remain later-course topics. Tool dispatch,
loop semantics, and harness boundaries are assessed in **S01**, not here.

> [!NOTE]
> Numerical results in Q10 are fictional exercise data, not observations from a real
> provider or validated model. The snippets in Q7 and Q9 are illustrative.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
