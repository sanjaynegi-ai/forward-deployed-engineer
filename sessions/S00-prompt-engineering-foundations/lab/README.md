# S00 — Prompt Engineering Foundations Lab

**Audience:** Experienced software professionals, including learners new to Python. **Duration:** 90-minute live session, plus optional extensions. All data is synthetic or a public illustrative sample — see **Scope / limitations**.

## 💻 Quick start

1. Open this folder in VS Code or JupyterLab.
2. Install the one dependency this lab needs: `python -m pip install pandas` (or run the
   commented `%pip install` line in the notebook's first cell). Using `uv` locally instead?
   Run `uv sync --group s00` from the repo root, then `uv run jupyter lab` — see
   `docs/TOOLING.md`.
3. Open `S00_Northstar_Prompt_Patterns_Lab.ipynb` and run the cells **top to bottom** — later cells depend on data and functions defined earlier.
4. No API key, network access, or paid account is required for the core path. The optional live-model section (Part 6) is off by default (`RUN_LIVE = False`).

## 🧩 Concept map

- **A prompt as a specification:** the gap a pattern closes, named before the pattern is applied — not phrasing for its own sake.
- **Naive vs. few-shot comparison:** two deterministic, offline stand-in classifiers simulate "no pattern" and "few-shot pattern" sentiment classification on the same hand-labeled comments, so you see *which specific comments* each one gets wrong, not just an accuracy number.
- **Semantic Filter + Recipe:** grouping free-text feedback by meaning into themes a support lead can act on.
- **Chain-of-Thought and Meta Prompt + Role + Structure:** turning real, computed churn statistics into a stakeholder-ready narrative — the prompting is something *you* draft; the notebook computes the numbers it needs to be about.

> [!NOTE]
> This lab does not build a tool-using agent or a typed output contract — there is no
> model-directed action selection or Pydantic validation here. If you want those
> mechanisms, see the **S01** lab (`../../S01-verified-agent-loops/lab/`) and the **S02**
> lab (`../../S02-structured-outputs-and-model-selection/lab/`).

## 🛠️ Checkpoints / exercises

**Part 1 — Data:** Load `data/user_comments.csv` (100 rows, ~28 unique phrasings) and
`data/churn_modelling.csv` (10,000 synthetic-style bank customer records). Skim both before
running anything else.

**Part 2 — Naive vs. few-shot:** Run both mock classifiers against the 28-item hand-labeled
gold set. Before looking at the printed mismatch table, predict which comments will trip up
the naive classifier — negation and hedging are the pattern to watch for.

**Part 3 — Semantic Filter:** Run the theme-assignment function over the negative-labeled
comments. Confirm by hand that at least one comment is grouped correctly by *meaning* even
though it shares no keyword with its theme name.

**Part 4 — Churn EDA:** Compute churn rate overall, by geography, by active-member status,
and by product count. These numbers are real `pandas` arithmetic on the provided CSV — not
simulated.

**Mini exercise (Part 2):** Add one new comment of your own, written to defeat the naive
classifier's keyword rule (use a negation or a hedge). Confirm it does.

**Learner modification (Part 4):** Add one more cut of the churn data (e.g., by credit
score band) and decide whether it changes which finding you'd lead with in a stakeholder
note.

**Part 6 — FDE decision exercise:** Write the 3–5 sentence stakeholder note for Northstar's
VP of Support. This is the same skill tested in the quiz's Q13 and the interview bank's
Q13 — practice it here first.

## 💻 Optional live model mode (requires credentials and provider validation)

1. Install `openai`: `python -m pip install openai` (or `uv sync --group live` from the
   repo root).
2. Set `OPENROUTER_API_KEY` in your shell environment. Never commit it or paste it into the notebook.
3. In Part 5, set `RUN_LIVE = True` and `LIVE_MODEL` to a verified OpenRouter model ID.
4. Paste in one of the patterned prompts you drafted in Part 4 or 5 and compare its real
   output against your own prediction.

> [!CAUTION]
> Only ever paste synthetic or illustrative data into a live prompt here, never real
> customer data. This path has not been executed as part of building this lab — review the
> provider's current structured-output support, data-retention terms, and pricing before
> running it live.

## 🔍 Troubleshooting

- `pandas` import error: re-run the install command for your environment/kernel.
- Gold-set comparison numbers look different from the README's description: confirm you
  didn't edit the gold-label dictionary before running Part 2's first pass.
- Live section raises `RuntimeError`: that's deliberate — it means `OPENROUTER_API_KEY` or
  `LIVE_MODEL` wasn't set. Leave `RUN_LIVE = False` if you don't intend to spend credits.
- Naive classifier "accidentally" gets a negated comment right: check which keyword it
  matched — some negated comments still contain a strong negative word elsewhere and get
  the right label for the wrong reason. The mismatch table, not the accuracy number, is
  where this shows up.

## ✅ Validation checklist

- [ ] Offline cells (Parts 1–4, 6) run top to bottom with no errors.
- [ ] The naive classifier visibly mislabels at least the negation/hedge cases described in the handout.
- [ ] Churn-rate figures are computed from `data/churn_modelling.csv`, not hardcoded.
- [ ] `RUN_LIVE` defaults to `False`; no secrets are present anywhere in the notebook.
- [ ] No real customer data anywhere in the notebook or its outputs.

## Scope / limitations

This is an instructional prototype, not a production sentiment pipeline or churn model.
The "naive" and "few-shot" classifiers are hand-coded deterministic lookups that emulate
the *kind* of errors each prompting approach tends to produce — they are **not** real LLM
calls and make no claim about any provider's actual accuracy. The 28-item gold set is a
small, single-rater, repetition-heavy sample built for teaching the evaluation mechanics,
not a statistically meaningful benchmark (see the quiz's Q11 for exactly why). The churn
dataset is a widely used public, synthetic-style bank-customer sample — `CustomerId` and
`Surname` values are not real identities, and it is used here purely as a stand-in for
Northstar's fictional data, not as Northstar's real records. A real churn or sentiment
analysis would need a larger, reviewed, representative dataset and production-grade
monitoring.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
