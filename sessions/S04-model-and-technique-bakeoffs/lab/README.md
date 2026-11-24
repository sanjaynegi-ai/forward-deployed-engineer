# S04 — Northstar Technique Bake-Off Lab

**Audience:** Experienced software professionals who have done S01 and S02. **Duration:** 90-minute live session, plus optional extensions. All data is synthetic.

## 💻 Quick start

1. Open this folder in VS Code or JupyterLab.
2. Install this lab's two dependencies: `python -m pip install pandas 'pydantic>=2,<3'`
   (or run the commented `%pip install` line in the notebook's first cell). Using `uv`
   locally instead? Run `uv sync --group s04` from the repo root, then `uv run jupyter
   lab` — see `docs/TOOLING.md`.
3. Open `S04_Northstar_Technique_Bakeoff_Lab.ipynb` and run the cells **top to bottom** —
   later cells depend on the ticket set, accounts, and functions defined earlier.
4. No API key, network access, or paid account is required for the core path. The
   optional live-model section (Part 7) is off by default (`RUN_LIVE = False`).

## 🧩 Concept map

- **Same task, two techniques:** a single structured call (S02's technique) and a
  verified agent loop with a lookup tool (S01's technique), run on the exact same 12
  labeled tickets and the exact same output contract.
- **Measured, not assumed:** accuracy, illustrative cost, and illustrative latency for
  each technique, side by side — not accuracy alone.
- **Tiered dispatch:** a confidence-gated router that keeps the cheap technique's answer
  when a signal says it can be trusted, and escalates to the expensive technique
  otherwise.
- **The actual lesson:** a more capable technique winning on accuracy does not, by
  itself, make it the right default — and a routing signal that looks clean on a small
  trial still needs its own validation before anyone trusts it in production.

> [!NOTE]
> This lab does not re-teach S01's harness/authorization mechanics or S02's contract
> validation — both are assumed working and reused as-is. If either is unfamiliar, do
> that session's lab first.

## 🛠️ Checkpoints / exercises

**Part 1 — Data:** Load the 12 synthetic Northstar tickets and their reference decisions.
Before running anything else, guess which six you think are self-contained and which six
need an account lookup, just from reading the ticket text.

**Part 2 — Technique 1 (single call):** Run the mock single-call technique over all 12
tickets. Confirm it gets all six self-contained tickets right and all six lookup-needed
tickets wrong.

**Part 3 — Technique 2 (agent loop):** Run the mock agent technique, which always calls
`lookup_account` before deciding. Confirm it gets all 12 right, and note its illustrative
cost and latency versus Technique 1's.

**Part 4 — Head to head:** Build the comparison table. Before looking at the numbers,
predict which technique wins on accuracy and which wins on cost — then check whether a
single technique wins on *both*.

**Part 5 — Tiered dispatch:** Run the confidence-gated router. Confirm it matches
Technique 2's accuracy while costing less, and inspect which six tickets it actually
escalated.

**Mini exercise (Part 5):** Add a 13th ticket deliberately designed to fool the
confidence heuristic — either a self-contained ticket that happens to contain one of the
heuristic's trigger words, or a lookup-needed ticket that avoids all of them. Confirm
tiered dispatch mis-routes it, and identify which of the two failure directions (§7 of
the handout) you triggered.

**Part 6 — FDE decision exercise:** Write the recommendation-plus-validation-plan for
Northstar's VP of Support. This is the same skill tested in the quiz's Q8 and the
interview bank's Q10 — practice it here first.

## 💻 Optional live model mode (requires credentials and provider validation)

1. Install `openai`: `python -m pip install openai` (or `uv sync --group live` from the
   repo root).
2. Set `OPENROUTER_API_KEY` in your shell environment. Never commit it or paste it into
   the notebook.
3. In Part 7, set `RUN_LIVE = True` and `LIVE_MODEL` to a verified OpenRouter model ID.

This optional section runs **Technique 1 only** — a real single structured call — against
a real model, and compares it to the mock Technique 2's numbers. A real tool-using agent
comparison needs a framework or hand-rolled harness wired to a live model; S01's lab
already has one built and tested — this lab doesn't duplicate it live.

> [!CAUTION]
> Only ever paste synthetic or illustrative data into a live prompt here, never real
> customer data. This path has not been executed as part of building this lab — review
> the provider's current structured-output support, data-retention terms, and pricing
> before running it live.

## 🔍 Troubleshooting

- `pandas`/`pydantic` import error: re-run the install command for your environment/kernel.
- Tiered dispatch's numbers look identical to Technique 2's: confirm the confidence
  heuristic is actually returning `False` for at least some tickets — an all-`True`
  confidence result silently degrades tiered dispatch into "always Technique 1."
- Mini-exercise ticket doesn't trigger a misroute: check it doesn't accidentally use a
  different trigger keyword than the one you intended, or that it isn't a near-duplicate
  of an existing ticket's wording.
- Live section raises `RuntimeError`: that's deliberate — it means `OPENROUTER_API_KEY`
  or `LIVE_MODEL` wasn't set. Leave `RUN_LIVE = False` if you don't intend to spend
  credits.

## ✅ Validation checklist

- [ ] Technique 1 gets exactly the six self-contained tickets right, no more.
- [ ] Technique 2 gets all 12 tickets right.
- [ ] Tiered dispatch matches Technique 2's accuracy at lower illustrative cost.
- [ ] The mini-exercise ticket demonstrably triggers one of the two misroute directions.
- [ ] `RUN_LIVE` defaults to `False`; no secrets anywhere in the notebook.
- [ ] No real customer data anywhere in the notebook or its outputs.

## Scope / limitations

This is an instructional prototype, not a production dispatch system. Both techniques'
"decisions" are hand-coded deterministic functions built to demonstrate a specific
capability/cost trade-off — they are **not** real LLM calls on the mock path and make no
claim about any provider's actual accuracy. The confidence heuristic's clean separation
on these 12 tickets is a deliberate teaching construction, not evidence about how a real
confidence signal behaves on real traffic — see the handout's §5 caution and the FDE
decision exercise's validation-plan requirement before generalizing from it. The
illustrative cost/latency multipliers (1 unit/1.0s for Technique 1, 3 units/3.0s for
Technique 2) are this lab's own invented stand-ins, not measured figures from any real
framework or provider.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
