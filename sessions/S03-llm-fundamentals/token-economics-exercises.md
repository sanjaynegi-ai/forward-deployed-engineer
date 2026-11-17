# Token Economics & Context Management — Exercises

**Companion to:** `notebooks/LLM_Engineering_Decisions.ipynb` (in this session's folder)
**Use this for:** review, self-assessment, or interview prep **without** running the
notebook — every question here is answerable on paper. For the hands-on version of the
same ideas, run the notebook itself; this document is the standalone check.

**How to take it:** answer each question yourself before expanding its **Answer**. All
dollar figures and token counts here either come from the notebook's own verified
computations (stated as such) or are illustrative assumptions for the exercise (stated as
such) — never a live market price.

---

## Section A — Token Exploration (Lab 1)

### A1. Why doesn't word count predict token cost?

Explain, in one or two sentences, why a five-word ticket can cost more tokens than a
fifteen-word ticket.

<details>
<summary>Answer</summary>

Token count depends on what the tokenizer's vocabulary already has single entries for,
not on word count — uncommon vocabulary, code syntax, heavy punctuation, and non-Latin
scripts all tend to split into multiple sub-word tokens per word, while common, short,
plain-English words often map to one token each. Five words of rare technical vocabulary
or a different script can outcost fifteen words of plain English.

**Misconception:** treating "visible length" (words or characters) as a stand-in for
"what this costs," when the two can diverge sharply depending on content.

</details>

### A2. Predict the higher-cost string

Between `"if x > 0: return x"` (a short code snippet) and `"If the value is greater than
zero, return the value."` (its English equivalent, longer by word count), which is more
likely to use *more* tokens relative to its word count, and why?

<details>
<summary>Answer</summary>

The code snippet. Code syntax (`:`, `>`, `0`, `x`, indentation-sensitive tokens) is far
less common in a general-purpose tokenizer's training data than ordinary English prose,
so it's more likely to split into multiple tokens per symbol. The English version, despite
having more words, uses common vocabulary a tokenizer is more likely to represent
efficiently.

**Misconception:** assuming the shorter string is automatically the cheaper one.

</details>

---

## Section B — Token Economics (Lab 2)

### B1. Calculate the retry multiplier

A workflow has a 12% retry rate. What is the expected number of attempts per completed
ticket? (Use `1 / (1 - retry_rate)`.)

<details>
<summary>Answer</summary>

`1 / (1 - 0.12) = 1 / 0.88 ≈ 1.136` expected attempts per completed ticket (verified via
the notebook's `ticket_cost_model` function, which uses exactly this formula).

</details>

### B2. Why does retry rate hit cost harder than output length?

A teammate proposes cutting output tokens in half to control cost, instead of
investigating a rising retry rate. What's the flaw in that priority order?

<details>
<summary>Answer</summary>

Cutting output tokens in half only reduces the output-token portion of a single attempt's
cost. A retry re-pays the **entire** per-attempt cost — input tokens and output tokens
both — every time it happens. In the notebook's verified sensitivity sweep, moving retry
rate from 2% to 30% (holding everything else at Scenario B's values) raised monthly cost
from $2,360.65 to $3,304.91 — a bigger swing than halving output tokens produced (from
$2,514.61 to $2,249.91 when cutting from 80 to 40 output tokens). Retry rate is usually
the higher-leverage, less obvious lever.

**Misconception:** assuming the most visible lever (output length, which is a config
setting you set once) is automatically the most impactful one.

</details>

### B3. Read the worked-scenario comparison

Using the notebook's verified figures — Scenario A (Lean): $636.76/month; Scenario B
(Context-heavy): $2,514.61/month, both at 50,000 tickets/day — what is the monthly
difference, and what two factors (not model choice, not pricing) caused it?

<details>
<summary>Answer</summary>

**$1,877.85/month difference.** The two scenarios use the identical model and identical
per-token prices — the only differences are (1) average input tokens attached per ticket
(250 vs. 1,200 — i.e., how much conversation history/context got attached) and (2) the
resulting retry rate (2% vs. 8%, plausibly because longer, noisier input produces more
validation failures). Neither difference required changing the model or negotiating a
better price.

**Misconception:** assuming a cost difference this size must come from model choice or
provider pricing, rather than from an application-level habit (how much gets attached
per call).

</details>

### B4. Cached-input pricing — what would you verify before trusting it?

A provider's documentation claims a 75% discount on a cached prompt prefix. Before
updating a cost forecast to reflect that discount, what would you check?

<details>
<summary>Answer</summary>

Whether the specific prefix you're sending is actually eligible for that provider's
caching rules (exact match, minimum length, time-to-live window), and whether the
**reported usage/invoice** for real calls actually reflects the discount — not just the
documented rate. The notebook's own cached-pricing cell states this explicitly: never
assume a discount applies without verifying it against real, measured usage.

**Misconception:** treating a documented discount rate as equivalent to a guaranteed,
automatic saving on every call.

</details>

---

## Section C — Context Window Engineering (Lab 3)

### C1. Trace the budget-pruning algorithm by hand

Mandatory blocks total 75 tokens. Available budget is 130 tokens (so 55 tokens remain
for optional blocks). Three optional blocks: `history_turn_1` (15 tokens),
`doc_sla_table` (30 tokens), `doc_billing_faq` (50 tokens). If the priority order (highest
priority, i.e. tried first, listed first) is `[doc_billing_faq, doc_sla_table,
history_turn_1]`, which blocks get kept and which get dropped?

<details>
<summary>Answer</summary>

**Kept: only `doc_billing_faq`. Dropped: `doc_sla_table` and `history_turn_1`.**
`doc_billing_faq` (50) fits in the 55 remaining, leaving 5 tokens remaining.
`doc_sla_table` (30) doesn't fit in 5 — dropped. `history_turn_1` (15) doesn't fit in 5
either — dropped. (This is the notebook's own verified "naive, size-first" ranking
result.) Note that reordering the same three blocks as `[history_turn_1, doc_sla_table,
doc_billing_faq]` against the same 55-token remainder keeps the first two (15 + 30 = 45
≤ 55) and drops only `doc_billing_faq` — same budget, same three blocks, a different
outcome purely from ranking order.

**Misconception:** assuming a budget constraint has one deterministic outcome regardless
of ranking, when ranking order is itself a design decision with real consequences.

</details>

### C2. Why "I don't have enough information" can be the *better* failure

The notebook's deterministic mock answers "I don't have enough information to determine
your SLA tier" when the tier-stating turn gets pruned, rather than guessing a plausible
tier. Why is that a better failure mode than a confident wrong answer?

<details>
<summary>Answer</summary>

A confident wrong answer (e.g., guessing "Standard" when the customer is actually
"Enterprise") can drive an incorrect downstream action with no visible signal that
anything went wrong. An honest "I don't have enough information" is detectable,
escalatable, and doesn't silently corrupt a business decision — the same verification
and escalation discipline **S01** and **S02** both build around model outputs, applied
here to context loss specifically.

**Misconception:** treating "the system produced an answer" as inherently better than
"the system correctly reported it couldn't."

</details>

### C3. Keyword-overlap selection vs. a RAG pipeline — what's actually different?

The notebook's `keyword_overlap_score` function ranks candidate documents by shared
words with the ticket text. Name one concrete limitation this approach has that an
embeddings-based retrieval system (RAG) is specifically built to address.

<details>
<summary>Answer</summary>

Keyword overlap only catches documents that share literal words with the query — it
misses a document that's genuinely relevant but phrased differently (e.g., a doc about
"response time commitments" wouldn't score well against a ticket asking about "SLA," even
though they mean the same thing). Embeddings-based retrieval is built to capture that kind
of semantic similarity rather than literal word overlap. The notebook deliberately stops
short of building that system — it's a future Context Engineering and RAG session's
subject.

**Misconception:** treating "a simple relevance heuristic" and "a full retrieval system"
as solving the same problem equally well at any scale.

</details>

### C4. "The context window is huge" — what's still missing from that argument?

A teammate argues Northstar should attach every available knowledge-base article to every
ticket, since the model's context window is large enough to fit all of them. What's
still unaddressed by that argument?

<details>
<summary>Answer</summary>

Fit is not the same as cost-effective or helpful: every attached token costs money and
latency on every call regardless of whether it's relevant, and irrelevant material can
crowd out the signal that actually matters to the answer. "It fits" answers a capacity
question; it doesn't answer a cost or relevance question, both of which Lab 2 and Lab 3
measure directly.

**Misconception:** conflating "technically fits in the context window" with "a good idea
to include."

</details>

---

## Section D — Streaming Architecture Decision (Lab 4)

### D1. Pick the metric for each workload

For an interactive support copilot (a human watches the reply appear) and a background
batch classification job (nobody watches any individual call), name the one latency
metric that actually matters for each.

<details>
<summary>Answer</summary>

**Interactive copilot:** time to first visible chunk (TTFT) — it's what the waiting human
actually experiences. **Batch classification:** total batch wall-clock time (throughput
across all calls) — no human is watching any single call's TTFT, so it's not the relevant
number for that workload.

**Misconception:** applying the same "streaming helps" framing to both workloads
regardless of whether anyone is actually watching output appear.

</details>

### D2. Why does a truncated stream fail to parse?

A client receives the first 30 characters of a streamed, structured JSON response and
tries `json.loads()` on it immediately. What happens, and why?

<details>
<summary>Answer</summary>

It raises a `JSONDecodeError` (verified in the notebook) — a partial JSON string is not a
smaller valid JSON object, it's simply not valid JSON until the closing brace and all
required fields have arrived. This is a real operational risk for any structured-output
workload that streams naively: either buffer the full response before parsing, or use a
provider's purpose-built structured-streaming support.

**Misconception:** assuming a structured response degrades gracefully into "a partial
but still useful answer" when interrupted, the way plain prose text does.

</details>

### D3. True or false: streaming makes the model generate faster

Justify your answer in one sentence.

<details>
<summary>Answer</summary>

**False.** The model still generates one token at a time via the same autoregressive
process regardless of delivery mode (S03's core claim); streaming only changes *when* the
client receives pieces of that output, not how much compute generation takes or the total
time until the last token exists.

**Misconception:** treating streaming as a performance optimization rather than a
delivery/UX choice.

</details>

---

## Section E — Synthesis: the Northstar recommendation

### E1. Write the full recommendation

Northstar wants to classify 50,000 tickets daily with predictable latency and spending.
Recommend: a prompt/context budget, model-selection criteria, an output-token limit,
streaming or non-streaming, a cost estimate with stated uncertainty, and the key
operational risks — in plain business language, as if sending it to Northstar's VP of
Support.

<details>
<summary>Grading guide (this is the notebook's own conclusion exercise — see its
instructor model answer for a full worked example)</summary>

A strong answer:
- Names a **specific** context budget and pruning rule (e.g., "ticket + top-2 relevant
  snippets + most recent turn, ranked by relevance, capped around 300–400 input tokens"),
  not "use less context."
- Ties model-selection criteria to **measured** accuracy/critical-miss rate on
  representative data (S02's method), not a benchmark leaderboard name.
- Gives a reasoned output-token number tied to what the task actually needs to produce
  (a category, priority, and short justification), not an arbitrary round number.
- Correctly argues **non-streaming** for this specific workload (nobody watches a single
  call; a structured result risks unparseable truncation if streamed) — not a blanket
  streaming rule in either direction.
- States a cost figure (using Lab 2's model) explicitly as **assumption-dependent**, not
  a committed budget number.
- Names risks that come from this notebook's own demonstrations — a bad pruning ranking
  silently dropping a load-bearing fact, a retry-rate spike quietly multiplying cost, an
  unverified caching/pricing assumption — rather than generic AI-safety language.

**Common weak answer:** picks the "smartest" or "cheapest" model without a measurement
criterion, recommends streaming "because it's modern," or gives a cost figure with no
stated assumptions or uncertainty.

</details>

---

## Coverage note

This exercise sheet assesses the same four labs as the companion notebook — token
counting, cost modeling, context-budget selection, and the streaming decision — applied
to Northstar's 50,000-ticket/day workload. It does not test agent-loop mechanics (S01) or
typed-contract validation (S02) directly, though E1's recommendation draws on both.
