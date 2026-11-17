# S03 Interview Preparation — LLM Fundamentals

**Course:** AI-Focused Forward Deployed Engineering · Session 03
**Audience:** Experienced software engineers, QA automation engineers, architects, and
technical product professionals. No prior AI/ML background is assumed.
**Scenario:** generic model-mechanics demonstrations; one Northstar-framed scenario in
Section D
**Competencies:** C1 AI Engineering Fundamentals (primary), C4 Evaluation/Reliability/
Security (secondary), C2 AI Solution Architecture (secondary), C5 Deployment & Operations
(secondary), C6 Customer-Facing Technical Delivery (secondary, scenario questions only).

## How to use this bank

These are engineering interviews, not vocabulary tests. Strong answers name the actual
mechanism (not just the term), identify what that mechanism does and doesn't guarantee,
and connect it to a concrete engineering or customer decision.

**Formats**
- **15-minute screen:** Q1, Q4, Q8, plus one follow-up from each.
- **30-minute technical interview:** Q2, Q5, Q6, Q9.
- **45-minute FDE design interview:** Q3, Q7, Q10, Q11, Q13.

**Rating rubric (per question)**

| Rating | Observable behavior |
|---|---|
| **0 — Missing** | Incorrect or irrelevant; confuses core components (tokenizer, model, API). |
| **1 — Emerging** | Correct terminology, but no real mechanism — describes behavior as "magic." |
| **2 — Competent** | Correct mechanism, with the relevant limitation named. |
| **3 — Strong** | Adds a concrete failure mode, a measurement angle, or the customer-facing implication. |

> [!NOTE]
> Agent loops, harness internals, and typed-output contracts are assessed in **S01** and
> **S02**, not here — this bank stays inside what happens during one model call.

---

## A. 🧩 Fundamentals

### Q1. Explain tokenization to a backend engineer who's never touched AI
**Difficulty:** Foundational · **Competency:** C1

**Prompt:** A teammate says, "I don't get it — doesn't the model just read my sentence?"
Explain what actually happens, and why "a tokenizer" and "an LLM" aren't the same thing.

**Expected strong answer:**
- A tokenizer converts text into integer token IDs using a fixed, trained vocabulary —
  it's a translation layer, with no capacity to predict or generate anything on its own.
- The LLM is the separate neural network that takes those IDs (via embeddings) and
  predicts scores for the next token — it never "reads" raw text directly.
- Different models can use different tokenizers, so the same sentence can cost a
  different number of tokens depending on which model is asked.

**Weak answer:** "The tokenizer breaks up words and feeds them to the AI" — true in
spirit but doesn't separate "translation" from "prediction," and implies tokens are
words.
**Probes:** Why might an emoji or an uncommon technical term cost more tokens than a
common word? What would happen if you tried to generate text using only the tokenizer?
**Evidence of mastery:** Candidate explicitly separates "converts text ⇄ IDs" from
"predicts the next ID" as two different jobs, done by two different components.
**Common misconception:** Treating "tokenizer" as a simplified synonym for "the AI."

### Q2. What are embeddings, and what are they not?
**Difficulty:** Foundational · **Competency:** C1

**Prompt:** A product manager asks, "Can we just use the model's embeddings for our
search feature?" What do you need to clarify before answering?

**Expected strong answer:**
- The embedding layer inside a generative LLM converts token IDs into vectors so the
  network has something numeric to compute with — one vector per token, looked up fresh
  for every request, not a reusable summary of a document.
- A **separate kind of embedding model**, trained specifically to produce one vector
  representing a whole sentence or document, is what search/RAG systems actually use —
  related mathematically, different job, not the same artifact this session inspects.
- Answering the PM's question requires clarifying which of the two they actually mean.

**Weak answer:** "Sure, embeddings are embeddings" — conflates the in-model lookup table
with a dedicated sentence-embedding model.
**Probes:** If you inspected the model's embedding layer directly, would you get one
vector for the whole prompt or one per token? Why does that answer rule out using it
directly for document search?
**Evidence of mastery:** Candidate names the distinction unprompted, not just when asked.
**Common misconception:** Assuming "embeddings" is one concept with one correct use case.

### Q3. What actually comes out of the model, and what should you do with it?
**Difficulty:** Intermediate · **Competency:** C1 · **Secondary:** C4

**Prompt:** Someone says, "The model told me *why* it classified the ticket as low
priority, so I trust the classification more now." Evaluate that claim.

**Expected strong answer:**
- What comes out of the model, every time, is scores (logits) over a fixed vocabulary,
  turned into probabilities, used to select one token — repeated for every generated
  token, including any "explanation" text.
- A generated rationale was produced by that exact mechanism — it is not a readout of the
  model's actual internal computation, and should be evaluated the same way any other
  generated claim is (does it hold up against evidence?), not trusted more because it
  sounds like reasoning.
- This is the same caution **S02** states about structured-output rationale fields,
  grounded here in the mechanism that makes it true.

**Weak answer:** "If it explains itself, that's more trustworthy" — the exact
misconception this question tests for.
**Probes:** If you ran the same prompt twice with sampling enabled, could the "reasoning"
text differ even if the final classification stayed the same? What would that tell you?
**Evidence of mastery:** Candidate explicitly connects "same mechanism produces both the
answer and the explanation" to "neither is more inherently trustworthy than the other."
**Common misconception:** Conflating a confident, articulate explanation with verified
correctness.

---

## B. 🧩 Mechanics in practice

### Q4. Whiteboard the token-to-text path
**Difficulty:** Foundational · **Competency:** C1

**Prompt:** Draw (or narrate) every stage a prompt passes through before you see a
response, from the text you typed to the text you read.

**Expected strong answer:** chat formatting → tokenizer encode (text → IDs) → embedding
lookup (IDs → vectors, inside the LLM) → transformer layers (contextualize the vectors) →
output projection (vectors → logits over the vocabulary) → token selection (greedy or
sampled) → repeat until a stop condition → tokenizer decode (IDs → text) → response
delivery (streamed or complete).

**Weak answer:** "Prompt goes in, AI thinks, answer comes out" — no stages named.
**Probes:** Which of these stages would a hosted API handle for you automatically? Which
one, if it failed, would look like "the model gave a bad answer" but actually wasn't the
model's fault at all?
**Evidence of mastery:** Candidate names at least six distinct stages in the correct
order, without conflating any two of them.
**Common misconception:** Treating the whole pipeline as one indivisible step.

### Q5. Diagnose an unbounded generation loop
**Difficulty:** Intermediate · **Competency:** C1, C4

**Prompt:**
```python
while True:
    next_id = pick_next_token(current_ids)
    current_ids = append(current_ids, next_id)
    if next_id == EOS_TOKEN:
        break
```
What's missing from this loop, and what would you add before shipping it?

**Expected strong answer:**
- No maximum-step/maximum-token bound — if the model never emits the expected
  end-of-sequence token (a real possibility, not just a theoretical one), this runs
  unbounded, consuming time and compute with no ceiling.
- Add an explicit `max_new_tokens`-style bound as a hard stop, independent of whether
  end-of-sequence ever appears, plus a timeout.
- Note the structural parallel to **S01**'s agent-loop step budget — same principle
  (never trust a model-controlled condition as your only stop signal), applied one layer
  lower.

**Weak answer:** "It's fine, the model will stop eventually" — the exact risk being
tested for.
**Probes:** What would you want logged if this loop hits its bound without ever seeing
end-of-sequence? Is this the same kind of unboundedness S01 worries about, or a different
one?
**Evidence of mastery:** Candidate proposes a concrete bound and explicitly names it as
independent of the model's own behavior.
**Common misconception:** Assuming a model-controlled stop condition is sufficient on its
own, without an enforced external limit.

### Q6. Streaming vs. non-streaming — predict, then explain
**Difficulty:** Foundational · **Competency:** C1

**Prompt:** A teammate says, "Switching to `stream=True` should make our classification
service faster." Is that the right expectation?

**Expected strong answer:**
- No — streaming changes when output becomes visible to the client, not how many tokens
  get generated or how much compute generation takes. Total time to the last token is
  typically unchanged (or marginally different due to overhead), not meaningfully faster.
- Streaming's actual benefit is perceived responsiveness in a UI where a human is
  watching text appear — it buys nothing for a backend call with no human watching
  partial output, like a classification service.

**Weak answer:** "Sure, streaming is basically always faster" — states the misconception
directly.
**Probes:** Would you recommend streaming for S01/S02's ticket-triage service? Why or why
not?
**Evidence of mastery:** Candidate distinguishes "faster" from "feels faster," and applies
that distinction to a concrete use case correctly (no, for a backend classifier with no
human watching).
**Common misconception:** Treating streaming as a performance optimization rather than a
delivery/UX choice.

### Q7. Greedy or sampled decoding — make the call
**Difficulty:** Intermediate · **Competency:** C1, C2

**Prompt:** You're building two things: a ticket-priority classifier, and a tool that
drafts three alternative subject lines for a marketing email. Which decoding strategy
would you pick for each, and why?

**Expected strong answer:**
- Classifier: greedy (deterministic) — the task needs a repeatable, auditable decision;
  sampling would introduce unnecessary variance into something that should be consistent
  given the same input.
- Subject-line drafting: sampling, likely with moderate temperature — the task explicitly
  wants varied options, and repeatability isn't the goal.
- The decision follows from the task's actual need for repeatability, not a default
  setting either way.

**Weak answer:** "Always use the model's default settings" — no task-specific reasoning.
**Probes:** What would you observe in production logs that would tell you you'd picked
the wrong decoding strategy for a task?
**Evidence of mastery:** Candidate ties the decoding choice explicitly to whether the
task needs determinism.
**Common misconception:** Treating temperature/sampling as a generic "creativity" dial to
raise for "better" output, independent of the task's actual requirement.

---

## C. 🔍 Evaluation and judgment

### Q8. Is a stated rationale reliable evidence?
**Difficulty:** Intermediate · **Competency:** C4

**Prompt:** A reviewer says, "This classification came with a detailed explanation, so
I'm comfortable shipping it without further review." Push back or confirm.

**Expected strong answer:**
- Push back. A generated explanation is produced by the same next-token mechanism as the
  classification itself — it's additional generated text, not an inspection of internal
  computation, and should be verified the same way any other claim would be, not trusted
  more because it sounds reasoned.
- The reviewer's actual confidence should come from independent verification (reference
  labels, business rules, human review) — exactly the verification discipline **S01**
  and **S02** both build around a model's output, applied here to the rationale text
  itself.

**Weak answer:** "If the explanation makes sense, that's good enough" — no independent
check proposed.
**Probes:** How would you test whether a model's stated rationale is faithful to its
actual decision process, if you wanted to try?
**Evidence of mastery:** Candidate proposes independent verification rather than trusting
the explanation's surface plausibility.
**Common misconception:** Equating "articulate" with "faithful" or "verified."

### Q9. "Our small test model behaved fine, so the production model will too"
**Difficulty:** Intermediate · **Competency:** C4, C2

**Prompt:** A teammate ran this session's 135M-parameter teaching model locally, saw
reasonable behavior, and concludes the same prompts will behave identically on a much
larger production model. Evaluate that inference.

**Expected strong answer:**
- Different models — even ones using similar mechanisms — have different trained weights,
  often different tokenizers/chat templates, and can behave differently on the same
  prompt. Mechanism similarity (both do next-token prediction) does not imply output
  similarity.
- The teaching model is useful for inspecting *mechanism*, explicitly not for
  benchmarking *quality* — the session itself states this distinction.
- Any production claim needs its own evaluation against the actual target model, the
  same discipline **S02** requires for comparing two model configurations.

**Weak answer:** "They're both LLMs, so behavior should transfer" — ignores that trained
weights and tokenizers differ.
**Probes:** What would you want to test on the actual production model before trusting
this pattern holds?
**Evidence of mastery:** Candidate separates "same mechanism" from "same behavior" cleanly.
**Common misconception:** Treating all autoregressive LLMs as interchangeable because
they share the same generation mechanism.

### Q10. "It worked in the demo" — generalizing a cost or latency claim
**Difficulty:** Advanced · **Competency:** C4, C5

**Prompt:** You measured that attaching full conversation history costs noticeably more
than attaching just the current ticket, on a handful of test cases. A stakeholder wants to
announce "we found a way to cut AI costs by X%." What do you say before that
announcement goes out?

**Expected strong answer:**
- The underlying mechanism (more tokens → more cost) is reliable and worth acting on —
  but the specific percentage from a handful of test cases is not yet a validated,
  representative production number.
- Recommend measuring the actual, representative distribution of ticket-history lengths
  in production before publishing a specific percentage, and state the current number as
  illustrative, not a guarantee.
- This mirrors the small-sample caution **S00/S01/S02** each apply to their own
  evaluation exercises, applied here to a cost claim instead of an accuracy claim.

**Weak answer:** "Sure, announce the number — the math is correct" — correct arithmetic
on a small sample is not the same as a validated production claim.
**Probes:** What would change your confidence in the percentage — more test cases, a
different kind of test case, or something else?
**Evidence of mastery:** Candidate distinguishes "the mechanism is real" from "this exact
number is production-validated."
**Common misconception:** Trusting correct arithmetic on a small sample as if it were a
representative measurement.

---

## D. 🗺️ Forward-deployed engineering scenarios

### S1. "Just stream everything, it'll be faster"
**Difficulty:** Advanced · **Competency:** C6, C1

**Prompt:** A Northstar stakeholder asks for streaming to be turned on everywhere,
expecting a faster system. Respond.

**Expected strong answer:**
- Agree that streaming is worth turning on **where a human is watching output appear** —
  it genuinely improves perceived responsiveness there.
- Clarify that it won't reduce total compute or backend processing time, and for a
  backend classification call with no human watching partial output (like ticket
  triage), it has no benefit worth the added complexity.
- Offer the accurate framing: "streaming changes when you see it, not how fast it's
  produced" — and apply that distinction concretely to which of Northstar's actual
  services would benefit.

**Weak answer:** Either flatly refuses without explaining why, or agrees to stream
everywhere without distinguishing use cases.
**Probes:** Which of Northstar's existing sessions' deliverables (S00's churn summary,
S01/S02's ticket triage) would plausibly benefit from streaming, if any?
**Evidence of mastery:** Candidate gives a differentiated answer by use case, not a
blanket yes or no.
**Common misconception:** Treating streaming as a universal performance lever.

### S2. "Our context window is huge — just attach the whole knowledge base"
**Difficulty:** Advanced · **Competency:** C6, C2, C5

**Prompt:** Northstar's team wants to attach their entire knowledge base to every support
ticket's classification request, since the model's advertised context window is large
enough to fit it. Respond.

**Expected strong answer:**
- Confirm the context window is a token **budget**, not free capacity — every token
  attached costs money and latency on every single call, and irrelevant material can
  actively hurt output quality by crowding out the signal that matters.
- Recommend a retrieval-based approach (fetch only the relevant article(s) per ticket)
  instead of brute-force inclusion — name this as a future session's actual subject
  (Context Engineering and RAG) rather than inventing a half-solution on the spot.
- Quantify the cost difference concretely if data is available, the same way this
  session's §9 exercise does.

**Weak answer:** Either agrees without raising the cost/relevance concern, or refuses
without offering a workable alternative.
**Probes:** What would you measure to prove attaching the whole knowledge base is
actually hurting output quality, not just raising cost?
**Evidence of mastery:** Candidate names both the cost concern and the relevance/signal
concern, and proposes retrieval as the actual fix rather than "attach less, somehow."
**Common misconception:** Treating "it fits in the context window" as equivalent to
"it's a good idea to include."

### S3. The bill spiked overnight — investigate
**Difficulty:** Advanced · **Competency:** C5, C4

**Prompt:** Northstar's model-API bill roughly tripled overnight with no announced
pricing change. Describe your investigation, grounded in what this session actually
taught you to check.

**Expected strong answer:**
- Check token volume first: did input or output token counts per call increase (longer
  conversation histories being attached, a prompt-template change, a new verbose system
  instruction), or did call *volume* increase (more tickets, a retry storm, a bug causing
  duplicate calls)?
- Check whether sampling/temperature or `max_tokens` settings changed, inflating output
  token counts.
- Check whether streaming vs. non-streaming changed in a way that affected reported usage
  accounting, and whether a prompt-caching assumption silently stopped applying.
- Reproduce on a fixed, small set of representative tickets before and after the
  suspected change, comparing token counts directly — not just the invoice total.

**Weak answer:** "Switch providers" or "ask the vendor" without first checking what
changed on Northstar's own side.
**Probes:** If token counts per call look unchanged, what's your next hypothesis?
**Evidence of mastery:** Candidate investigates token volume and call volume as two
separate, independently checkable hypotheses before escalating to the provider.
**Common misconception:** Assuming a cost spike must be a provider-side pricing or
billing error rather than checking the application's own token usage first.

### S4. "We need an agent" — before you've built one
**Difficulty:** Advanced · **Competency:** C1, C2 (preview of S01)

**Prompt:** A Northstar stakeholder, having just seen this session's manual
next-token-generation demo, says "so we already have an agent, right?" Correct the
record and explain what's actually missing.

**Expected strong answer:**
- No — what was demonstrated is a **generation loop inside one model response**. An
  agent loop is a different, outer concept: multiple independent model **requests**, with
  application-executed tool calls and authorization between them, plus a harness and
  verification policy around the whole thing.
- Name the concrete missing pieces if they actually wanted that: tool definitions,
  an authorization boundary, a step budget, and independent verification of results —
  all **S01: Verified Agent Loops**'s subject, not built in this session.
- Correct the misconception directly but constructively — it's an easy, common confusion,
  not a sign of poor judgment.

**Weak answer:** Lets the mischaracterization stand, or corrects it without explaining
what the actual missing mechanism is.
**Probes:** What's the smallest concrete change to this session's demo that would turn it
into something resembling an agent loop?
**Evidence of mastery:** Candidate names the specific missing mechanisms, not just "no,
that's different."
**Common misconception:** Assuming "the model predicted multiple tokens in sequence"
and "the system acted as an agent" are the same claim.

---

## E. ✅ Self-assessment scoring sheet

| Question | Rating (0–3) | Notes |
|---|---|---|
| Q1 |  |  |
| Q2 |  |  |
| Q3 |  |  |
| Q4 |  |  |
| Q5 |  |  |
| Q6 |  |  |
| Q7 |  |  |
| Q8 |  |  |
| Q9 |  |  |
| Q10 |  |  |
| S1 |  |  |
| S2 |  |  |
| S3 |  |  |
| S4 |  |  |

### ⚠️ Red flags that justify deeper probing

- Uses "tokenizer," "model," and "API" interchangeably without separating their jobs.
- Trusts a generated rationale as evidence of internal computation.
- Treats streaming as a performance optimization rather than a delivery choice.
- Has no stop condition in mind for a generation loop beyond "the model will know when
  to stop."
- Generalizes a small-sample cost or behavior observation into a production claim
  without flagging the sample size.
- Confuses this session's generation loop with S01's agent loop, in either direction.

> [!TIP]
> **🎤 Interview Tip:** if a candidate answers S4 by treating "the model generated
> several tokens" and "the system is an agent" as the same claim, revisit the handout's
> §2 and §5 "two uses of loop" framing before continuing your interview practice — this is
> the single most common confusion this session is written to prevent.

## 🗺️ Related learner resources

- **Handout:** Concise concept reference, including the full request/response path and
  the three-layer diagram.
- **Quiz:** A 13-question, 54-point formative assessment.
- **Lab:** `S03_LLM_Fundamentals_Lab.ipynb` — a runnable, Colab-compatible notebook with
  the manual next-token generation loop as its central demonstration, plus a
  Northstar-framed token/cost-budget exercise.

## 🛠️ Recommended learner practice

Before your next interview or review, pick one claim from this bank that you answered at
a "2 — Competent" level and push it to "3 — Strong": add the concrete failure mode or
measurement angle you skipped the first time. If you can't name what you'd actually
measure to back up a claim, you've practiced the vocabulary, not the judgment.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
