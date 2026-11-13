# S00 Interview Preparation — Prompt Engineering Foundations

**Course:** AI-Focused Forward Deployed Engineering · Session 00
**Audience:** Experienced software engineers, QA automation engineers, architects, engineering managers, and technical product professionals. No ML background is assumed.
**Scenario:** Northstar (fictional), a customer with synthetic churn and feedback data, before any custom build existed
**Competencies:** C1 AI Engineering Fundamentals (primary), C6 Customer-Facing Technical Delivery (primary), C4 Evaluation/Reliability/Security (secondary), C2 AI Solution Architecture (secondary).

## How to use this bank

These are engineering interviews, not vocabulary tests. Strong answers name the specific
gap a pattern closes, show a concrete prompt (not a paraphrase of "use AI better"), and
know when a pattern-only workflow has stopped being enough.

**Formats**
- **15-minute screen:** Q1, Q3, Q8, plus one follow-up from each.
- **30-minute technical interview:** Q2, Q5, Q7, Q9.
- **45-minute FDE design interview:** Q4, Q10, Q11, Q12, Q13.

**Rating rubric (per question)**

| Rating | Observable behavior |
|---|---|
| **0 — Missing** | Incorrect or irrelevant; cannot name which pattern applies or why. |
| **1 — Emerging** | Correct terminology, but a vague or generic prompt with no concrete mechanism. |
| **2 — Competent** | A workable, specific prompt or diagnosis, with the relevant limitation named. |
| **3 — Strong** | Adds a falsifiable evaluation claim, a named failure mode, and the customer-facing implication. |

An overall interview should include both foundational and applied questions. Do **not**
infer production-readiness from a strong answer to a single question.

> [!NOTE]
> Agent loops, harness internals, and typed-output contracts are assessed in S01 and S02,
> not here — this bank stays inside prompt-only workflows.

---

## A. 🧩 Fundamentals

### Q1. What is a prompt pattern, and why isn't it "magic words"?
**Difficulty:** Foundational · **Competency:** C1

**Prompt:** A teammate says, "Prompt patterns are basically just phrasing tricks — add the
right words and the model does better." Push back on or refine that claim.

**Expected strong answer:**
- A pattern is a reusable template that closes a *specific class* of under-specification
  (missing audience/role, missing worked examples, missing stated reasoning target, missing
  theme structure) — the same way a design pattern closes a specific class of software
  problem, not a universal improvement.
- The right test for using one: name the failure it's supposed to fix *before* applying it.
  "I don't know, try adding a persona" is the smell of a trick, not engineering.
- Patterns compose (Persona + Recipe + Meta Language in one prompt) but don't substitute
  for giving the model real material to work with.

**Weak answer to probe:** "Just add 'act as an expert' to anything and it gets better."
**Probing follow-ups:** What's an example where adding a persona would *not* help? What
would convince you a pattern made no measurable difference?
**Evidence of mastery:** Candidate names the gap first, then the pattern — not the reverse.
**Common misconception:** Treating prompt patterns as a competitive-advantage secret rather
than ordinary specification discipline applied to a new kind of interface.

### Q2. Persona Pattern — what does it change, what doesn't it change?
**Difficulty:** Foundational · **Competency:** C1 · **Secondary:** C4

**Prompt:** A stakeholder says, "I gave it a 'senior BI consultant' persona, so I trust this
dashboard recommendation now." Evaluate that trust.

**Expected strong answer:**
- A persona narrows the implicit audience, tone, and depth the model answers at — real and
  useful for getting a response that's immediately usable rather than generic.
- It does **not** verify factual correctness, check the suggestion against Northstar's
  actual data, or guarantee the "expertise" claimed is genuine rather than a confident
  surface style.
- Trust should come from review against explicit criteria, not from the persona label
  itself — a direct echo of S02's schema-validity-versus-correctness distinction, applied
  to prompting instead of typed outputs.

**Weak answer:** "The persona is basically giving it expertise, so it knows more now."
**Probes:** How would a persona-labeled wrong answer look different from a no-persona wrong
answer? What would you check before shipping its recommendation to a VP?
**Evidence of mastery:** Candidate separates *framing quality* from *correctness* cleanly.
**Common misconception:** Conflating confident tone with verified accuracy.

### Q3. Why does Few-Shot need negated and hedged examples?
**Difficulty:** Foundational · **Competency:** C1 · **Secondary:** C4

**Prompt:** Your few-shot classification prompt shows one clearly positive and one clearly
negative example. A reviewer flags it as incomplete before you ship it. Why might they be
right?

**Expected strong answer:**
- Clean, unambiguous examples don't demonstrate the boundary cases that actually cause
  disagreement: negation ("would not recommend"), hedging ("not bad, but could be
  better"), and cancellation ("neither good nor bad").
- A label name alone doesn't disambiguate these; the model needs a worked case showing how
  the label applies when a surface keyword points one way and the real sentiment points
  another.
- The fix is targeted, not "add more examples" generically — add one negated/hedged example
  per label class you expect to encounter.

**Weak answer:** "Two examples should be plenty, one per class."
**Probes:** Which specific test comment would you use to prove the gap before and after
adding the fix? How would you know the fix actually worked, rather than just feeling safer?
**Evidence of mastery:** Candidate names the specific boundary-case category, not just "add
more examples."
**Common misconception:** Treating few-shot coverage as a *count* of examples rather than a
*coverage of language patterns*.

---

## B. 💻 Patterns in practice

### Q4. Diagnose this Chain-of-Thought prompt
**Difficulty:** Intermediate · **Competency:** C1 · **Secondary:** C4

**Prompt:** "Northstar's CSAT dropped. Think step by step and explain why." Nothing else is
supplied. What's missing, and what would you add?

**Expected strong answer:**
- No concrete data to reason over (what actually moved, by how much, over what period) —
  "think step by step" with nothing to chain through just produces generic, unfalsifiable
  steps.
- No instruction for what the reasoning should conclude with (a ranked hypothesis? a single
  metric to check first?), so a reviewer can't tell which claim the final answer rests on.
- Fix: supply the actual correlated metrics (response time, ticket volume, CSAT) and ask
  for a stated, falsifiable conclusion — e.g., "state which single metric you'd investigate
  first and why."

**Weak answer:** "It looks fine, CoT just means it reasons more."
**Probes:** If you ran this prompt twice, would you expect the same reasoning path both
times? Why would that matter to a reviewer?
**Evidence of mastery:** Candidate identifies the missing *material*, not just the missing
phrase.
**Common misconception:** That the instruction phrase is the mechanism rather than a
request that still needs real content to act on.

### Q5. Design a Semantic Filter + Recipe prompt
**Difficulty:** Intermediate · **Competency:** C1, C6

**Prompt:** Northstar now wants the same theming treatment applied to *positive* feedback,
to find out what's actually working. Design the prompt.

**Expected strong answer:**
- Keep the recipe shape (a named theme set + "one insight per theme"), but choose themes
  relevant to what's working — e.g., Product Quality, Pricing/Value, Support Experience,
  Delivery Speed — rather than reusing the complaint-oriented theme set unchanged.
- Explicitly exclude negative/neutral comments from this pass, the same way the negative
  pass should exclude positive ones — state the inclusion rule in the prompt, don't assume
  it.
- Note the result is still unverified: themes are a starting hypothesis for the support
  team to confirm against their own read of the comments, not a final answer.

**Weak answer:** Reuses the negative-feedback theme list unchanged and doesn't address
exclusion at all.
**Probes:** What would you do with a comment that's mixed — some praise, some complaint?
**Evidence of mastery:** Candidate adapts the recipe to the new goal rather than copying it
verbatim.
**Common misconception:** Treating "Semantic Filter" as a fixed theme list rather than a
reusable grouping *method*.

### Q6. When does Question Refinement backfire?
**Difficulty:** Intermediate · **Competency:** C1, C6

**Prompt:** A production incident is actively costing Northstar money. Someone suggests:
"Before answering, ask me 3–5 clarifying questions." Is that still the right move?

**Expected strong answer:**
- Question Refinement trades immediate action for precision — the wrong trade when time
  pressure outweighs the cost of acting on a reasonable guess.
- A better move under time pressure: state your best-guess assumption explicitly and act,
  flagging what you assumed, rather than pausing the whole response on clarification.
- The pattern is well-suited to genuinely ambiguous, non-urgent goals (the original churn
  ask) — not to every vague request regardless of context.

**Weak answer:** "Clarifying questions are always good practice."
**Probes:** How would you redesign the prompt to get speed *and* a stated assumption?
**Evidence of mastery:** Candidate recognizes pattern selection is situational, not a
default best practice.
**Common misconception:** Treating every pattern as strictly additive goodness regardless
of context.

### Q7. Build a few-shot set with real boundary-case coverage
**Difficulty:** Intermediate · **Competency:** C1, C4

**Prompt:** You need to classify incoming Northstar support tickets as **Urgent** or
**Not Urgent**. Write 4 few-shot examples that deliberately cover a boundary case a naive
rule would get wrong.

**Expected strong answer:**
- At least one example should defeat an obvious naive rule (e.g., a ticket containing the
  word "urgent" that isn't actually urgent — "not urgent, just curious" — and one that's
  genuinely urgent without using the word "urgent" at all — "production is down for all
  customers right now").
- Candidate states *which* naive rule each example is designed to defeat, not just that the
  examples are "varied."

**Weak answer:** Four examples that are all unambiguous, none testing a real boundary.
**Probes:** What's the naive keyword rule you're specifically trying to break here?
**Evidence of mastery:** Candidate reasons backward from a specific failure mode to the
example that exposes it.
**Common misconception:** Picking "different-looking" examples instead of examples that
specifically probe a known weak point.

---

## C. 🔍 Evaluation and judgment

### Q8. Debug suspiciously perfect prompting results
**Difficulty:** Intermediate · **Competency:** C4

**Prompt:** A teammate demos a new sentiment-classification prompt with 100% accuracy on
10 example comments and wants to ship it. What do you ask before agreeing?

**Expected strong answer:**
- How were the 10 examples chosen — randomly, or cherry-picked because they already look
  clean/unambiguous?
- Do the 10 include any negated, hedged, sarcastic, or mixed-sentiment comments, or only
  clear-cut cases?
- Is 10 even enough to detect a real failure rate, or is this sample too small to trust at
  all — the same small-sample caution this session's lab applies to its own 28-item gold
  set?

**Weak answer:** "100% is 100%, ship it."
**Probes:** What specific comment would you add to try to break it?
**Evidence of mastery:** Candidate questions the sample's composition and size before the
number itself.
**Common misconception:** Treating a clean demo result as evidence of production readiness.

### Q9. Overall accuracy or error type — which matters more?
**Difficulty:** Intermediate · **Competency:** C4

**Prompt:** Classifier A gets 90% of comments right but occasionally rates a strongly
negative comment as Positive. Classifier B gets 85% right and never makes that specific
error — its mistakes are all neutral/positive mixups. Which would you recommend to
Northstar's support team, and why?

**Expected strong answer:**
- Likely Classifier B: missing a strongly negative comment entirely (routing a furious
  customer as if they were happy) is a more costly failure than confusing two mild
  sentiments.
- The headline accuracy number hides exactly this distinction — evaluation needs to look at
  *which* comments are misclassified and *how badly*, not just the count.
- The right answer depends on what the classification result actually drives — if it's
  just a dashboard tally, the cost profile is different than if it's triggering outreach.

**Weak answer:** "A, because 90% beats 85%."
**Probes:** What would change your answer if this classification result triggered an
automatic apology email?
**Evidence of mastery:** Candidate ties the evaluation metric to the actual downstream
consequence of an error.
**Common misconception:** Treating aggregate accuracy as sufficient on its own.

### Q10. "It worked in the demo" vs. "it's ready"
**Difficulty:** Intermediate · **Competency:** C4, C6

**Prompt:** Explain to a non-technical Northstar stakeholder, in plain language, why a
prompt that produced a great result in your demo isn't automatically ready to run
unattended on all their real customer data.

**Expected strong answer:**
- The demo ran on a small, often cleaner sample than what arrives in production — real
  text has typos, sarcasm, multiple languages, and multi-topic comments the demo set may
  not have tested.
- A good result on a handful of examples doesn't bound the failure rate on the full volume
  — that requires a larger, representative check.
- Plain-language framing matters here: "working" and "measured to work at this volume,
  with this failure rate" are different claims, and a stakeholder needs to hear which one
  you're making.

**Weak answer:** Jumps straight into technical caveats without ever landing a plain-English
version a non-technical stakeholder would act correctly on.
**Probes:** How would you phrase the caveat so it doesn't sound like you're walking back
the result?
**Evidence of mastery:** Candidate keeps the caveat honest *and* actionable in one plain
sentence.
**Common misconception:** Either overselling the demo or hedging it into uselessness.

---

## D. 🗺️ Forward-deployed engineering scenarios

### Q11. "Can't we just ask ChatGPT to do all of this?"
**Difficulty:** Advanced · **Competency:** C6, C2

**Prompt:** A Northstar stakeholder asks why they'd need an engineering engagement at all
if a well-written prompt can already produce the churn summary and the feedback themes.
Respond.

**Expected strong answer:**
- They're right that a well-patterned prompt is often enough for a one-off analytical read
  — that's exactly this session's point, and it's worth saying plainly rather than talking
  them out of a true observation.
- The line moves once the output needs to run repeatedly, unattended, on live data, feeding
  a decision with real consequences (a refund, a discount, a backlog priority) — at that
  point you need the verification and harness mechanics (S01) and/or a typed, validated
  contract (S02) a one-off prompt doesn't provide.
- A credible FDE names that line explicitly instead of either overselling the need for a
  build or underselling the value of what a good prompt already does for free.

**Weak answer:** Defends the need for a build reflexively, without acknowledging the prompt
already solved the immediate problem.
**Probes:** What's the smallest version of this that would still need a real build?
**Evidence of mastery:** Candidate concedes ground honestly, then draws a specific,
defensible line.
**Common misconception:** Treating "can a prompt do it" and "should this become a product"
as the same question.

### Q12. Make the call: automate the discount decision?
**Difficulty:** Advanced · **Competency:** C2, C6, C4

**Prompt:** Northstar wants the churn-summary prompt turned into a nightly job that
automatically issues retention discounts to at-risk customers, with no human review. Make
the recommendation, with reasoning.

**Expected strong answer:**
- No, not as a direct extension of the current prompt — it's now an unreviewed, recurring,
  automated action with real financial consequence, not an analytical read.
- Name the specific missing mechanisms: bounded verification before any discount fires
  (S01's harness/verification concerns) and a typed, validated decision contract so the
  automation can't act on a malformed or out-of-policy result (S02's concerns).
- A credible middle path: keep a human in the loop for the first N cycles, measure false
  positive/negative rates on real outcomes, and only reduce review once that's demonstrated
  — not "add safeguards eventually."

**Weak answer:** Either "sure, it worked for the summary" or a flat refusal with no path
forward offered.
**Probes:** What would you want to see in week one of a human-in-the-loop pilot before
trusting it further?
**Evidence of mastery:** Candidate gives a specific, staged path rather than a binary
yes/no.
**Common misconception:** That "the prompt already works" transfers directly to "the
automation is safe to run unattended."

### Q13. Twenty minutes before the funding meeting
**Difficulty:** Advanced · **Competency:** C6

**Prompt:** You have 20 minutes with Northstar's VP before a meeting that decides whether
the next phase gets funded. Describe your prompt-driven workflow, timeboxed, and name what
you will explicitly skip.

**Expected strong answer:**
- A concrete, timeboxed sequence: load the churn/feedback data (2 min), run the patterned
  prompts already drafted rather than improvising new ones under pressure (8 min), sanity
  check 2–3 numbers by hand against the raw data (5 min), draft the 3–5 sentence stakeholder
  note (5 min).
- Explicitly skip: building any new pattern from scratch, chasing a statistically rigorous
  evaluation, or verifying every number — state plainly which numbers you spot-checked
  versus trusted as-is.
- The deliverable is a believable, honestly-caveated read, not a guarantee — and saying so
  out loud is part of the deliverable, not a weakness in it.

**Weak answer:** A vague "I'd just ask the AI a few questions and see what comes back."
**Probes:** Which one number would you personally verify by hand if you only had time for
one?
**Evidence of mastery:** Candidate gives a real timebox with real trade-offs named, not an
idealized full-rigor version that wouldn't fit in 20 minutes.
**Common misconception:** Treating "I didn't have time to verify everything" as something
to hide rather than something to state as an explicit, honest scope limit.

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
| Q11 |  |  |
| Q12 |  |  |
| Q13 |  |  |

### ⚠️ Red flags that justify deeper probing

- Reaches for a pattern name without ever stating which gap it closes.
- Treats a persona, or any single pattern, as a correctness guarantee.
- Can't produce a concrete prompt on demand — only describes patterns abstractly.
- Trusts a small or cherry-picked evaluation sample without questioning it.
- Can't name the specific signal that moves a task from "prompt is enough" to "needs a
  verified build."

> [!TIP]
> **🎤 Interview Tip:** if a candidate answers Q11 or Q12 by either dismissing the value of
> a well-patterned prompt or defending a full build reflexively, without naming where the
> actual line is, revisit the corresponding handout section before continuing your
> interview practice.

## 🗺️ Related learner resources

- **Handout:** Concise concept reference, including all six pattern walkthroughs.
- **Quiz:** A 14-question, 70-point formative assessment.
- **Lab:** A runnable synthetic Northstar scenario — churn EDA plus a naive-vs-few-shot
  comparison — with deterministic offline checks and an optional live-model path.

## 🛠️ Recommended learner practice

Before your next interview or review, pick one Northstar prompt from the handout and
rewrite it for your own current work — same pattern, your own data. If you can't name the
specific gap your version closes, you haven't practiced the pattern yet, only copied it.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
