# S05 — Northstar Deployment and Context Bake-Off Lab

**Audience:** Experienced software professionals who have done S02 and S03. **Duration:** 90-minute live session, plus optional extensions. All data is synthetic.

## 💻 Quick start

Environment setup (dependencies, kernel selection) is a one-time step done once at the
**repo root**, not per lab — see the root `README.md` / `docs/TOOLING.md`. Once that's
done:

1. Open `S05_Northstar_Deployment_Context_Lab.ipynb` and run the cells **top to
   bottom** — later cells depend on the knowledge base, ticket set, and functions
   defined earlier.
2. No API key, network access, or paid account is required for the core path (the
   tokenizer runs fully offline). The optional live-model section (Part D) is off by
   default (`RUN_LIVE = False`).

## 🧩 Concept map

- **Open-weight vs. closed-weight:** a deployment-location fact, not an accuracy fact —
  only open-weight models can be run entirely on your own or a customer's hardware.
- **Hosted vs. local:** the same open-weight model should score identically on accuracy
  either way; cost, latency, and memory are what actually change.
- **Context trimming, measured with a real tokenizer:** sending only the knowledge-base
  section a ticket actually needs, using a cheap, already-available routing hint — the
  same cheap-signal idea S04's tiered dispatch used, applied to context instead of
  technique.
- **The surprising result:** trimming context in this lab doesn't just cut cost — it
  also removes the specific unrelated text that was causing one ticket to be
  misclassified, so accuracy goes *up*, not just down in cost.

> [!NOTE]
> This lab does not build a tool-using agent (S01) or compare single-call against
> agent-loop techniques (S04) — every run here is a single structured call. Only the
> model, where it runs, and the context it receives change.

## 🛠️ Checkpoints / exercises

**Part 1 — The knowledge base and ticket set:** Load Northstar's general rules and four
category sections, and the 10 labeled tickets. Before running anything, read the access
section's "repeated 401 errors" rule and predict which ticket (if any) it might wrongly
apply to.

**Part A — Model/deployment comparison (full context, fixed):** Run all three
configurations (closed-hosted, open-hosted, open-local) on the same 10 tickets with full
context. Confirm the two open-weight rows score identically, and identify the one
ticket only the closed model gets right.

**Part B — Context comparison (open-hosted, fixed):** Run the open-hosted configuration
once with full context and once with trimmed context. Confirm the trimmed run uses
roughly half the tokens — and scores *higher*, not just cheaper.

**Mini exercise (Part B):** Find which ticket's accuracy changed between full and
trimmed context, and explain the mechanism in your own words before reading the
handout's §5 explanation.

**Learner modification:** Add a new knowledge-base section (e.g., "Security") with its
own trigger phrase, and a ticket designed to be mis-routed by it under full context the
same way the existing "401" ticket is. Confirm trimming fixes your new case too.

**Part C — FDE decision exercise:** Write the constraint-first recommendation for the
data-residency scenario. This is the same skill tested in the quiz's Q8 and the
interview bank's Q10 — practice it here first.

## 💻 Optional live model mode (requires credentials and provider validation)

1. Copy the repo root's `.env.example` to `.env` and set `OPENROUTER_API_KEY` there — the
   notebook's live cell calls `load_dotenv()`, which finds it automatically. Never commit
   `.env` or paste a key into the notebook.
2. In Part D, set `RUN_LIVE = True` and `LIVE_MODEL` to a verified OpenRouter model ID.

This section sends the **real** full and trimmed prompts to a real model and compares
real token counts and timing against the mock numbers above. It does not attempt to
compare a real hosted deployment against a real local one — running an open-weight
model locally is out of scope for this optional section; the mock `open_local`
configuration's numbers stand in for it.

> [!CAUTION]
> Only ever send synthetic or illustrative data to a live model, never real customer
> data. This path has not been executed as part of building this lab — review the
> provider's current structured-output support, data-retention terms, and pricing
> before running it live.

## 🔍 Troubleshooting

- `tiktoken`/`pandas`/`pydantic` import error: re-run the install command for your
  environment/kernel.
- Trimmed and full context report the same token count: check that `topic_hint` is
  actually narrowing `sections_included` to one category, not accidentally including
  every section.
- The two open-weight rows don't match in Part A: check that both configurations use
  `capability="open"` — only `capability="closed"` should change the mock decision
  logic.
- Live section raises `RuntimeError`: that's deliberate — it means `OPENROUTER_API_KEY`
  or `LIVE_MODEL` wasn't set. Leave `RUN_LIVE = False` if you don't intend to spend
  credits.

## ✅ Validation checklist

- [ ] The two open-weight configurations score identically in Part A.
- [ ] Trimmed context in Part B uses roughly half the tokens of full context.
- [ ] Trimmed context's accuracy is at least as high as full context's, with the
      specific fixed ticket identified.
- [ ] `RUN_LIVE` defaults to `False`; no secrets anywhere in the notebook.
- [ ] No real customer data anywhere in the notebook or its outputs.

## Scope / limitations

This is an instructional prototype, not a production deployment comparison. The mock
decision logic is hand-coded to demonstrate two specific, designed failure modes (a
capability-limited cross-reference error and a context-dilution error) — it is **not** a
real model on the mock path and makes no claim about any provider's or open-weight
model's actual accuracy. The illustrative cost-per-1,000-token and seconds-per-1,000-
token figures for each configuration are this lab's own invented stand-ins, not measured
figures from any real provider, framework, or hardware — only the **token counts**
themselves are real, computed with `tiktoken` against this lab's own knowledge-base
text. The topic hint used for trimming is assumed accurate for every ticket in this
curated set; a real intake-form hint needs its own validation, per the handout's §5 note
and the quiz's Q7.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
