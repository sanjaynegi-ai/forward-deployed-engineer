# S02 — Structured Outputs and Model Evaluation Lab

**Audience:** Experienced software professionals, including learners new to Python. **Duration:** 90-minute live session, plus optional extensions. All data is synthetic.

## 💻 Quick start

1. Open this folder in VS Code or JupyterLab.
2. Install the one dependency this lab needs: `python -m pip install 'pydantic>=2,<3'` (or run the commented `%pip install` line in the notebook's first cell).
3. Open `S02_Northstar_Model_Evaluation_Lab.ipynb` and run the cells **top to bottom** — later cells depend on classes and data defined earlier.
4. No API key, network access, or paid account is required for the core path. The optional live-model section (Part 7) is off by default (`RUN_LIVE = False`).

## 🧩 Concept map

- **Three engineering layers:** application → model-serving API/gateway → model. Each owns a different kind of failure.
- **Structured output:** a typed Pydantic contract the response must satisfy. This is a **validation rule**, not a correctness guarantee.
- **Schema validity vs. business correctness:** a response can be well-formed and still be the wrong decision for the ticket.
- **Task-first comparison:** two configurations are compared on the *same* synthetic tickets, with failures counted rather than discarded.
- **Cost estimation:** token-rate arithmetic illustrates billing mechanics; it is not a current price quote for any provider.

> [!NOTE]
> This lab does not build a tool-using agent — there is no model-directed action
> selection here. If you want that mechanism, see the **S01** lab
> (`../../S01-verified-agent-loops/lab/`).

## 🛠️ Checkpoints / exercises

**Part 1–2 — Contract:** Run the `TicketDecision` model against a valid and an invalid
record. Confirm you can explain *why* the invalid one is rejected before moving on.

**Part 3 — Data:** Read all 12 synthetic tickets before running anything against them.
Predict which ones look ambiguous.

**Part 4–5 — Comparison:** Run both simulated configurations and the evaluation function.
Identify which configuration trades a *dangerous* error (under-prioritizing a true
high-severity ticket) for a *safer* one (unnecessary human escalation).

**Mini exercise (Part 2):** Construct a case that **passes** schema validation but is
**wrong** for the ticket described — this is the fastest way to feel the schema/semantics
gap yourself.

**Learner modification (Part 5):** Add one ambiguous ticket, introduce one new simulated
failure case, and re-run. Does the aggregate accuracy number hide the new failure?

**Part 8 — FDE decision exercise:** Write the 3–5 sentence stakeholder recommendation.
This is the same skill tested in the quiz's Q14 and the interview bank's Q15 — practice it
here first.

## 💻 Optional live model mode (requires credentials and provider validation)

1. Install `openai`: `python -m pip install openai`.
2. Set `OPENROUTER_API_KEY` in your shell environment. Never commit it or paste it into the notebook.
3. In Part 7, set `RUN_LIVE = True` and `LIVE_MODEL` to a verified OpenRouter model ID that supports JSON response formatting.

> [!CAUTION]
> Requesting JSON output format is **not the same as** enforcing a JSON Schema at
> generation time. Review the provider's actual structured-output support, data-retention
> terms, and pricing before running a live call — and only on synthetic tickets, never real
> customer data. This path has not been executed as part of building this lab.

## 🔍 Troubleshooting

- `pydantic` import error: re-run the install command for your environment/kernel.
- `ValidationError` you didn't expect: re-read the `Literal` constraints — they're intentionally strict.
- Live section raises `RuntimeError`: that's deliberate — it means `OPENROUTER_API_KEY` or `LIVE_MODEL` wasn't set. Leave `RUN_LIVE = False` if you don't intend to spend credits.
- Evaluation numbers look suspiciously perfect: re-check `make_decision` — the simulated functions are deterministic stand-ins, not real model variance.

## ✅ Validation checklist

- [ ] Offline cells (Parts 1–6, 8–10) run top to bottom with no errors.
- [ ] The intentional `ValidationError` in Part 2 triggers as described.
- [ ] Both simulated configurations produce different failure *patterns*, not just different totals.
- [ ] `RUN_LIVE` defaults to `False`; no secrets are present anywhere in the notebook.
- [ ] No real customer data anywhere in the fixtures.

## Scope / limitations

This is an instructional prototype, not a production model-evaluation harness. The two
"configurations" are hand-coded deterministic functions that emulate different error
*patterns* — they are **not** real LLM calls and make no claim about any provider's actual
accuracy, latency, or price. The 12-ticket set is for teaching measurement mechanics, not
statistically meaningful evaluation. A real evaluation would need a larger, reviewed,
representative dataset; repeated trials; held-out labels; and production-grade monitoring.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
