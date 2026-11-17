# S03 Learner Quiz — LLM Fundamentals

**AI-Focused Forward Deployed Engineering · Session 03**
**Scenario:** generic model mechanics (SmolLM2-135M-Instruct demonstrations); one
Northstar-framed question in Section 3

## Purpose and administration

This assessment checks whether you can explain tokenization and token IDs, trace a
prompt through inference, reason about embeddings/logits/token selection at an intuitive
level, distinguish inference from training, reason about context windows and streaming,
and connect each of those to an engineering or customer-facing decision.

- **Suggested time:** 25–30 minutes, answering each question before opening its answer.
- **Total:** 54 points, 13 questions. Partial credit is permitted where specified.
- **Primary competency:** C1 (AI Engineering Fundamentals). **Secondary:** C2 (AI
  Solution Architecture), C4 (Evaluation, Reliability & Security), C5 (Deployment &
  Operations), C6 (Customer-Facing Technical Delivery).
- **Assumptions:** This quiz does not require a GPU, API keys, or running any cell
  yourself — code questions ask you to predict or explain behavior. Agent loops (S01) and
  typed output contracts (S02) are **not** in scope here, except where a question
  explicitly asks you to recognize that boundary.
- **How to take it:** Answer each question yourself before expanding its **Answer**
  section. The answers are collapsed by default specifically so you can self-test one
  question at a time without losing your place.

---

## Section 1 — Concepts (Q1–Q5)

### Q1. Tokenizer vs. LLM (2 points)
**Difficulty:** Foundational · **Competency:** C1 · **Type:** Multiple choice

Which statement is correct?

A. A tokenizer is a small LLM specialized for text splitting.
B. A tokenizer converts text to token IDs and back; it has no trained weights for
   predicting anything.
C. Loading a tokenizer is sufficient to generate a response.
D. The tokenizer and the embedding layer are the same component.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** B (2 points)

**Explanation:** A tokenizer is a text-processing algorithm plus a learned vocabulary — it
converts text ⇄ token IDs. It is not a language model and cannot generate anything on its
own.

**Misconception:** Treating "tokenizer" and "language model" as interchangeable because
both involve "tokens."

</details>

### Q2. Predict the token count (3 points)
**Difficulty:** Foundational · **Competency:** C1 · **Type:** Short answer

Two strings are tokenized by the same model: `"cats"` and `"Python is fun 🐍"`. Which one
is more likely to use *more* tokens per visible character, and why?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** The emoji string (3 points)

**Explanation:** Common words like "cats" are likely covered by a single vocabulary
entry; an emoji and the specific word combination are less common in the tokenizer's
training data and are more likely to be split into multiple smaller tokens (or
multi-byte encodings), costing more tokens for the same number of visible characters.

**Misconception:** Assuming token count scales directly and uniformly with character
count or word count, regardless of content.

</details>

### Q3. Match the stage to what it produces (4 points)
**Difficulty:** Foundational · **Competency:** C1 · **Type:** Matching

Match each stage to what it actually produces: **token IDs**, **embedding vectors**,
**logits**, or **generated text**.

| Stage | Produces |
|---|---|
| a. Tokenizer encoding | |
| b. Embedding lookup | |
| c. Output projection (after transformer layers) | |
| d. Tokenizer decoding | |

<details>
<summary><strong>Answer</strong></summary>

**Answer:** a: token IDs; b: embedding vectors; c: logits; d: generated text (4 points)

**Explanation:** Encoding turns text into integer IDs; the embedding layer turns each ID
into a vector; the output projection turns transformer-processed vectors into a score
(logit) per vocabulary entry; decoding turns a chosen ID back into readable text.

**Misconception:** Collapsing "embedding vectors" and "logits" into the same idea because
both are "numbers the model produces."

</details>

### Q4. Is output the reverse of input? (3 points)
**Difficulty:** Intermediate · **Competency:** C1 · **Type:** True/false + explain

True or false: generating a response is the input pipeline run in reverse (vector →
original token ID, repeated). Justify your answer in one sentence.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** False (3 points)

**Explanation:** The model does not reverse the embedding lookup to recover an input ID —
it produces **new** logits over the whole vocabulary and selects a **new** next token ID.
Only tokenizer decoding (ID → text) is roughly the inverse of tokenizer encoding
(text → ID); the full generation process is not an inverse of the full input pipeline.

**Misconception:** Assuming "decoding reverses encoding" implies "the whole response
reverses the whole input process."

</details>

### Q5. Context window, correctly stated (2 points)
**Difficulty:** Foundational · **Competency:** C1, C5 · **Type:** Multiple choice

Which claim about a context window is correct?

A. It's a persistent memory the model keeps across separate API calls.
B. It's the maximum number of tokens the model can account for in one request, including
   instructions, history, and the room needed for output.
C. It only limits output length, not input length.
D. A larger context window guarantees better answers.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** B (2 points)

**Explanation:** The context window is a token budget for a single request — input and
output share it. Nothing persists between separate calls unless the application re-sends
it.

**Misconception:** Treating a large advertised context window as free, unlimited, or
automatically beneficial memory.

</details>

## Section 2 — Trace and code reasoning (Q6–Q9)

### Q6. Trace the manual loop (4 points)
**Difficulty:** Intermediate · **Competency:** C1, C4 · **Type:** Code reasoning

```python
for step in range(12):
    next_logits = model(current_ids).logits[:, -1, :]
    next_id = torch.argmax(next_logits, dim=-1, keepdim=True)
    current_ids = torch.cat([current_ids, next_id], dim=-1)
```

How many new tokens does this produce, and what determines **which** token gets picked
at each step? Name one optimization a real inference engine applies that this snippet
deliberately skips.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** 12 tokens; highest-scoring logit each step; KV caching skipped (4 points)

**Explanation:** The loop runs exactly 12 iterations, appending one token per iteration.
`torch.argmax` always picks the single highest-scoring next token (greedy decoding) —
deterministic given the same input. Real inference engines cache earlier computations
(the KV cache) instead of reprocessing the entire growing prefix every step, which this
snippet skips for clarity.

**Rubric:** 1 for count, 2 for the selection mechanism, 1 for a named optimization
(KV cache, batching, or similar).

</details>

### Q7. What stops this loop from running forever? (4 points)
**Difficulty:** Intermediate · **Competency:** C1, C4 · **Type:** Debugging

A teammate removes the `range(12)` bound and replaces it with `while True`, planning to
rely on the model eventually producing an end-of-sequence token. Identify **two** risks
with this change.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** No hard bound; no handling if end-of-sequence never appears (4 points)

**Explanation:** (1) Removing the explicit iteration bound means a model that doesn't
produce (or isn't checked for) an end-of-sequence token can run unbounded, consuming time
and compute with no ceiling. (2) Even checking for end-of-sequence requires explicit
stopping-criteria logic that this snippet doesn't have — relying on "eventually" with no
enforced maximum is the same category of risk **S01** flags for an unbounded agent loop,
applied here to the inner generation loop instead.

**Misconception:** Assuming a model will "naturally" stop without an enforced bound,
the same way a learner might assume an agent loop self-limits without an explicit step
budget.

</details>

### Q8. Streaming — predict the behavior (3 points)
**Difficulty:** Foundational · **Competency:** C1 · **Type:** Short answer

A non-streaming call and a streaming call generate the same response to the same prompt
with the same settings. Will the **total number of tokens generated** differ between the
two? Will **when the client sees text** differ?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Token count: no; visibility timing: yes (3 points)

**Explanation:** Both modes run the identical underlying next-token generation process —
the number of tokens generated doesn't change. What changes is delivery: non-streaming
waits for the full result before returning anything; streaming sends chunks as they
become available.

**Misconception:** Believing streaming makes the model "faster" or changes how much
compute generation takes.

</details>

### Q9. Greedy vs. sampling across reruns (3 points)
**Difficulty:** Intermediate · **Competency:** C1 · **Type:** Short answer

You run the same prompt three times with `do_sample=False`, then three times with
`do_sample=True` at a fixed temperature. Which set of three outputs should be identical to
each other, and which set may differ? Why?

<details>
<summary><strong>Answer</strong></summary>

**Answer:** Greedy set identical; sampled set may differ (3 points)

**Explanation:** Greedy decoding always selects the single highest-scoring token at each
step, so repeated runs on identical input produce identical output. Sampling draws
randomly from a (temperature-adjusted) probability distribution, so repeated runs can
legitimately produce different text even with everything else held constant.

**Misconception:** Expecting any "AI" call to be inherently non-deterministic, without
distinguishing the decoding strategy that actually causes (or prevents) that variation.

</details>

## Section 3 — Evaluation and FDE judgment (Q10–Q13)

### Q10. Is a generated rationale evidence of the real decision? (6 points)
**Difficulty:** Advanced · **Competency:** C4 · **Type:** Judgment

A model classifies a ticket as `priority: low` and generates the text: *"I chose low
priority because the customer's tone is calm and no deadline is mentioned."* Is that
sentence reliable evidence of the actual computation that produced `priority: low`?
Justify your answer using what §4's logits demonstration actually showed.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** No, not reliable evidence of internal computation (6 points)

**Explanation:** That sentence was generated by the exact same next-token-prediction
mechanism as the classification itself — scores over a vocabulary, one token at a time.
It is a plausible-sounding **output**, not a readout of the model's actual internal
state. It should be evaluated the same way any other generated text is (does it hold up
against evidence, is it consistent, is it correct) — never trusted as a faithful trace of
*why* the model produced its answer.

**Misconception:** Treating a model's stated reasoning as inherently more trustworthy
than its stated conclusion, when both come from the same mechanism.

</details>

### Q11. Generation loop or agent loop? (6 points)
**Difficulty:** Advanced · **Competency:** C1, C3 (preview) · **Type:** Architecture judgment

A system calls a model once, receives a tool request, executes the tool in application
code, and sends a second model request that includes the tool's result. Is the
"loop" connecting these two model requests the same kind of loop you traced in §5's manual
next-token demonstration? Explain the distinction and name the session that covers the
mechanism this scenario actually needs.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** No — this is an agent loop, not a generation loop; S01's mechanism (6 points)

**Explanation:** §5's loop is next-token iterations **inside one model response**. This
scenario makes **two separate model requests**, with application-executed tool use and
authorization between them — that's an agent loop, the subject of **S01: Verified Agent
Loops**, which also covers the harness and verification mechanics this scenario would
need (tool authorization, bounded retries, escalation). Each of the two model requests in
this scenario may itself contain a full next-token generation loop internally — the two
concepts nest, they don't substitute for each other.

**Misconception:** Describing any repeated model involvement as "the same loop," rather
than distinguishing the loop's actual scope (inside one response vs. across requests).

</details>

### Q12. Calculate the cost difference (6 points)
**Difficulty:** Intermediate · **Competency:** C2, C5 · **Type:** Numerical interpretation

Classifying a ticket with just its text costs 180 input tokens; classifying the same
ticket with the full prior conversation attached costs 640 input tokens. Both calls
generate 60 output tokens. Using $1.00 per million input tokens and $4.00 per million
output tokens, calculate the per-call cost for each, and the projected difference across
10,000 tickets.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** $0.00042 vs. $0.00088 per call; ~$4.60 difference per 10,000 tickets (6 points)

**Explanation:** `(180 × 1.00 + 60 × 4.00) / 1,000,000 = $0.00042`;
`(640 × 1.00 + 60 × 4.00) / 1,000,000 = $0.00088`. Difference per call ≈ $0.00046;
across 10,000 tickets ≈ **$4.60**. On its own this may look small — the point is that it
scales linearly with volume and with how much history gets attached, and a support team
submitting dozens of related tickets a day compounds it further than this single pair
suggests.

**Rubric:** 2 points per correct per-call calculation; 2 points for the scaled
difference.

</details>

### Q13. Northstar customer-facing recommendation (8 points)
**Difficulty:** Advanced · **Competency:** C6, C2 · **Type:** Communication

Write the 3–5 sentence note you'd send Northstar's support lead after confirming the
pattern from Q12. Include the headline finding, a concrete context-size policy
recommendation, and the one trade-off your policy accepts.

<details>
<summary><strong>Answer</strong></summary>

**Example strong answer (8 points):**

"We confirmed that classification cost scales directly with how much conversation history
gets attached to each request — agents who paste in the full prior thread are paying for
every one of those extra tokens on every call, not because the task is harder, but because
token count drives cost regardless of what's actually relevant. I'd recommend capping
attached history to the current ticket plus the last two exchanges, which should cut
average input tokens meaningfully without losing the context that matters for most
tickets. The trade-off: on the rare ticket where something from four exchanges ago is
actually load-bearing, the model won't see it — we'd want a way for an agent to flag and
manually re-attach that older context when it's genuinely needed."

**Grading:** 3 points for a plainly stated headline finding; 3 points for a concrete,
specific policy (not "use less context" unqualified); 2 points for naming a real trade-off
rather than implying the policy is free.

**Misconception:** Recommending "always use less context" without naming what might be
lost, or recommending "always attach everything" because the model's context window is
technically large enough to fit it.

</details>

---

## Submission checklist

- [ ] I distinguished "the tokenizer did X" from "the model did X" throughout, not just
      in Q1.
- [ ] I correctly separated the generation loop (§5, Q6/Q7) from the agent loop (S01, Q11).
- [ ] I treated a generated rationale as a string to evaluate, not as internal evidence
      (Q10).
- [ ] I showed the actual arithmetic in Q12, not just a qualitative "it costs more."
- [ ] I named a concrete trade-off in my Q13 recommendation, not just a restated finding.

## 🔍 Interpret your results

**Suggested self-assessment ranges (not certification thresholds):** 46–54 strong; 36–45
developing; 0–35 revisit relevant concepts. These are not empirically validated cut
scores.

**Diagnose by concept:**
- Q1, Q3, Q4, Q5: component boundaries and what each stage actually produces.
- Q2, Q8, Q9: predicting mechanism-driven behavior (tokens, streaming, decoding).
- Q6, Q7: tracing and hardening the generation loop itself.
- Q10, Q11: the two safety-rail distinctions this session exists to set up for S01/S02.
- Q12, Q13: turning mechanism into a measured, customer-facing recommendation.

**Coverage note:** This quiz assesses tokenization, the request/response lifecycle,
embeddings/logits at an intuitive level, context windows, and streaming — not agent
loops, harness design, or typed-output validation. Those remain **S01** and **S02**
topics respectively; this quiz tests only that you can correctly recognize the boundary
when it comes up (Q11).

> [!NOTE]
> All token counts, costs, and model behavior described in this quiz come from the
> session's own small teaching model (SmolLM2-135M-Instruct) and illustrative pricing —
> not a benchmark or claim about any specific provider's current rates.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
