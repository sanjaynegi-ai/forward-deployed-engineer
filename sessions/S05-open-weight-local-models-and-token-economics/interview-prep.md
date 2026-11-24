# S05 Interview Preparation — Open-Weight, Local Models, and Token Economics in Practice

**Course:** AI-Focused Forward Deployed Engineering · Session 05
**Audience:** Experienced software engineers, architects, engineering managers, and technical product professionals who have completed S02 and S03.
**Scenario:** Northstar Support Systems, a fictional customer with synthetic support tickets
**Competencies:** C2 AI Solution Architecture (primary), C5 Deployment & Operations (primary). **Secondary:** C1 AI Engineering Fundamentals, C4 Evaluation/Reliability/Security, C6 Customer-Facing Technical Delivery.

## How to use this bank

These interviews probe whether a candidate keeps three separate questions straight:
*which weights* (accuracy), *where they run* (cost/latency/memory/residency), and *what
you send them* (token cost and, less obviously, accuracy). A candidate who conflates any
two of these gives a weaker answer than one who keeps them apart, even when both reach
the same final recommendation.

**Formats**
- **15-minute screen:** Q1, Q4, Q7, plus one follow-up from each.
- **30-minute technical interview:** Q2, Q5, Q8, Q9.
- **45-minute FDE design interview:** Q3, Q6, Q10, Q11, Q12.

**Rating rubric (per question)**

| Rating | Observable behavior |
|---|---|
| **0 — Missing** | Treats open/closed and hosted/local as the same axis, or ignores data residency as an architectural constraint. |
| **1 — Emerging** | Correct terminology, but no measurement or validation plan behind it. |
| **2 — Competent** | Correctly separates the axes and gives a workable comparison or trimming design. |
| **3 — Strong** | Adds real-token measurement, a validation step for any assumed signal, and customer-facing framing of a hard constraint. |

> [!NOTE]
> Agent-loop mechanics (S01) and technique dispatch (S04) are assessed in their own
> sessions, not here. This bank assumes S02's contract/comparison discipline and S03's
> token mechanics are already solid.

---

## A. 🧩 Fundamentals

### Q1. What does open-weight actually buy you?
**Difficulty:** Foundational · **Competency:** C2 · **Secondary:** C5

**Prompt:** A stakeholder says, "Let's just use an open-weight model, it's cheaper."
Respond.

**Expected strong answer:**
- Open-weight is a licensing/deployment fact — it determines where you're allowed to
  run the model, including entirely on your own or a customer's infrastructure.
- It says nothing by itself about accuracy or cost: compute, hosting, and operational
  burden still cost something, whether hosted or local.
- The real reason to reach for open-weight is usually deployment flexibility (including
  data residency), not an assumed cost or accuracy advantage.

**Weak answer to probe:** "Open-weight models are always cheaper and that's the whole
reason to use one."
**Probing follow-ups:** What would make an open-weight model *more* expensive than a
closed one in practice? What does "open-weight" not tell you at all?

### Q2. Same weights, two deployments — what should and shouldn't change
**Difficulty:** Foundational · **Competency:** C5 · **Secondary:** C2

**Prompt:** The same open-weight model is deployed once through a hosted provider and
once on local hardware. What should differ between the two, and what shouldn't?

**Expected strong answer:**
- Should differ: marginal cost per call, latency/throughput profile, memory footprint,
  and whether data leaves the premises.
- Shouldn't differ: accuracy — same weights should produce the same results; a real
  accuracy gap is evidence of a quantization difference, version mismatch, or
  serving-stack bug, not a legitimate deployment-location effect.

**Weak answer:** "Local is always more accurate because it's more controlled" or "local
is always less accurate because it's a smaller model" — both assume a link between
location and capability that isn't actually there.
**Probes:** If you saw an accuracy gap between the two in production, what would you check first?

### Q3. Tokens, not words
**Difficulty:** Intermediate · **Competency:** C1 · **Secondary:** C5

**Prompt:** A teammate estimates prompt cost by counting words instead of running a
tokenizer. What's the risk?

**Expected strong answer:**
- Tokenization is model/tokenizer-specific and doesn't map 1:1 onto words — word
  fragments, punctuation, and formatting can change token count independent of word
  count.
- Cost and context-window limits are measured in tokens, not words; a word-count
  estimate can be meaningfully wrong in either direction.
- Measure with the actual tokenizer for the model/route in question before quoting a
  cost or capacity figure.

**Weak answer:** "Words and tokens are close enough for estimation purposes."
**Probes:** What would make the gap between word count and token count larger — short common words, or long technical/foreign terms? Why?

---

## B. 🧩 Design and measurement

### Q4. Design a context-trimming scheme
**Difficulty:** Intermediate · **Competency:** C5 · **Secondary:** C1

**Prompt:** You have a knowledge base split into one section per topic, plus a shared
general-rules section. Design a way to send a model only what a given request actually
needs.

**Expected strong answer:**
- Use a cheap, already-available signal to pick the relevant section — e.g., something
  the customer already indicated, not something that requires an expensive call to
  infer.
- Always include whatever rules apply universally (like the general-rules section) —
  trimming the relevant-but-topic-specific material, not the baseline rules every
  request needs.
- Measure the actual token/cost/latency savings with a real tokenizer, and measure
  whether accuracy changed — in either direction — not just assume it held constant.

**Weak answer:** Proposes trimming by truncating the prompt at a fixed character/word
count, without regard to which content that keeps or removes.
**Probes:** What happens if the cheap signal you're trimming by is sometimes wrong? Where does that risk show up?

### Q5. Debug this trimming function
**Difficulty:** Intermediate · Code/debugging · **Competency:** C4

**Prompt:**

```python
def build_context(ticket, sections, general_rules):
    relevant = sections.get(ticket["topic_hint"], "")
    return general_rules + relevant + sections["general"]
```

What's the defect?

**Expected strong answer:**
- `sections["general"]` is appended unconditionally, regardless of `topic_hint` — any
  ticket whose hint isn't `"general"` silently receives two sections instead of one.
- This partially defeats the trimming's token/cost savings and reintroduces the
  context-dilution risk trimming exists to avoid, since an unrelated section's text is
  back in the prompt.
- Fix: only include the one section the hint actually names.

**Weak answer:** "It looks fine, it includes the relevant section."
**Probes:** How would you catch this kind of bug with a token-count assertion in a test, rather than by reading the code?

### Q6. What do you monitor after choosing a deployment?
**Difficulty:** Advanced · **Competency:** C5 · **Secondary:** C4

**Prompt:** You've picked a model/deployment/context configuration and shipped it. What
do you keep watching?

**Expected strong answer:**
- Real token counts and cost per request over time — context size can drift as the
  knowledge base grows, silently eroding the savings a trimming design achieved at
  launch.
- Accuracy, specifically watched for any divergence between what should be identical
  configurations (e.g., hosted vs. local of the "same" model) — a real divergence is an
  actionable bug, not noise.
- The rate at which any cheap routing/trimming signal disagrees with the ground truth,
  on an ongoing sample — not just at launch.

**Weak answer:** "Just watch the final decision output — that's what matters to the
customer."
**Probes:** How would you notice, from monitoring alone, that a hosted provider silently
changed the model version behind an API you call?

---

## C. 🔍 Evaluation and validation

### Q7. Validate a routing hint before trusting it
**Difficulty:** Advanced · Evaluation design · **Competency:** C4

**Prompt:** Context trimming in this session's lab assumed a customer-provided topic
hint always matches the real category. How do you validate that assumption?

**Expected strong answer:**
- On a representative, held-out sample, compare the hint against the human-confirmed
  correct category and measure the disagreement rate.
- For disagreements, specifically check whether trimming to the (wrong) hinted section
  caused a wrong decision the full-context version would have avoided — that's the
  actual production risk, not the raw disagreement rate alone.
- Decide a tolerance threshold with the business, not unilaterally — a 2% hint error
  rate might be fine; a 20% one changes the trimming design's viability entirely.

**Weak answer:** "The hint comes from the customer, so it's reliable by definition."
**Probes:** What would you do if the hint's error rate turned out to be too high to trust blindly?

### Q8. Explain a result that looks backwards
**Difficulty:** Intermediate · **Competency:** C4 · **Secondary:** C1

**Prompt:** Trimming a prompt's context made accuracy go *up*, not just cost go down.
Explain the mechanism to a skeptical teammate who assumes less context can only hurt.

**Expected strong answer:**
- The improvement came from removing one specific unrelated section whose wording was
  distracting a less capable model into a wrong category on one ticket — a
  context-dilution error, not a capability limit.
- Context size and accuracy don't trade off in a single fixed direction; relevance is
  the actual variable. Irrelevant material can actively hurt, not just cost more and do
  nothing.
- This doesn't mean smaller is always better — it means *relevant* is what to optimize
  for, and smaller-but-still-relevant is what trimming, done correctly, achieves.

**Weak answer:** "That shouldn't be possible — more information can't make a model
worse."
**Probes:** What would you expect to happen if you trimmed too aggressively — removed a section the ticket genuinely needed?

### Q9. The benchmark-fitness trap, one level up
**Difficulty:** Intermediate · **Competency:** C2 · **Secondary:** C4

**Prompt:** S02 warned against trusting a public leaderboard over a task-specific
comparison. What's the equivalent trap in this session's material?

**Expected strong answer:**
- Assuming the closed model's win on this lab's 10-ticket trial — specifically, on one
  hard, cross-referencing ticket — generalizes to "the closed model is categorically the
  right choice" without knowing how often real traffic looks like that one hard case.
- The deployment-location comparison (hosted vs. local) has its own version: assuming a
  clean trial result on illustrative cost/latency numbers predicts real infrastructure
  cost without measuring against real traffic and real hardware.
- Task-specific, volume-scaled, held-out evidence is still what a real recommendation
  needs — the session's own numbers establish a mechanism, not a production figure.

**Weak answer:** "The closed model won the trial, so it's the better choice, period."
**Probes:** What would you want to know about real traffic before trusting this trial's accuracy gap as representative?

---

## D. 🗺️ Forward-deployed engineering scenarios

### Q10. The data residency conversation
**Difficulty:** Advanced · Customer discovery · **Competency:** C6 · **Secondary:** C2

**Prompt:** A prospect requires that ticket text never leave their infrastructure. Their
trial used the closed, hosted configuration, which scored highest. The account team asks
if the deal is still possible with "the good model."

**Expected strong answer:**
- States plainly that the closed model is ruled out architecturally — every call to it
  leaves the premises by definition — before discussing cost or accuracy at all.
- Identifies open-weight local as what's actually left to choose from, and names the
  real accuracy trade-off being accepted (the specific capability gap measured in the
  trial), not a vague "slightly less accurate."
- Doesn't oversell a workaround that doesn't exist — there is no way to keep the closed
  model and satisfy a genuine on-premises requirement.

**Weak answer:** Proposes encrypting the data in transit to the closed model's API as if
that satisfies a residency requirement, rather than addressing that the data still
leaves the premises either way.
**Probes:** What specific evidence would you want before quoting the customer an accuracy number for the local deployment?

### Q11. Hosted and local disagree in production
**Difficulty:** Advanced · Troubleshooting · **Competency:** C4 · **Secondary:** C5

**Prompt:** Hosted and local deployments of "the same" open-weight model start producing
different results on replayed tickets at a measurable rate. Investigate.

**Expected strong answer:**
- First confirm both sides are actually running the same model version and the same
  quantization/precision — a quantized local model is a genuine capability difference
  disguised as a deployment-location one, and is a very common real cause of this exact
  symptom.
- Second, confirm both sides receive an identical prompt — a client library or
  serving-stack difference silently altering formatting, truncation, or default
  parameters is another common cause.
- Treat "same weights, different results" as a bug to find, consistent with the
  handout's own §2 claim, not as expected noise to shrug off.

**Weak answer:** "Models aren't fully deterministic, so some disagreement is normal and
doesn't need investigating."
**Probes:** What would convince you the remaining disagreement really is just
non-determinism, after ruling out version and prompt mismatches?

### Q12. When local isn't the right call, even if requested
**Difficulty:** Advanced · **Competency:** C2 · **Secondary:** C5

**Prompt:** A customer says they'd prefer a local deployment, with no stated hard
requirement behind it. When would you push back?

**Expected strong answer:**
- If there's no genuine data-residency or compliance requirement, weigh local's real
  costs (latency, memory/hardware burden, operational maintenance) against a hosted
  option's accuracy/cost/latency profile on its own merits, rather than defaulting to
  the customer's stated preference.
- If the customer's actual traffic volume or hardware budget can't realistically support
  local deployment's memory and throughput needs, say so plainly rather than building
  toward a configuration that won't hold up.
- A preference is a data point to discuss, not an unquestionable requirement — unlike a
  genuine data-residency constraint, which isn't up for debate.

**Weak answer:** "If the customer wants local, we build local — it's their call."
**Probes:** How would you distinguish, in that first conversation, a real requirement from a stated preference that hasn't been pressure-tested yet?

---

## E. ✅ Self-assessment scoring sheet

| Dimension | Questions that provide evidence | Strong-answer indicators | Score (0–3) |
|---|---|---|---|
| Open/closed vs. hosted/local separation | Q1, Q2, Q9 | Correctly attributes accuracy to weights, cost/latency/memory/residency to location | ___ |
| Token measurement discipline | Q3, Q4, Q6 | Real tokenizer measurement, not word-count estimation | ___ |
| Trimming design and debugging | Q4, Q5, Q8 | Correct conditional section inclusion; explains the context-dilution mechanism | ___ |
| Signal and deployment validation | Q6, Q7, Q11 | Concrete held-out tests; treats an unexpected result as a bug to find | ___ |
| Customer-facing constraint judgment | Q10, Q12 | Treats a hard requirement as ruling out candidates, not as a preference to weigh | ___ |

**Suggested interpretation:** Average ~2 indicates practical readiness for S05's learning
objectives; ~3 indicates strong practical judgment within this session's scope. These
ratings are instructional heuristics, **not calibrated hiring cutoffs**.

### ⚠️ Red flags that justify deeper probing

- Attributes an accuracy difference to deployment location (hosted vs. local) rather
  than treating it as evidence of a configuration bug.
- Estimates token cost from word count instead of measuring with a real tokenizer.
- Treats data residency as one more factor to weigh against cost and accuracy, rather
  than a constraint that removes candidates outright.
- Assumes a routing/trimming hint is reliable without proposing any way to measure its
  real error rate.
- Generalizes a small trial's accuracy gap to a production recommendation without
  asking how often real traffic resembles the hard case that drove it.

## 🗺️ Bridge to a later session

Consider: **"Northstar now has a model/deployment choice that satisfies a customer's data
residency requirement. What happens when that same agent needs to work through an entire
queue of tickets on its own, not just decide one at a time?"**

That's an orchestration question, not a model-and-deployment one — **S06: Queue
Harnesses: Orchestrating at Scale, Build vs. Buy** extends S01's single-item agent loop
into one agent that organizes and works a whole queue, independent of which
model/deployment choice this session's material would recommend for it.

---

## 🛠️ Recommended learner practice

1. Rehearse Q1 and Q10 as concise whiteboard explanations — the open/closed-weight
   distinction and the data-residency conversation, under stakeholder pressure.
2. Re-run the lab's trimming code with one knowledge-base section deliberately duplicated
   into another, and predict the token/cost/accuracy consequence before checking it.
3. Redo Q4's volume math at a different assumed daily ticket volume and notice how the
   case for investing in trimming changes.
4. Use the S05 quiz for basic retention; use this bank to probe deeper architectural and
   validation judgment.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
