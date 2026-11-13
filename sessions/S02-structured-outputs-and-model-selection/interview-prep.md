# S02 Interview Preparation — Structured Outputs and Choosing a Model

**Course:** AI-Focused Forward Deployed Engineering · Session 02
**Audience:** Experienced software engineers, QA automation engineers, architects, engineering managers, and technical product professionals. Python and ML proficiency are not assumed.
**Scenario:** Northstar Support Systems, a fictional customer with synthetic support tickets
**Competencies:** C1 AI Engineering Fundamentals (primary), C4 Evaluation/Reliability/Security (primary), C2 AI Solution Architecture (secondary). C3/C5/C6 are touched through integration, cost, and customer-delivery scenarios.

## How to use this bank

These are engineering interviews, not vocabulary tests. Strong answers use precise
boundaries, falsifiable claims, an executable evaluation plan, and awareness of failure
modes.

**Formats**
- **15-minute screen:** Q1, Q4, Q8, plus one follow-up from each.
- **30-minute technical interview:** Q2, Q5, Q9, Q11.
- **45-minute FDE design interview:** Q3, Q7, Q10, Q13, Q15.

**Rating rubric (per question)**

| Rating | Observable behavior |
|---|---|
| **0 — Missing** | Incorrect or irrelevant; confuses core components. |
| **1 — Emerging** | Correct terminology, but little mechanism, validation, or engineering trade-off. |
| **2 — Competent** | Accurate explanation, workable implementation or evaluation, and key limitations. |
| **3 — Strong** | Adds precise failure analysis, concrete measurements, relevant alternatives, and customer-facing implications. |

An overall interview should include both foundational and applied questions. Do **not**
infer production-readiness from a strong answer to a single question. Evaluate reasoning
separately from Python syntax fluency.

> [!NOTE]
> Tool-execution loops, harness internals, and agent frameworks are assessed in S01, not
> here.

---

## A. 🧩 Fundamentals

### Q1. Where does the model end and the application begin?
**Difficulty:** Foundational · **Competency:** C1 · **Secondary:** C2

**Prompt:** A stakeholder says, "We purchased an LLM API, so now we have a customer
support product." Explain the missing pieces using a three-layer architecture.

**Expected strong answer:**
- **LLM:** processes supplied context and produces candidate outputs.
- **Serving API/gateway:** exposes supported models, authentication, request/response contracts, routing and metering; features vary by provider.
- **Application:** owns business policy, access control, orchestration, response validation, retries/failure behavior, persistence, user experience and task evaluation.
- An API call is a building block, not the deployed business capability.

**Weak answer to probe:** "The LLM handles everything" or "the API guarantees a correct response."
**Probing follow-ups:** Who decides whether an incorrectly classified ticket is escalated? What changes if the model provider is replaced but business rules stay constant?
**Evidence of mastery:** Candidate draws the boundaries and assigns a concrete failure to the correct owner.
**Common misconception:** The inference service is equivalent to the end-user product.

### Q2. What is a context window, and why does it matter?
**Difficulty:** Foundational · **Competency:** C1 · **Secondary:** C5

**Prompt:** Northstar wants to attach its entire knowledge base to every support ticket
because its selected model advertises a large context window. Assess the idea.

**Expected strong answer:**
- Context is the data and instructions available for that model request or server-managed session; the supported window and input/output limits are model/API-specific.
- Limits, cost, latency and relevance all matter; a larger context is not necessarily a better answer.
- Irrelevant, contradictory or stale material can distract the model, and some relevant material may still be missed.
- Establish what each task needs before deciding how much context to supply.

**Weak answer:** "It fits, so there is no problem."
**Probes:** How would you detect when context size is hurting results? What should happen when a request exceeds a provider limit?
**Mastery signal:** Suggests a small controlled experiment with fixed tickets, smaller curated context, and measured correctness/latency/usage.

### Q3. Does increasing reasoning effort automatically improve quality?
**Difficulty:** Intermediate · **Competency:** C2 · **Secondary:** C4, C5

**Prompt:** A lead proposes that every ticket request use the provider's maximum reasoning
setting. Is that defensible?

**Expected strong answer:**
- Reasoning settings are provider/model-specific; some models do not expose equivalent controls.
- More inference work may help difficult tasks but can be unnecessary for simple classification.
- Compare measured task outcomes, tail latency, token usage, and cost at multiple supported settings.
- Evaluate hard and ambiguous cases separately rather than using only overall accuracy.
- Generated rationales are **not** guaranteed faithful transcripts of internal reasoning.

**Weak answer:** "Higher reasoning is always smarter," or "it is just chain-of-thought text."
**Probes:** What result would persuade you to lower effort? Would an improvement from 95% to 96% justify a threefold latency increase?

---

## B. 🧩 Typed outputs, contracts, and debugging

### Q4. Does schema-valid JSON prove the model made the right decision?
**Difficulty:** Foundational · **Competency:** C1 · **Secondary:** C4

**Prompt:** The classifier returns `{"priority":"low"}` and it passes Pydantic validation,
but the ticket says a production outage impacts all customers. What can you conclude?

**Expected strong answer:**
- Schema validation shows permitted **shape/type/allowed values**; it does not establish factual or business correctness.
- A separate acceptance rule or task evaluator must assess whether `low` is appropriate.
- A valid response can still misinterpret an incident, lack evidence, or violate the customer's rubric.
- Prefer explicit escalation/uncertainty paths and review difficult failures.

**Weak answer:** "Pydantic confirms that the priority is correct."
**Probes:** Which checks belong before calling the model? What if the label is valid but the summary fabricates a fact?

### Q5. Diagnose a Pydantic contract bug
**Difficulty:** Intermediate · Code/debugging · **Competency:** C1 · **Secondary:** C4

**Prompt:** A learner writes:

```python
from pydantic import BaseModel

class TicketDecision(BaseModel):
    priority: str
    needs_human: bool

payload = {"priority": "urgentest", "needs_human": "yes"}
record = TicketDecision.model_validate(payload)
```

What is problematic, and how would you improve the contract?

**Expected strong answer:**
- `str` permits arbitrary priority labels such as `urgentest`.
- Pydantic may coerce certain string inputs to booleans in its default validation mode; relying on coercion may mask integration mistakes.
- Constrain priority with `Literal["low", "medium", "high"]` or an enum.
- Consider `StrictBool` for strict input validation; test exact accepted inputs.
- Still evaluate decision correctness independently.

**Possible revised snippet:**

```python
from typing import Literal
from pydantic import BaseModel, StrictBool

class TicketDecision(BaseModel):
    priority: Literal["low", "medium", "high"]
    needs_human: StrictBool
```

**Weak answer:** "No issue; Pydantic always rejects bad values."
**Probes:** Would the revised schema prevent assigning `low` to an outage? What should the API do with a validation error?
**Code status:** Illustrative; not executed as part of this artifact.

### Q6. A provider claims to support structured outputs. What would you verify?
**Difficulty:** Intermediate · **Competency:** C3 · **Secondary:** C1, C4

**Prompt:** Northstar routes several models through an API gateway. One model accepts an
ordinary JSON prompt but rejects a schema-enforced call.

**Expected strong answer:**
- Separate **prompting for JSON**, provider-native JSON mode, schema-constrained generation, and client-side parsing/validation.
- Check model-level and route/provider-level support; gateway compatibility does not imply every backend supports every feature.
- Validate refusal, truncation, timeout, malformed response, and unsupported-schema paths.
- Establish fallback behavior: retry within limits, move to supported route, or refer to human review.
- Test under the same route/model configuration intended for the application.

**Weak answer:** "The API is OpenAI-compatible, so all features must work."
**Probes:** What telemetry identifies whether the failure was transport, unsupported capability, malformed payload, or incorrect business classification?

### Q7. Build a contract and negative tests for a support classification API
**Difficulty:** Advanced · Applied code/design · **Competency:** C1 · **Secondary:** C4, C3

**Prompt:** Specify `category`, `priority`, `needs_human`, and `summary`, and describe
four tests you would run before plugging in an LLM.

**Expected strong answer:**
- Type constrained category and priority; boolean human-review flag; bounded/nonempty summary where appropriate.
- Four kinds of tests might include unknown categories, invalid types, missing required fields, and semantically inconsistent payloads.
- Distinguishes schema tests from business-policy consistency tests.
- Defines the downstream contract for validation failure (clear error, quarantine, fallback, not silent acceptance).

**Weak answer:** Provides only a happy-path payload and assumes the model never fails.
**Probes:** Who owns backward compatibility? Would you change the schema before or after aligning business labels with the customer?

---

## C. 🔍 Evaluation, model choice, and debugging

### Q8. Design a fair two-model comparison
**Difficulty:** Intermediate · **Competency:** C4 · **Secondary:** C2, C5

**Prompt:** You can access Model A and Model B. Northstar needs ticket category and
priority classification. How do you choose?

**Expected strong answer:**
- Define task and labels with business stakeholders; use the same held-out synthetic examples, rubric, input context, output schema and reporting method.
- Capture correctness by field and case type, invalid/missing responses, latency distribution and actual usage/cost.
- Repeat trials where model stochasticity matters; compare supported reasoning/settings transparently.
- Inspect failures, especially high-impact escalation misses; avoid choosing solely by a public ranking.
- Document sample-size and distribution limitations before recommending production use.

**Weak answer:** "Use the model with the best public benchmark score."
**Probes:** Why is a five-ticket test insufficient? What if one model fails schema generation but has excellent classification when it responds?

### Q9. Debug suspiciously strong evaluation results
**Difficulty:** Advanced · Evaluation/debugging · **Competency:** C4 · **Secondary:** C2

**Prompt:** Your test results show 100% agreement with reference labels on 20 tickets.
What checks would you perform before claiming the solution is reliable?

**Expected strong answer:**
- Check data leakage: examples/labels accidentally present in prompts, duplicated records or development/test overlap.
- Validate label correctness, representative class balance and difficulty; check whether labels reflect current policy.
- Inspect per-category outcomes, missing/ambiguous cases and failure of escalation logic.
- Report confidence limits; 20 examples cannot establish robust performance across a broad population.
- Verify reproducibility and log model, configuration, prompt version, dataset version and provider route.

**Weak answer:** "100% means production-ready."
**Probes:** How would you construct a held-out set? What happens when the customer's policy changes next month?

### Q10. What matters more: overall accuracy or error type?
**Difficulty:** Advanced · **Competency:** C4 · **Secondary:** C2, C6

**Prompt:** Two models are 90% accurate. Model A occasionally marks high-severity outages
as `low`; Model B more often marks routine tickets `high`. Which one should you choose?

**Expected strong answer:**
- Cannot decide from aggregate accuracy alone. Define stakeholder-specific error costs and acceptance thresholds.
- Analyze a severity-aware confusion matrix or per-class recall/precision; specifically quantify missed high-severity cases.
- Consider conservative escalation, human review or deterministic overrides for high-risk conditions.
- Choose by measured business impact and system performance, not accuracy alone.

**Weak answer:** "They are equal because both are 90% accurate."
**Probes:** What questions would you ask a customer operations lead? What evidence would you bring to that conversation?

### Q11. Explain token billing and caching to a tech lead
**Difficulty:** Intermediate · **Competency:** C5 · **Secondary:** C1

**Prompt:** A repeated system instruction dominates Northstar's prompts. The lead wants to
know whether prompt caching will cut the bill by 75%.

**Expected strong answer:**
- Token prices and caching rules vary by model, provider, route and eligible prefix.
- Total cost includes input, output, possible cache write/read charges and other provider-specific pricing.
- Measure reported **actual** cache hits and cost on a representative workload; do not assume any fixed discount.
- Optimize only after measuring quality and usage; maintain stable prefixes when relevant and safe.

**Weak answer:** "Caching always makes the whole request four times cheaper."
**Probes:** Could a cached prompt prefix be stale? Why might reducing response length hurt task quality?

### Q12. Benchmark intelligence versus business fitness
**Difficulty:** Intermediate · **Competency:** C2 · **Secondary:** C4

**Prompt:** A frontier model tops a public intelligence index but a smaller model performs
comparably on Northstar's ticket labels. What recommendation do you make?

**Expected strong answer:**
- Public benchmarks help shortlist candidates but are not acceptance tests for a particular customer workflow.
- Prefer the smallest/cheapest/fastest **configuration that meets explicit quality and operational constraints**, after representative comparison.
- Include variability, route behavior, privacy requirements and monitoring in the recommendation.
- Reevaluate as models, pricing and traffic patterns change.

**Weak answer:** "Always buy the strongest model because it is safer."
**Probes:** Under what circumstances might the frontier model still be worth choosing? What would change your recommendation?

---

## D. 🗺️ Forward-deployed engineering scenarios

### Q13. The customer asks for "an AI that handles support tickets"
**Difficulty:** Advanced · Customer discovery · **Competency:** C6 · **Secondary:** C2, C4

**Prompt:** In a 10-minute kickoff, what must you clarify before choosing a model or
writing code?

**Expected strong answer:**
- What action is needed: classify, summarize, recommend, or autonomously execute?
- Which ticket categories, escalation policies and existing APIs define the task?
- What are the acceptance criteria, sample labels, high-cost error categories and human handoff requirements?
- What are the latency, volume, budget, data handling and integration boundaries?
- What does a successful pilot demonstrate, and which decisions remain human-owned?

**Weak answer:** Immediately recommends a specific LLM or an agent framework before defining the problem.
**Probes:** What can you reasonably prototype in one day? How would you handle conflicting stakeholder definitions of "urgent"?

### Q14. A production model suddenly misclassifies billing tickets
**Difficulty:** Advanced · Troubleshooting · **Competency:** C4 · **Secondary:** C3, C5

**Prompt:** Last week's classifier worked on test data. Today billing tickets
increasingly receive the wrong category. Describe your investigation plan.

**Expected strong answer:**
- First determine blast radius and safe fallback; avoid silent automated downstream actions.
- Check input drift, ticket mix, new ticket templates, policy label changes and integration parsing.
- Compare prompt/schema versions, model and route IDs, configuration, usage/latency and error logs.
- Reproduce on a fixed regression set and newly collected representative cases, with privacy-safe data handling.
- Isolate data, model, prompt and business-rule causes; propose targeted fixes and rerun evaluations.

**Weak answer:** "Just upgrade to the newest model" or "add more tokens to the prompt."
**Probes:** What if the provider silently changes the backend? What telemetry should the team collect from the start?

### Q15. Make a recommendation to Northstar's VP of Support
**Difficulty:** Advanced · Oral FDE exercise · **Competency:** C6 · **Secondary:** C2, C4, C5

**Prompt:** Present a 90-second recommendation. You tested two synthetic-model
configurations on 60 labeled tickets. Assume the following illustrative results:

| Measure | Configuration A | Configuration B |
|---|---:|---:|
| Correct category + priority | 54/60 (90%) | 56/60 (93.3%) |
| High-severity misses | 0/12 | 2/12 |
| p95 latency | 1.4 s | 3.1 s |
| Measured cost per 1,000 tickets | $1.20 | $3.80 |

**Expected strong answer:**
- Does not equate higher total accuracy with higher safety or business value.
- Calls out the two severe misses in B and the tiny sample sizes; recommends **A as a provisional pilot candidate**, not as a production-proven winner, assuming escalation risk is a priority.
- Communicates the quality/latency/cost trade-off without jargon and identifies what must be tested next.
- Requests more representative high-severity examples, policy review and a documented acceptance threshold before production rollout.

**Weak answer:** "B wins because 93.3% is higher than 90%," or "A is definitively safe because it had zero severe misses in 12 examples."
**Probes:** What evidence would reverse your recommendation? How would you present statistical uncertainty to a nontechnical executive?
**Assumptions:** All figures are hypothetical for interview practice, not real API benchmarks or course lab measurements.

---

## E. ✅ Self-assessment scoring sheet

| Dimension | Questions that provide evidence | Strong-answer indicators | Score (0–3) |
|---|---|---|---|
| Layer boundaries and terminology | Q1, Q2, Q6 | Clear ownership of model/API/application responsibilities | ___ |
| Contract design and implementation | Q4, Q5, Q7 | Schema limits, meaningful tests, deterministic validation | ___ |
| Evaluation rigor | Q3, Q8, Q9, Q10, Q12 | Task data, failure type, measurement and uncertainty | ___ |
| Operations/cost judgment | Q2, Q3, Q11, Q14 | Provider-specific assumptions, latency, usage, reproducibility | ___ |
| Customer-facing architecture decisions | Q10, Q13, Q15 | Requirements first, defensible trade-offs and next steps | ___ |

**Suggested interpretation:** Average ~2 indicates practical readiness for S02 learning
objectives; ~3 indicates strong practical judgment within this session's scope. These
ratings are instructional heuristics, **not calibrated hiring cutoffs**.

### ⚠️ Red flags that justify deeper probing

- Treats schema validity as a guarantee of factual or business correctness.
- Claims a single benchmark identifies the best model for all workflows.
- Treats maximum reasoning or maximum context as universally superior.
- Ignores severe error categories while celebrating overall accuracy.
- Assumes every API gateway supports every endpoint feature equally.
- Recommends an autonomous agent for a simple classification task without evidence of need.
- Treats a small synthetic evaluation set as a production validation.

## 🗺️ Bridge to S01

Consider: **"If Northstar sometimes needs to look up an account, sometimes needs incident
status, and sometimes needs no lookup at all, how could the application decide what to do
next?"**

A fixed, explicitly programmed workflow may suffice. If the model needs to dynamically
choose permitted operations, that is the move into **tools, agent loops, and harnesses —
already covered in S01: Verified Agent Loops**. Do not assume dynamic autonomy is
automatically the better design.

---

## 🛠️ Recommended learner practice

1. Rehearse Q1, Q4 and Q10 as concise whiteboard explanations.
2. Run the Q5 Pydantic snippet in the course environment and verify the coercion behavior
   for the pinned version.
3. Prepare two Northstar tickets with distinct error-cost implications.
4. Recheck provider-specific structured-output, reasoning, and caching behavior before
   applying the ideas to a real system.
5. Use the S02 quiz for basic retention; use this bank to probe deeper technical and
   customer judgment.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
