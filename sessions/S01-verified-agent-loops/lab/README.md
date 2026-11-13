# S01 — Northstar Verified Agent Loop Lab

**Audience:** Experienced software professionals, including learners new to Python. **Duration:** 90-minute live session, plus optional extensions. All data is synthetic.

## 💻 Quick start (VS Code terminal)

1. Open this folder in VS Code.
2. Install `uv` during pre-course onboarding; verify with `uv --version`.
3. Run `uv sync --group dev` (generates `uv.lock` if missing; commit it after resolution).
4. Run `uv run python main.py --mode mock`.
5. Run `uv run python main.py --mode mock --ticket T-101` to compare a single-call task.
6. Run `uv run python main.py --mode mock --ticket T-101 --invalid-first` to see verifier feedback and retry.
7. Run `uv run pytest` to execute the tests.

`uv` may install the pinned Python 3.12 if not available; network access is required for initial environment setup. The mock application itself uses only the Python standard library.

## 🧩 Concept map

- **Agent loop:** model decision -> permitted tool execution -> observation -> model decision -> independent verification -> accept or escalate.
- **Harness:** tool allowlist, argument validation, ticket-scoped account lookup, step budget, repeated-call detection, structured trace.
- **Verification:** deterministic checks for fields, category, ticket identity, and evidence provenance. These checks **do not prove semantic correctness** of the category.
- **Loop Engineering:** course-defined umbrella for feedback, bounded retries, event-driven continuation, and measured improvement. It is not a standardized industry component.
- **Hill-climbing:** optional extension: compare a proposed improvement against a fixed labeled evaluation set; do not optimize against one anecdotal ticket.

## 🛠️ Checkpoints / exercises

**00 — Starter:** inspect `data/tickets.json`, `pyproject.toml`, and `main.py`; run mock.

**01 — Single call:** use `--ticket T-101`. Locate model decision and verifier; explain why a tool is unnecessary.

**02 — Tool loop:** use `--ticket T-104`. Find the `tool_executed` trace event. Identify where tool authorization happens in `triage/core.py`.

**03 — Verification:** use `--ticket T-101 --invalid-first`. Identify `verification_failed` and the corrected result. Change `--max-steps 1` and explain escalation.

**Challenge A:** Add an allowed `priority` policy based on explicit ticket signals. Write tests; discuss false positives.

**Challenge B:** Add a fixture where an account is not found. Ensure the final answer does not claim account evidence and considers human review.

**Challenge C:** Write a small labeled evaluation set and compare accuracy, tool count, and escalation rate between two policies.

## 💻 Optional live model mode (requires credentials and provider validation)

1. Run `uv sync --group live --group dev`.
2. Copy `.env.example` to `.env`, configure a **tested** tool-capable model and provider key. Never commit `.env`.
3. Run `uv run python main.py --mode live`.

The live adapter uses OpenAI-compatible Chat Completions. It is intentionally small: it reconstructs each request from the ticket, observations, and verification feedback rather than maintaining a full provider-native multi-message tool transcript. This works as a pedagogical orchestration pattern for compatible models but is **not** a production agent implementation.

> [!CAUTION]
> Providers differ in tool behavior and JSON fidelity; the live path is **not
> prevalidated** and may incur charges. Test it in your environment before relying on it. No
> automatic retry of network failures is implemented.

## 🔍 Troubleshooting

- `uv` not found: complete pre-course installation and restart terminal.
- Python version unavailable: `uv python install 3.12` then `uv sync`.
- Tests unavailable: run `uv sync --group dev`.
- Live `401` or missing key: check `.env` locally; never share keys in screenshots.
- Live malformed output: inspect trace; verifier should reject or escalate.
- Network or provider unavailable: switch to `--mode mock` immediately.

## ✅ Validation checklist

- [ ] Mock CLI run succeeds on direct ticket and lookup ticket.
- [ ] Injected failure is rejected and corrected or escalated.
- [ ] `uv run pytest` passes in target environments.
- [ ] Live provider tool calling tested separately, if demonstrated.
- [ ] No secrets or real customer data included.

## Scope / limitations

This is an instructional prototype, not a production ticket router. The mock class uses hand-coded branching and is **not an LLM**. The verifier checks structural and evidence-provenance requirements, not ground-truth classification accuracy. A real system would add stronger authentication, PII handling, timeouts, audit logging, evaluation datasets, idempotency, monitoring, and human-review routing.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
