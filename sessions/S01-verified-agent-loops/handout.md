# S01 Learner Handout — From LLM Calls to Verified Agent Loops

**AI-Focused Forward Deployed Engineering · Session 01 · 90 minutes**  
**Case study:** Northstar Support Systems (fictional) · Support-ticket triage

Northstar's tickets already get answered by a model. This session answers a harder
question: who's allowed to act on that answer, when does the system get to try again, and
when does it have to stop and ask a human instead?

## 🎯 What you will learn

By the end of this session, you should be able to run a Python AI project with `uv`, distinguish a model's tool request from actual tool execution, trace a bounded agent loop, identify the harness's responsibilities, verify an output independently of the model's claims, and decide when *not* to use an agent.

## 1. 🧩 Start with the business problem

Northstar receives tickets that should be routed to **billing**, **technical**, **access**, or **general** support. Some tickets contain enough information to classify directly; others require a permitted lookup of synthetic account context.

**Engineering decision:** Start with the simplest workable approach. Rules may be enough for predictable inputs; a single model call may handle ambiguous text; a tool-using loop is justified only when the task needs additional information or actions. An agent is not automatically better.

Example *candidate* result (not yet verified):

```json
{"ticket_id":"T-104","category":"billing","priority":"medium","needs_human":false}
```

## 2. 🧩 Five essential concepts

| Concept | Meaning | Engineering question |
|---|---|---|
| **Model call** | Send context/instructions to a model and receive a response | What did the model propose? |
| **Agent loop** | Repeatedly request decisions, execute authorized tools, incorporate observations, and stop | What happens next, and when do we stop? |
| **Harness Engineering** | Design the software surrounding model execution: tools, state, permissions, limits, logging, and recovery | What can the agent safely do? |
| **Verification** | Independently check a proposed result against explicit criteria | Is the result acceptable? |
| **Loop Engineering** | Our course's teaching term for deliberately designing feedback, continuation, retries, stopping, and iterative improvement | How does the process react and improve? |

*Loop Engineering* is a course-defined perspective, not a universally standardized software component. It connects the agent loop, harness, and verification policy.

### The core control flow

```mermaid
flowchart TD
    A[Ticket and goal] --> B[Model proposes response or tool request]
    B --> C{Tool requested?}
    C -->|Yes| D[Application validates and authorizes request]
    D --> E[Execute permitted tool]
    E --> F[Return observation to conversation]
    F --> B
    C -->|No| G[Independent verifier]
    G --> H{Acceptable?}
    H -->|Yes| I[Accept result]
    H -->|No, budget remains| J[Provide specific feedback]
    J --> B
    H -->|No, budget exhausted| K[Abstain or escalate]

    classDef model fill:#2a78d6,color:#ffffff,stroke:#184f95
    classDef action fill:#eb6834,color:#ffffff,stroke:#b84420
    classDef success fill:#0ca30c,color:#ffffff,stroke:#076b07
    classDef failure fill:#d03b3b,color:#ffffff,stroke:#8f2626
    classDef pending fill:#fab219,color:#0b0b0b,stroke:#a8790f

    class B,C model
    class D,E,F,G,H action
    class I success
    class J pending
    class K failure
```

> [!IMPORTANT]
> The model can *request* a tool call; the application must authorize and execute it. A
> tool schema is not a security boundary. Actual SDK implementations also need to preserve
> tool-call identifiers and associate each result with the corresponding request.

### What "the application authorizes and executes it" actually means in code

An agent framework is not magic — it's a **tool registry** (names mapped to callables)
plus a **dispatcher** (the code that looks a name up, validates the arguments, checks
authorization, executes, and returns an observation). In the smallest possible terms:

```python
tools = {"lookup_account": lookup_account}          # the registry

def dispatch(name, args, state):                     # the dispatcher
    if name not in tools: return {"error": "unknown tool"}
    if not isinstance(args, dict): return {"error": "invalid arguments"}
    if not authorized(name, args, state): return {"error": "not authorized"}
    try:
        return {"result": tools[name](**args)}
    except Exception as exc:
        return {"error": str(exc)}
```

`dispatch()` is this course's name for the pattern, not a name every framework uses —
Part 5 of the companion notebook maps it onto LangGraph's actual `ToolNode`. What's
universal is the five-step mechanism: lookup, validate, authorize, execute, observe —
every one of them application code, none of them something the model does.

> [!TIP]
> **Build this yourself, from an ordinary Python function up to a full bounded loop:**
> `lab/Tool_Calling_From_Scratch.ipynb` — an optional companion notebook, no API key
> required for its required path, that builds exactly this progression with a weather
> example before re-applying it to Northstar's `create_escalation` tool below.

## 3. 💻 Work in VS Code with uv

The course's pre-course onboarding covers installation. In the starter project, use:

| Command | What it does |
|---|---|
| `uv --version` | Confirm uv is available |
| `uv init northstar-triage` | Initialize a new project (when starting from scratch) |
| `uv python pin 3.12` | Select a project Python version |
| `uv add openai python-dotenv` | Add dependencies when needed |
| `uv add --dev pytest` | Add pytest as a development dependency |
| `uv sync` | Synchronize environment from project metadata/lockfile |
| `uv run python main.py --mode mock` | Run the **planned starter-lab interface** using the managed environment |
| `uv run pytest` | Execute tests once provided |
| `uv tree` | Inspect dependency relationships |

**Project files:** `pyproject.toml` declares dependencies; `uv.lock` records resolved versions; `.venv/` is the local environment. Commit the lockfile for a reproducible application; do not commit `.venv/` or `.env` secrets. The `--mode mock` argument is part of our **planned lab application**, not a built-in uv option. A mock response is simulated, not a real model call.

## 4. 💻 Build a bounded agent loop

A conceptual sketch (not a drop-in SDK implementation):

```python
for step in range(max_steps):
    decision = model_call(conversation, available_tools)

    if decision.requests_tool:
        request = validate_and_authorize(decision.tool_request)
        observation = execute_tool(request)
        conversation = append_tool_exchange(conversation, decision, observation)
        continue

    errors = verify(decision.candidate, ticket_id)
    if not errors:
        return decision.candidate

    conversation = append_feedback(conversation, errors)

return {"status": "needs_review", "reason": "step budget exhausted"}
```

A production implementation also needs malformed-argument handling, tool timeouts, repeated-call detection, retry budgets, exception paths, and appropriately redacted telemetry. A maximum-step limit prevents unbounded looping; it does **not** guarantee correctness.

## 5. 🧩 Verify, then decide what happens next

Consider this invalid model output:

```json
{"ticket_id":"T-104","category":"refunds","priority":"medium"}
```

It violates two clear constraints: `refunds` is not an allowed category, and `needs_human` is missing.

```python
def verify(candidate: dict, expected_ticket_id: str) -> list[str]:
    errors = []
    if candidate.get("ticket_id") != expected_ticket_id:
        errors.append("ticket_id mismatch")
    if candidate.get("category") not in {"billing", "technical", "access", "general"}:
        errors.append("invalid category")
    if not isinstance(candidate.get("needs_human"), bool):
        errors.append("missing/invalid review flag")
    return errors
```

These checks verify **structure and explicit invariants**, not whether the category is semantically correct. For semantic quality, use reference-labeled tickets, evidence checks, representative evaluations, and human review when appropriate. Model-stated confidence is not independent evidence.

**Event-driven continuation:** A tool result arriving or a verifier returning a specific failure is an event that can justify the next step. This does not require a distributed event bus.

**Introductory hill-climbing:** Measure a baseline against a defined test set; make one targeted change (for example, improve the classification instructions); measure again; keep the change only if it improves the chosen objective without violating constraints. Beware noisy small samples and optimizing a metric that does not reflect customer outcomes.

## 6. 🔍 Security and failure modes

| Failure | Appropriate response |
|---|---|
| Model asks to look up another customer's account | Deny at tool authorization; do not rely on final-output verification |
| Model returns an out-of-enum category | Reject and return specific feedback within a retry budget |
| Model repeatedly calls the same tool | Detect repetition; stop or escalate |
| Tool fails or times out | Record controlled error; retry only when safe and bounded |
| Result passes JSON/schema checks but is factually wrong | Evaluate against evidence or reference labels; consider human review |
| API or model tool support unavailable | Use a clearly labeled deterministic mock path |
| Duplicate escalation request for the same ticket, worded differently each time | Block by a *business* key (the ticket), not just by matching the exact tool call |
| Well-formed arguments requesting an unsafe business action (e.g., escalating a standard-tier account) | Enforce business authorization separately from argument validity — a schema-valid call is not an authorized one |

The lab's own `create_escalation` tool (a **write**, side-effecting action, unlike the
read-only `lookup_account`) exercises both new rows directly: it's only authorized for a
high-priority ticket on a premium-support account, and the harness blocks a second
escalation for the same ticket even if the model's stated reason text differs the
second time. See `tests/test_core.py`'s `test_duplicate_escalation_prevented` for the
exact scenario, run and passing.

## 🗺️ Where these concepts appear in real agent frameworks

| This course's vocabulary | LangChain | LangGraph |
|---|---|---|
| Tool registry | A function passed to `tools=[...]` | Tools registered with a graph node |
| Model's tool request | `response.tool_calls` (`name`, `args`, `id`) | Same `AIMessage.tool_calls` |
| Dispatcher | The documented loop: look up by `name`, call `tool.invoke(call)` | `ToolNode` — a prebuilt node that runs the requested tools |
| Tool-call-ID-matched observation | A `ToolMessage` with a matching `tool_call_id` | Same convention |
| Authorization (this course's own addition — not built in) | Not provided; you still write this | `wrap_tool_call` hook, or your own node before `ToolNode` |

**Verified current links** (checked live, not quoted from memory — one stale URL,
`python.langchain.com/docs/concepts/tool_calling`, now permanently redirects, which is
exactly the kind of drift to expect and re-check yourself later):
[LangChain tool calling](https://docs.langchain.com/oss/python/langchain/models) ·
[LangGraph `ToolNode`](https://reference.langchain.com/python/langgraph.prebuilt/tool_node/ToolNode) ·
[`ToolNode` source](https://github.com/langchain-ai/langgraph/blob/main/libs/prebuilt/langgraph/prebuilt/tool_node.py).

A framework gives you the registry-and-dispatcher scaffolding; it never gives you the
authorization policy itself — that's still your job, in a framework or out of one. The
companion notebook's Part 5 has the full mapping and an optional source-reading exercise.

> [!CAUTION]
> Use **synthetic data only** for exercises. Never commit API keys or display real secrets.
> Provider privacy settings, pricing, and tool compatibility must be checked before using a
> live endpoint.

## 🛠️ Forward Deployed Engineer Decision Challenge

**Customer scenario:** Northstar wants an AI workflow to retrieve account details and
route tickets end to end, including billing disputes, with minimal engineering review —
while Security/Compliance hasn't signed off on what account data it can touch.

**Engineering decision:** Which tools are authorized and which are explicitly
prohibited, what verification and retry/stop limits apply, what triggers human
escalation, and whether a bounded tool loop is even the right scope yet.

**Your deliverable:** A short workflow authorization-and-escalation design one-pager.
~10–15 minutes. Do this **before** attempting the hands-on challenge below — it sets the
policy that challenge's trace will test.

**Full exercise, rubric, and worked examples:**
[`docs/fde-exercises/verified-agent-loop-decision.md`](../../docs/fde-exercises/verified-agent-loop-decision.md)

## 7. 🛠️ Hands-on challenge

Inspect this trace:

```text
1. Ticket T-104 arrives for account A-104.
2. Model requests lookup for account A-999.
3. Tool returns account A-999 details.
4. Model proposes category = "refunds".
5. Application accepts the result.
```

**Your task:** Identify (a) the authorization failure, (b) the verification failure, (c) the safe next action, and (d) one test that would catch each problem. Explain why correcting the final category would **not** undo an earlier unauthorized disclosure.

### ✅ Quick knowledge check

1. Does a model-generated tool call mean the tool has executed?
2. Can valid JSON still be wrong?
3. What stops a failed agent from retrying forever?
4. When might a single LLM call be preferable to an agent loop?
5. How does a verifier differ from the model evaluating its own answer?

> [!TIP]
> **Expected takeaways:** The model proposes; application code authorizes and acts;
> verification checks explicit criteria; bounded feedback determines whether to accept,
> retry, abstain, or escalate.

## 📚 Further reading

- [uv: Projects](https://docs.astral.sh/uv/guides/projects/) — environments, dependencies, and lockfiles.
- [uv: CLI reference](https://docs.astral.sh/uv/reference/cli/) — command details.
- [OpenAI: Function calling](https://platform.openai.com/docs/guides/function-calling) — tool request and execution concepts.
- [OWASP: LLM application security](https://genai.owasp.org/) — prompt injection and tool-use risks.

## 🗺️ What you have built, and what's next

**What you have built:** a working bounded agent loop (`triage/core.py`) with **two**
tools — the original read-only `lookup_account` and a new, side-effecting
`create_escalation` — tool authorization, repeated-call detection, business-level
duplicate-side-effect prevention, independent verification, bounded retry with
feedback, and escalation on exhaustion — exercised by a passing 14-test suite, not just
described. If you worked through the optional companion notebook, you also built a
generic tool registry and dispatcher from first principles, before ever seeing
`triage/core.py`'s version of the same mechanism.

**What limitations remain:** the verifier checks structure, identity, and evidence
provenance — not semantic classification accuracy. The mock model is a deterministic
stand-in, not a real LLM. A production system still needs stronger authentication, PII
handling, audit logging, and a real labeled evaluation set.

**What the next session adds:** **S02: Structured Outputs and Model Selection** adds a
typed decision contract and a model-comparison method for trusting *which* category or
priority gets chosen — this session's verifier checks that a result is well-formed and
authorized, not that the classification itself is correct. The two sessions don't
depend on each other and can be taken in either order.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
