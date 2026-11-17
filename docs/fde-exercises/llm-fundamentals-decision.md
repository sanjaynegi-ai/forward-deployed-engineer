# FDE Decision Exercise — LLM Fundamentals

**Targets session:** S03 — LLM Fundamentals
**Run after:** §9 (the handout's existing token/cost-budget note) — **this exercise
formalizes §9** into a full stakeholder brief, so it belongs right after that note, not
before it. It does not replace the optional `LLM_Engineering_Decisions.ipynb` companion
notebook, which goes deeper (four full labs) for learners with more time.
**Timebox:** 10–15 minutes. **Artifact:** a short production-configuration memo.

---

## 1. Customer situation

Northstar's support volume has grown to **50,000 tickets per day**. A pilot on a smaller
sample showed the triage model works, but leadership now wants to scale it into a
standing production workflow — and before approving the recurring monthly spend, they
want predictable latency and a defensible cost estimate, not "it worked in the demo."

## 2. Customer stakeholder

**Northstar's Head of Platform Operations** — the operational owner who will carry this
as a recurring line-item cost and an SLA commitment. Unlike S00's VP of Support (who
cared about the business narrative), this stakeholder cares about predictability: will
this run reliably, at this volume, within a budget she can defend.

## 3. Business objective

Approve a production configuration — how much context gets attached per ticket, what the
output limit is, whether responses stream — that keeps cost and latency predictable at
50,000 tickets/day, before this becomes a standing commitment.

## 4. Available information

- Pilot measurements: ~1,200 average input tokens per ticket (full prior thread attached
  by habit), ~80 output tokens, an observed 8% retry rate.
- Illustrative pricing for this exercise: $1.00 per million input tokens, $4.00 per
  million output tokens (stated as an assumption, not a live quote).
- The classification result must be machine-parseable (it feeds S02's typed contract
  downstream).
- Nobody reviews an individual classification call in real time — it's a backend,
  unattended workflow.

## 5. Missing information and reasonable assumptions

- Real production pricing has not been confirmed with the provider yet — assume today's
  figure is illustrative and must be re-verified before being treated as a budget
  commitment.
- The retry-rate distribution at full 50,000/day scale is unknown — only piloted on a
  smaller sample; assume it could be higher under real load and noisier real tickets.
- Whether any ticket genuinely needs multi-turn history is not yet confirmed — assume
  most don't, but some edge cases might.

## 6. Technical decision required

1. **Token-related cost drivers:** which levers (input size, output size, retry rate)
   actually move the bill, and by how much, relative to each other.
2. **Context-budget assumptions:** how much gets attached per ticket, and what gets
   pruned first if a ticket's real history doesn't fit.
3. **Latency and API constraints:** what the context window and output-token limit
   imply for per-call latency at this volume.
4. **Streaming or non-streaming:** a decision, justified by who (if anyone) is watching
   the output.
5. **Risks and unknowns:** what could make this estimate wrong, and what you'd watch for.

## 7. Expected learner artifact

A short **production-configuration recommendation** (bullet memo, not prose paragraphs):

- Context budget per ticket + the one-line pruning rule if it overflows.
- Output-token cap, with a one-line reason.
- Streaming decision, with a one-line reason.
- Cost estimate (using the session's cost-estimation pattern) stated as a range, with its
  assumptions named.
- Top two operational risks.

## 8. Evaluation rubric

| Criterion | What a passing answer shows | Points |
|---|---|---:|
| Correct cost-driver ranking | Identifies retry rate as the highest-leverage lever (it re-pays the *entire* attempt, not just one token category), not just "more tokens cost more" | 3 |
| Specific context budget | Names an actual number and a pruning rule — not "attach less context" unqualified | 3 |
| Correct streaming call | Recommends non-streaming for this specific unattended, backend workload, with the reason tied to who's watching, not a blanket rule | 3 |
| Cost estimate properly scoped | States the figure as assumption-dependent, names the assumptions, does not present it as a measured bill | 3 |
| Risks named are real, not generic | Names risks this scenario actually has (retry-rate spike at scale, unverified pricing, a pruning rule dropping needed context) rather than generic AI-safety language | 2 |
| **Total** | | **14** |

## 9. Instructor guidance

- **Timing:** this fits naturally right after §7's streaming demo — 2 minutes to restate
  the brief, 8 minutes to draft, 3–5 minutes to compare.
- **Reuse, don't re-derive:** learners should reuse the handout's own cost-formula
  pattern (`estimate_usd`-style arithmetic) rather than inventing new math — the exercise
  is testing the *decision*, not arithmetic originality.
- **Watch for:** the single most common failure is recommending maximum context "to be
  safe" without naming the cost trade-off, or turning on streaming out of habit for a
  workload nobody watches live. Both are directly addressed in the handout's §6 and §7
  engineering-implication callouts — point learners back there if they miss it.
- **Connects to:** the optional `LLM_Engineering_Decisions.ipynb` companion notebook runs
  this exact scenario as a full, measured exercise (Labs 2–4) for learners who want to
  verify their intuition with real computed numbers rather than reasoning from the
  handout alone.

## 10. Example of a strong answer

> - **Context budget:** ~300–400 input tokens per ticket — current ticket text plus the
>   single most recent prior turn, dropping older history first if it doesn't fit.
> - **Output cap:** 80–100 tokens — enough for a category, priority, and one-line
>   justification; no need for more on a classification task.
> - **Streaming:** off. Nobody watches an individual classification call, and a
>   structured result risks becoming unparseable if interrupted mid-stream — streaming
>   buys nothing here.
> - **Cost estimate:** roughly $1,000–$1,500/month at current pricing assumptions and an
>   8% retry rate — this depends entirely on those assumptions holding and needs to be
>   re-checked against real provider invoices once live.
> - **Top risks:** a retry-rate increase at full scale would raise cost disproportionately
>   (retries re-pay the whole call, not just part of it); and the pruning rule could drop
>   context a specific ticket actually needed, producing a wrong but schema-valid
>   classification.

**Why it works:** every number has a stated reason; the streaming call is justified by
who's watching, not habit; the cost figure is explicitly conditional; the risks are the
ones this specific workflow actually has.

## 11. Example of an inadequate answer, and why it fails

> "Since the model's context window is large, we should attach the full ticket history
> every time to make sure nothing gets missed. We'll turn on streaming so responses feel
> fast. Cost should be low since it's a small model."

**Why it fails:**
- "Attach the full history to be safe" ignores that every attached token costs money and
  latency on every one of 50,000 daily calls — exactly the "fits in the window ≠ good
  idea" mistake the handout's §6 warns against.
- Turning on streaming "to feel fast" for a backend call nobody watches live provides no
  benefit and adds interrupted-parsing risk for a structured result.
- "Cost should be low" with no numbers, no stated assumptions, and no connection to the
  actual per-token prices or volume is not an estimate — it's a guess presented as a
  conclusion, exactly what this session's cost-modeling exercises are meant to prevent.
