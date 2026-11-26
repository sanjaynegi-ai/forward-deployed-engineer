# S01 — Northstar Verified Agent Loop Lab

**Audience:** Experienced software professionals, including learners new to Python. **Duration:** 90-minute live session, plus optional extensions. All data is synthetic.

## 💻 Quick start

Environment setup — installing `uv`, syncing dependencies, selecting the kernel — is a
one-time step done once at the **repo root**, not per lab: see the root
[`README.md`](../../../README.md) and [`docs/TOOLING.md`](../../../docs/TOOLING.md).
Once that's done, everything below runs from this folder:

1. `uv run python main.py --mode mock`.
2. `uv run python main.py --mode mock --ticket T-101` to compare a single-call task.
3. `uv run python main.py --mode mock --ticket T-101 --invalid-first` to see verifier feedback and retry.
4. `uv run python main.py --mode mock --ticket T-110` to see the two-tool escalation
   path: `lookup_account` → `create_escalation` → final decision, on a premium account
   with a high-priority ticket.
5. `uv run python main.py --mode mock --ticket T-111` to see the same critical
   wording **not** escalate, because the account is standard tier, not premium.
6. `uv run pytest` to execute the tests (14, including six for `create_escalation`'s
   authorization and duplicate-prevention behavior).

The mock application itself uses only the Python standard library.

## 📓 This lab's two notebooks

Both notebooks open and run from the repo root's shared Jupyter environment — see the
root `README.md` / `docs/TOOLING.md` for setup; nothing in this folder needs its own.

- **`S01_Northstar_Triage_Notebook.ipynb`** — the core lab: classify tickets with
  `MockModel`, observe the agent loop, watch verification and retry, see Loop
  Engineering in the trace. See the concept map below.
- **`Tool_Calling_From_Scratch.ipynb`** — optional companion (see the note below).

Jupyter starts each notebook's kernel with its working directory set to the notebook's
own folder, so `from triage.core import ...` and `data/tickets.json` resolve correctly
no matter which directory Jupyter itself was launched from.

## 🧩 Concept map

- **Agent loop:** model decision -> permitted tool execution -> observation -> model decision -> independent verification -> accept or escalate.
- **Registry and dispatcher:** `triage/core.py`'s tool allowlist and the branch inside
  `run_agent` that looks a tool up by name, validates its arguments, authorizes it, and
  executes it are a concrete instance of the registry/dispatcher pattern — see the
  handout's new "what the application authorizes and executes it actually means in
  code" section if you want the pattern named explicitly before reading the real code.
- **Harness:** tool allowlist (now two tools: read-only `lookup_account` and
  side-effecting `create_escalation`), argument validation, ticket-scoped account
  lookup, step budget, repeated-call detection, business-level duplicate-side-effect
  prevention, structured trace.
- **Verification:** deterministic checks for fields, category, ticket identity, and evidence provenance. These checks **do not prove semantic correctness** of the category.
- **Loop Engineering:** course-defined umbrella for feedback, bounded retries, event-driven continuation, and measured improvement. It is not a standardized industry component.
- **Hill-climbing:** optional extension: compare a proposed improvement against a fixed labeled evaluation set; do not optimize against one anecdotal ticket.

> [!NOTE]
> **Optional companion notebook:** `Tool_Calling_From_Scratch.ipynb` builds the
> registry/dispatcher/bounded-loop pattern from an ordinary Python function up, with a
> weather example, before re-applying it to this lab's real `triage.core` tools —
> including a live replay of the authorization-failure trace below and all eight
> framework-safety failure modes, each actually executed. No fixed timebox; no API key
> required for its required path (Parts 1–4). See
> `docs/curriculum/tool-calling-from-scratch-teaching-guide.md` for suggested pacing if
> run live.

## 🛠️ Checkpoints / exercises

**00 — Starter:** inspect `data/tickets.json`, `triage/core.py`, and `main.py`; run mock.

**01 — Single call:** use `--ticket T-101`. Locate model decision and verifier; explain why a tool is unnecessary.

**02 — Tool loop:** use `--ticket T-104`. Find the `tool_executed` trace event. Identify where tool authorization happens in `triage/core.py`.

**03 — Verification:** use `--ticket T-101 --invalid-first`. Identify `verification_failed` and the corrected result. Change `--max-steps 1` and explain escalation.

**Challenge A:** Add an allowed `priority` policy based on explicit ticket signals. Write tests; discuss false positives.

**Challenge B:** Add a fixture where an account is not found. Ensure the final answer does not claim account evidence and considers human review.

**Challenge C:** Write a small labeled evaluation set and compare accuracy, tool count, and escalation rate between two policies.

**04 — Escalation and duplicate-side-effect prevention:** use `--ticket T-110` (escalates)
and `--ticket T-111` (does not — standard tier). Then read
`tests/test_core.py::test_duplicate_escalation_prevented` and explain, in your own
words, why exact-argument repeated-call detection alone would not have caught that
specific scenario.

## 💻 Optional live model mode (requires credentials and provider validation)

1. Copy the repo root's `.env.example` to `.env` (also at the repo root) and configure a
   **tested** tool-capable model and provider key there. Never commit `.env`.
2. Run `uv run python main.py --mode live`.

The live adapter uses OpenAI-compatible Chat Completions. It is intentionally small: it reconstructs each request from the ticket, observations, and verification feedback rather than maintaining a full provider-native multi-message tool transcript. This works as a pedagogical orchestration pattern for compatible models but is **not** a production agent implementation.

> [!CAUTION]
> Providers differ in tool behavior and JSON fidelity; the live path is **not
> prevalidated** and may incur charges. Test it in your environment before relying on it. No
> automatic retry of network failures is implemented.

## 🔍 Troubleshooting

- `uv` not found, Python version unavailable, or tests unavailable: these are all
  environment/dependency issues — see the repo root's `README.md` / `docs/TOOLING.md`.
- Live `401` or missing key: check the repo root's `.env`; never share keys in screenshots.
- Live malformed output: inspect trace; verifier should reject or escalate.
- Network or provider unavailable: switch to `--mode mock` immediately.

## ✅ Validation checklist

- [ ] Mock CLI run succeeds on direct ticket and lookup ticket.
- [ ] Injected failure is rejected and corrected or escalated.
- [ ] `uv run pytest` passes in target environments.
- [ ] Live provider tool calling tested separately, if demonstrated.
- [ ] No secrets or real customer data included.

## Scope / limitations

This is an instructional prototype, not a production ticket router. The mock class uses hand-coded branching and is **not an LLM**. The verifier checks structural and evidence-provenance requirements, not ground-truth classification accuracy. `create_escalation`'s duplicate-side-effect check is scoped to one in-memory run of `run_agent` and keyed only on ticket ID — a real system would need this to be durable across process restarts (e.g., a database constraint or an idempotency-key table), not just an in-memory set. A real system would also add stronger authentication, PII handling, timeouts, audit logging, evaluation datasets, monitoring, and human-review routing.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
