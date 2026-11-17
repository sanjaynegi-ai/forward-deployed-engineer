# S03 — LLM Fundamentals Lab

**Audience:** Experienced software professionals, including learners new to AI/ML.
**Duration:** 90-minute required path, plus optional extensions. **Environment:** Google
Colab (GPU optional, CPU works) or local Jupyter with the same packages.

## 💻 Quick start

1. Open `S03_LLM_Fundamentals_Lab.ipynb` in Colab or JupyterLab.
2. Run the setup cells (§0) — this installs `transformers`, `accelerate`,
   `python-dotenv`, and `openai`, and downloads the small teaching model
   (`HuggingFaceTB/SmolLM2-135M-Instruct`, ~135M parameters) on first run.
3. Run the notebook **top to bottom** through §9 — later cells depend on the tokenizer,
   model, and variables defined earlier. No API key, network access beyond the one-time
   model download, or paid account is required for the required path.
4. Sections and cells marked **(optional)** can be skipped without breaking anything
   downstream in the required path — they're self-contained extensions, not
   prerequisites.

> [!CAUTION]
> Never put a real API key in a shared or committed notebook. The `.env`-upload cell in
> §0 and the hosted-provider section (§8b) are both off by default and only needed if
> you intend to run the optional live-provider comparison.

## 🧩 Concept map

- **Tokens and tokenization:** a tokenizer converts text ⇄ token IDs; it is not the
  language model.
- **The full request/response path:** chat formatting → tokenizer → embedding lookup →
  transformer → logits → selection → decode → delivery, one real local demo per stage.
- **The manual next-token generation loop (§5b):** the session's central demonstration —
  watch, by hand, exactly what `model.generate(...)` normally hides.
- **Generation loop vs. agent loop:** this notebook's loop runs *inside one model
  response*; an agent loop (S01) makes multiple independent model requests with tool
  execution between them. The notebook states this distinction twice on purpose.
- **Context window, streaming, and the three-layer (LLM / inference runtime / provider
  API) separation:** each gets its own real demo, tied explicitly back to S02's existing
  caution about attaching too much context and S02's own three-layer diagram.
- **The Northstar FDE decision (§9):** a token/cost-budget note, using the same
  cost-estimation pattern S02's lab already uses.

> [!NOTE]
> This lab does not build a tool-using agent or a retrieval pipeline — there is no
> model-directed action selection and no document retrieval here. If you want the agent
> mechanism, see the **S01** lab (`../../S01-verified-agent-loops/lab/`); a future Context
> Engineering and RAG session will cover retrieval.

## 🛠️ Checkpoints / exercises

**§1 — Tokens:** Run the tokenizer examples. Before reading the output, predict which
example costs the most tokens relative to its visible length, and why.

**§2 — Loading the LLM:** Run the chat-template cell. Confirm out loud (or in your own
notes) that what's printed is *not* what you typed as `user_question`.

**§3 — Embeddings:** Run the embedding-shape inspection. State, before revealing the
answer in the markdown, whether the embedding tensor holds one vector for the whole
prompt or one per token.

**§4 — Logits:** Run the top-8-candidates cell. Pick one candidate that looks like a word
fragment rather than a clean English word, and explain why that's expected, not a bug.

**§5b — The critical demonstration:** Before running the manual generation loop, answer
the notebook's posed question: what would happen if this loop had no stop condition? Then
run it and watch at least four of the printed steps as they appear, not just the final
text.

**§6 — Context window:** Run the token-growth comparison. State, in your own words, where
"memory" across separate API calls actually has to live.

**§9 — FDE decision (take-home):** Run the cost-estimation cell, then actually write the
one-page note in the blank markdown cell before you consider the session done — don't let
this become homework you never start.

## 💻 Optional extensions (not required for the 90-minute path)

- **§1:** the `tiktoken` cross-tokenizer comparison.
- **§3:** the "same token ID → same initial embedding" nuance demo.
- **§4:** the softmax conceptual note.
- **§7:** the TTFT/TPOT vocabulary note (precise measurement is out of scope).
- **§8b — hosted-provider comparison:** requires `OPENAI_API_KEY` and/or
  `OPENROUTER_API_KEY` set as environment variables (never pasted into the notebook).
  Skips gracefully with a printed message if no keys are present. Only ever use synthetic
  prompts here — never real customer data.
- **End-of-notebook optional self-study activities:** five additional exercises for
  learners who want more practice beyond the required checkpoints above.
- **Companion notebook:** `../notebooks/LLM_Engineering_Decisions.ipynb` — four applied
  labs (token exploration, token economics, context-window budgeting, and the streaming
  decision) built on Northstar's 50,000-ticket/day workload. No fixed timebox; see
  `docs/curriculum/token-economics-instructor-guide.md` for suggested pacing if run live.
- **Standalone exercise sheet:** `../token-economics-exercises.md` — the same four labs'
  questions and answer key on paper, for review or interview prep without running the
  notebook.

## 🔍 Troubleshooting

- `transformers`/`accelerate` import error: re-run the `%pip install` cell for your
  environment/kernel.
- Model download is slow or stalls: this is a ~135M-parameter model (a few hundred MB) —
  expected on a slow connection; it only downloads once per environment/session.
- CPU runtime feels slow during generation: expected — the manual loop (§5b) and the
  sampling comparisons (§5c) are the slowest cells; a GPU runtime speeds them up but
  isn't required.
- §8b raises no error but prints "No provider keys found": that's deliberate — it means
  `OPENAI_API_KEY`/`OPENROUTER_API_KEY` weren't set. Leave them unset if you don't intend
  to run this optional section.
- Variables from an earlier section seem undefined: confirm you ran the notebook top to
  bottom — later cells (especially §9) reuse variables (`short_chat`, `long_chat`,
  `tokenizer`, `model`) defined in earlier required sections.

## ✅ Validation checklist

- [ ] Required-path cells (§0–§10) run top to bottom with no errors on both CPU and GPU
      runtimes.
- [ ] The manual generation loop (§5b) prints all 12 steps and a non-empty final string.
- [ ] The streaming cell (§7) visibly displays text progressively, not all at once.
- [ ] §8b's cells skip gracefully (no stack trace) when no provider keys are present.
- [ ] No secrets are present anywhere in the notebook; `UPLOAD_ENV` and `RUN_LIVE`-style
      gates default to off.
- [ ] No real customer data anywhere in the notebook or its outputs.

## Scope / limitations

This is an instructional prototype for teaching mechanism, not a production inference
pipeline. `HuggingFaceTB/SmolLM2-135M-Instruct` is a small teaching model chosen for cost
and speed, not for response quality — its general-knowledge answers (e.g., in §5a) may be
wrong, and that's expected; the point is watching the mechanism, not grading the model. Do
not generalize this model's specific behavior to any production-scale model (see the
interview-prep's Q9 for exactly why). The §9 cost exercise uses illustrative token-rate
figures, not any specific provider's current pricing — verify real rates before using
this pattern to make an actual customer recommendation.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
