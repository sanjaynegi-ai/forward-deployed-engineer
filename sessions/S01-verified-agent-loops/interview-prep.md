# S01 Interview Preparation — From LLM Calls to Verified Agent Loops

**Course:** AI-Focused Forward Deployed Engineering · Session 01  
**Audience:** Experienced software professionals; Python/LLM experience not assumed  
**Scenario:** Northstar Support Systems, a fictional customer with synthetic support tickets  
**Competencies:** C1 AI Engineering Fundamentals (primary), C4 Evaluation/Reliability/Security (primary), C3 Integration Engineering (secondary). C2/C6 are touched only through decision-making scenarios.

## How to use this guide

This is **interview preparation**, not a repeat of the S01 14-question learner quiz. The questions invite verbal reasoning, whiteboarding, pseudocode, and trade-off discussions. They assess what the candidate understands, how they diagnose uncertainty, and whether they choose proportionate solutions.

- **Self-study:** Attempt a question aloud in 2–4 minutes, then compare with the expected answer and practice the follow-up.
- **Peer mock interview (35 minutes):** 5 minutes fundamentals, 10 minutes code/control flow, 10 minutes debugging, 10 minutes customer architecture decision.
- **Extended peer mock interview (45 minutes):** Pick one question from each section, then add two probing follow-ups. Do not expect every question in one interview.
- **Evaluation scale (per question):** 0 = incorrect or unsafe; 1 = partial definition; 2 = correct with an example; 3 = correct, precise, and addresses trade-offs or failure modes. Score **reasoning**, not fluency or Python syntax memorization.

> [!NOTE]
> **Course terminology:** **Loop Engineering** is a teaching term for verification,
> event-driven continuation, bounded feedback, and measured improvement. It is not a
> standardized industry component.

---

## A. 🧩 Fundamentals

### F1. What is the difference between a model call and an agent loop?
**Level:** Foundational · **Competency:** C1

**Expected answer:** A model call submits context and receives a response. An agent loop is application-controlled repetition in which the model may request a tool, the application validates and executes it, the observation is added to state, and another model decision may follow. A loop needs explicit stopping and error behavior. Not every LLM feature needs an agent.

**Evaluation:** 1 point each for clear single-call definition, application-controlled iteration, and stopping/tool distinction.  
**Weak response:** “An agent is an LLM that thinks multiple times,” with no executable control flow.  
**Probe:** “If the model returns a tool call, has the database already been queried?” Expected: no; the application must authorize and execute it.

### F2. What belongs to the harness rather than the model?
**Level:** Foundational · **Competencies:** C1, C4

**Expected answer:** Tool registry and permissions, argument validation, state/history, execution and time budgets, retries, logging, error handling, and escalation are application responsibilities. The model proposes text or structured tool requests; it does not enforce access policy by itself.

**Evaluation:** Names at least three controls, locates enforcement in application code, and avoids claiming that a harness guarantees semantic truth.  
**Weak response:** “The system prompt tells the model not to call forbidden tools, so we are safe.”  
**Probe:** “Where would you enforce an account-scoped lookup?” Expected: server-side authorization using the caller's identity and permitted account scope.

### F3. Explain tool calling to a backend engineer unfamiliar with LLMs.
**Level:** Foundational · **Competency:** C1

**Expected answer:** A tool declaration resembles a typed API contract shown to the model. The model emits a proposed function name and arguments; the application parses, validates, authorizes, and invokes the actual function; its result becomes an observation for the next model call. The declaration is **not** the security boundary.

**Evaluation:** Uses the API analogy accurately and describes request/execution/result separation.  
**Weak response:** “The model directly invokes any Python function it wants.”  
**Probe:** “What if the tool arguments are malformed?” Expected: reject or return a structured tool error; do not blindly execute.

### F4. What is verification, and why isn't valid JSON enough?
**Level:** Foundational · **Competency:** C4

**Expected answer:** Verification evaluates a candidate result against independently specified criteria. Parsing checks syntax; schema validation checks required fields and types; business rules check allowed categories and identity consistency; semantic correctness may require labeled examples, trusted evidence, or human review. Valid JSON can still contain a wrong category or invented rationale.

**Evaluation:** Distinguishes syntactic, structural, and semantic checks; identifies a limitation of deterministic validation.  
**Weak response:** “If it matches the JSON schema, the classification is correct.”  
**Probe:** “How would you check whether `billing` is the *right* category?” Expected: ground-truth labels or human-reviewed examples, not just schema checks.

### F5. Explain `uv` to someone familiar with npm or Maven.
**Level:** Foundational · **Competency:** C1

**Expected answer:** `uv` manages Python projects, interpreters/environments, dependencies, and execution. `uv init` creates a project, `uv add` records dependencies, `uv sync` reconciles the environment with the lockfile, and `uv run` executes commands in the project environment. `pyproject.toml` expresses project configuration; `uv.lock` captures resolved dependencies; `.venv` is a local environment that should not be committed.

**Evaluation:** Correctly distinguishes declared dependencies, lockfile, and local environment; gives a runnable workflow.  
**Weak response:** “`uv` is just a replacement for the `python` command.”  
**Probe:** “Which files belong in source control?” Expected: usually `pyproject.toml`, `uv.lock`, and appropriate source; not `.venv` or secrets such as `.env`.

---

## B. 🧩 Intermediate technical reasoning

### I1. Whiteboard the smallest safe tool-using loop for Northstar.
**Level:** Intermediate · **Competencies:** C1, C3, C4

**Expected answer:** Start with ticket and bounded state; call model with allowed tool schemas; if a tool is requested, validate name, argument shape, caller/ticket scope, and step budget; execute only approved tool; append a sanitized result; repeat. If a final answer is returned, verify fields and permitted values; accept, retry with specific feedback if budget remains, or return a structured failure/human escalation. Include exception handling and telemetry.

**Evaluation:** Correct order, application-owned execution, explicit limit, verification, and terminal failure state.  
**Weak response:** A `while True` loop that trusts model-selected function names.  
**Probe:** “What if the model asks for the same lookup ten times?” Expected: repeated-call detection, limits, and fail-safe termination.

### I2. When should Northstar use rules, one LLM call, or an agent?
**Level:** Intermediate · **Competencies:** C1, C4; C2 reinforced

**Expected answer:** Rules for stable, well-defined mappings; a single structured LLM call for text interpretation with sufficient context; a bounded tool-using agent only when decisions genuinely require iterative external context or actions. Compare quality, latency, cost, permissions, failure surface, and maintainability using a labeled test set.

**Evaluation:** Starts from the problem and constraints, not enthusiasm for agents.  
**Weak response:** “Agentic is always more capable, so choose it by default.”  
**Probe:** “What evidence would justify upgrading the single-call baseline?” Expected: measured failures that a permitted lookup can address, with acceptable operational overhead.

### I3. What should be stored in agent state?
**Level:** Intermediate · **Competencies:** C1, C4

**Expected answer:** Ticket identifier, bounded conversation and tool results, current step, prior tool requests, verification feedback, correlation IDs, and relevant policy context. Avoid unnecessary sensitive data; enforce retention and size limits. Keep trusted control metadata distinct from untrusted ticket/tool content.

**Evaluation:** Addresses correctness and data minimization.  
**Weak response:** “Store every token and every customer field forever so the model remembers.”  
**Probe:** “How do you prevent an old tool result from being mistaken for a new one?” Expected: structured message types, request IDs, timestamps or versioning, and explicit state transitions.

### I4. How would you design a bounded retry policy?
**Level:** Intermediate · **Competency:** C4

**Expected answer:** Separate recoverable validation errors from nonrecoverable authorization/security failures; return specific verifier feedback; retry at most a defined number of times, preferably with changed context or deterministic repair when safe; enforce overall time/cost limits; escalate on exhaustion. Never retry unauthorized tool calls as if they were formatting mistakes.

**Evaluation:** Bound, targeted feedback, failure classification, safe terminal behavior.  
**Weak response:** “Keep asking until the LLM gets it right.”  
**Probe:** “What if retries increase the probability of a wrong but schema-valid answer?” Expected: use independent semantic evaluation, not blind acceptance.

### I5. What does event-driven continuation mean in this course?
**Level:** Intermediate · **Competency:** C1

**Expected answer:** The next transition occurs in response to a meaningful event—such as tool completion, verifier rejection, or an approval decision—rather than an uncontrolled polling loop. At S01 it is a **control-flow concept**, not a requirement to introduce Kafka, queues, or durable workflow engines.

**Evaluation:** Describes event and resulting state transition; distinguishes it from infrastructure.  
**Weak response:** “Event-driven means we must use a message broker.”  
**Probe:** “What if the tool never completes?” Expected: timeout, cancellation, recorded failure, and terminal/escalation path.

---

## C. 🧩 Advanced engineering judgment

### A1. A verifier accepts every schema-valid response. What can still go wrong?
**Level:** Advanced · **Competency:** C4

**Expected answer:** Wrong classification, unsupported evidence, mis-scoped account data, prompt injection, stale context, hidden bias across ticket types, and confidence overstatement. Add representative labeled evaluations, per-class and critical-error metrics, trace review, and escalation for ambiguous/high-impact cases. Schema validity is a necessary but insufficient property.

**Evaluation:** Identifies multiple failure classes and matching checks without promising absolute accuracy.  
**Weak response:** “Nothing; the verifier guarantees correctness.”  
**Probe:** “Which failures can you detect deterministically, and which need human labels?”

### A2. A model-requested tool result contains instructions to export customer data. How should the system react?
**Level:** Advanced · **Competencies:** C3, C4

**Expected answer:** Treat tool output as untrusted data, not a privileged instruction. Do not execute the export. Restrict tool capabilities and network egress, enforce authorization independent of model text, minimize data exposure, and log/flag suspicious content. A legitimate tool's data may still contain attacker-authored text.

**Evaluation:** Explicit trust boundary, preventive enforcement, observability.  
**Weak response:** “Add a stronger prompt saying to ignore malicious instructions,” without application controls.  
**Probe:** “Would you let the model choose arbitrary URLs for an outbound HTTP tool?” Expected: not without strict policy/allowlists and authorization.

### A3. How do you prevent a retry loop from causing duplicate side effects?
**Level:** Advanced · **Competencies:** C3, C4

**Expected answer:** Separate read-only lookups from writes; use idempotency keys, operation identifiers, deduplication, explicit confirmation, and state tracking for any side-effecting tool. Do not blindly replay a payment, ticket reassignment, or email after an ambiguous timeout. In S01, the account lookup is intentionally read-only.

**Evaluation:** Recognizes at-least-once execution risk and proposes concrete controls.  
**Weak response:** “Retries are harmless because the model is only text.”  
**Probe:** “The API times out after creating the ticket—what do you do before retrying?”

### A4. Describe hill-climbing as an engineering improvement method, and its limits.
**Level:** Advanced · **Competency:** C4

**Expected answer:** Define a metric and baseline; change one relevant component (e.g., classification instructions or validation policy); measure candidate on a controlled dataset; retain improvements that satisfy constraints; repeat cautiously. Risks include overfitting to the test set, noisy model outputs, local optima, regression on rare classes, and trading quality for latency/cost. S01 covers the intuition, not a production optimization framework.

**Evaluation:** Measurable objective, comparison procedure, at least two caveats.  
**Weak response:** “Just let the agent keep improving its own prompt until it says it is better.”  
**Probe:** “Why do you need a holdout set?” Expected: to check whether improvement generalizes beyond examples used to tune the system.

### A5. How would you observe a failed agent execution without exposing secrets?
**Level:** Advanced · **Competencies:** C4, C3

**Expected answer:** Record correlation ID, model/provider version, step count, tool name (not sensitive arguments by default), authorization outcome, durations, token/cost estimates when available, verifier errors, retries, and final status. Redact secrets/PII, restrict log access, set retention, and preserve enough structured metadata to replay with synthetic inputs where possible.

**Evaluation:** Debuggability plus privacy and access controls.  
**Weak response:** “Log every prompt, response, API key, and customer record.”  
**Probe:** “What minimum trace distinguishes model error from tool failure?”

---

## D. 🔍 Debugging and troubleshooting drills

### D1. Tool-call dispatch vulnerability
**Level:** Intermediate · **Competencies:** C3, C4

```python
def dispatch(name, arguments):
    return globals()[name](**arguments)
```

**Question:** Identify the defect and explain a safer design.

**Expected answer:** Arbitrary function resolution allows unintended callables and side effects. Replace with an explicit tool registry; validate the function name, arguments, ticket/account scope, permissions, and budget before execution. Return structured errors; never treat the model-supplied name as authority.

**Evaluation:** Names risk and specifies both allowlist and authorization.  
**Weak response:** “Catch `KeyError` and it is safe.”  
**Probe:** “Why is a JSON schema supplied to the model insufficient?”

### D2. Infinite-loop diagnosis
**Level:** Intermediate · **Competency:** C1

```python
while True:
    result = model_call(history)
    if result.tool_request:
        history.append(execute(result.tool_request))
        continue
    return result.answer
```

**Question:** What could fail, and how would you harden it?

**Expected answer:** No step/time/cost bounds, missing authorization and argument checks, no handling for repeated calls, no exception path, no final-result verification, possible uncontrolled history growth. Introduce bounded iterations, a safe dispatcher, structured tool messages, verifier, logging, and escalation.

**Evaluation:** Identifies at least four distinct flaws and prioritizes stopping and authorization.  
**Weak response:** “Set temperature to zero and the loop will terminate.”  
**Probe:** “What terminal result should a customer integration receive on exhaustion?”

### D3. Trace: schema-valid but wrong customer
**Level:** Advanced · **Competencies:** C3, C4

```text
request: ticket=T-104, account=A-17
model: lookup_account(account=A-71)
tool: returns A-71 billing status
model: {"ticket_id":"T-104","category":"billing","priority":"medium"}
verifier: schema OK
```

**Question:** What is the first unacceptable transition, and how should it be prevented?

**Expected answer:** The model's request to look up A-71 is not authorized merely because it is well formed. The dispatcher must enforce the ticket-to-account binding and caller permissions before execution. The verifier should also check provenance and account consistency; schema-only acceptance misses the data-scope breach.

**Evaluation:** Identifies the pre-execution authorization boundary; post-hoc validation alone is inadequate.  
**Weak response:** “The final category is plausible, so accept it.”  
**Probe:** “What if the model claims A-71 is the correct account?” Expected: verify against trusted application data.

### D4. Trace: repeated verifier rejection
**Level:** Intermediate · **Competency:** C4

```text
attempt 1: {"category":"billing"} -> missing ticket_id
attempt 2: {"category":"billing"} -> missing ticket_id
attempt 3: {"category":"billing"} -> missing ticket_id
```

**Question:** How do you diagnose and recover?

**Expected answer:** Confirm whether the schema was communicated, whether feedback was added to the next model request, and whether a deterministic field can be filled safely from trusted input. Bound retries and return an explicit failure/escalation on exhaustion. Do not silently weaken the schema to declare success.

**Evaluation:** Checks feedback propagation, considers safe deterministic repair, preserves the acceptance contract.  
**Weak response:** “Run the same prompt indefinitely.”  
**Probe:** “Is copying the ticket ID from trusted request metadata safer than asking the model to invent it?” Expected: generally yes, with identity checks.

---

## E. 🧩 FDE customer scenarios and architecture trade-offs

### S1. The customer demands an autonomous agent for ticket routing. What do you do first?
**Level:** FDE scenario · **Competencies:** C1, C4; C6 preview

**Expected answer:** Clarify the business outcome and existing routing baseline; obtain representative, appropriately handled labeled examples; identify costly misroutes and required account context; compare deterministic rules and one-call classification before adding a tool-using loop. Propose a small measured pilot with clear human escalation and data-access boundaries.

**Evaluation:** Discovery, measurable baseline, least-complex viable design, risk management.  
**Weak response:** “Start building a multi-agent architecture immediately.”  
**Probe:** “What would persuade you *not* to use an agent?”

### S2. An agent improves classification accuracy but doubles latency. Is it better?
**Level:** FDE scenario · **Competencies:** C1, C4; C2 preview

**Expected answer:** Cannot decide without service-level targets, severity-weighted error costs, volume, budget, and customer workflow. Compare per-class performance, critical misroute rates, p95 latency, cost per ticket, and escalation rate on representative data. Consider selective tool use only for ambiguous cases.

**Evaluation:** Rejects a single-metric decision and proposes measurable trade-offs.  
**Weak response:** “Accuracy always wins,” or “latency always wins.”  
**Probe:** “What if only 5% of tickets require the account lookup?” Expected: route only those cases to the more expensive path if validated.

### S3. Northstar's compliance team prohibits exposing account notes to external models. How do you adapt?
**Level:** FDE scenario · **Competencies:** C3, C4; C6 preview

**Expected answer:** Clarify policy and data classification; minimize/transform context where permitted; keep sensitive decisions or lookups in trusted application code; use deterministic rules or approved model deployment paths as appropriate; enforce tool scope and auditability. Do not claim a provider is compliant without documented verification.

**Evaluation:** Honors hard constraints and offers workable alternatives.  
**Weak response:** “Just turn off training in the API settings and send everything.”  
**Probe:** “What customer evidence do you need before selecting a model deployment?”

### S4. What would you demonstrate at the end of a one-week proof of concept?
**Level:** FDE scenario · **Competencies:** C1, C4; C6 preview

**Expected answer:** A reproducible run on synthetic or approved tickets; comparison to baseline; successful tool-request and verification traces; examples of safe rejection/escalation; measured latency/cost where available; known limitations; and a clear go/no-go decision with next steps. Distinguish demo success from production readiness.

**Evaluation:** Evidence of value, reliability, and transparency about limitations.  
**Weak response:** “A polished demo with three hand-picked successes proves it works.”  
**Probe:** “What would your acceptance criteria be for a pilot?”

---

## F. ✅ Compact mock-interview scoring sheet

| Dimension | What a strong answer demonstrates | Score (0–3) |
|---|---|---|
| Conceptual precision | Separates model request, tool execution, loop, harness, and verifier | ___ |
| Safe control flow | Authorization, validation, budgets, stopping, escalation | ___ |
| Evaluation reasoning | Distinguishes schema checks from semantic quality; uses baselines | ___ |
| Debugging | Finds the first failed trust/state boundary from a trace | ___ |
| Architecture judgment | Chooses rules, one call, or agent based on measured need | ___ |
| Customer delivery mindset | Asks for constraints and defines success evidence | ___ |

**Interpretation:** 15–18 = strong for S01; 11–14 = solid with targeted gaps; 0–10 = revisit concepts. These are **formative self-assessment heuristics**, not validated hiring cutoffs. S01 alone does not certify FDE job readiness.

### ⚠️ Red flags to listen for

- Equates a model-generated tool request with an executed side effect.
- Relies on prompting alone for permissions or data access.
- Assumes schema-valid output means business-correct output.
- Has no stop condition or failure result for a loop.
- Recommends agent complexity without a baseline.
- Treats repeated prompt tuning on a tiny dataset as proof of generalization.

### ✅ Positive signals

- Draws explicit trust boundaries and can explain failure modes.
- Chooses simpler software when it meets requirements.
- Specifies what is deterministic and what needs empirical evaluation.
- Designs for observable failures, safe escalation, and customer acceptance.

---

## G. 🛠️ Teach-back challenge

After using this guide, you should be able to perform the following **without notes**:

1. Draw the model → tool request → authorization → execution → observation → model sequence.
2. Explain the difference between **Agent Loop**, **Harness Engineering**, and our course-defined **Loop Engineering** in under 90 seconds.
3. Explain why event-driven continuation does not require a message broker.
4. Give an example of a schema-valid but semantically wrong ticket classification.
5. Describe a bounded recovery policy for invalid output and a different policy for unauthorized tool access.
6. Defend a rules-based or one-call baseline when a customer requests an agent.
7. Explain why a small improvement on the tuning dataset does not establish production reliability.

> [!TIP]
> **Self-check:** If you cannot explain any answer in plain software-engineering language,
> revisit the corresponding handout section before continuing your interview practice.

## 🗺️ Related learner resources

- **Handout:** Concise concept reference, including `uv` commands.
- **Quiz:** A 14-question, 40-point formative assessment.
- **Lab:** A runnable synthetic Northstar scenario with deterministic offline checks and
  an optional live-model path.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
