# S00 Learner Quiz — Prompt Engineering Foundations

**AI-Focused Forward Deployed Engineering · Session 00**
**Scenario:** Northstar (fictional); synthetic customer-feedback and churn extracts

## Purpose and administration

This assessment checks whether experienced software professionals can recognize which
prompt pattern closes a given gap, write a pattern-appropriate prompt for a stated
business need, predict a specific failure a missing pattern causes, and reason about why
a small accuracy comparison is or isn't enough evidence to recommend a prompting approach
to a customer.

- **Suggested time:** 25–35 minutes, answering each question before opening its answer.
- **Total:** 70 points, 14 questions. Partial credit is permitted where specified.
- **Primary competencies:** C1 (AI Engineering Fundamentals), C6 (Customer-Facing Technical Delivery). **Secondary:** C2 (AI Solution Architecture), C4 (Evaluation, Reliability & Security).
- **Assumptions:** All Northstar data is synthetic. This quiz does not require running any
  model — code questions ask you to predict or explain behavior. Agent loops (S01) and
  typed output contracts (S02) are **not** in scope here, except where a question explicitly
  asks you to recognize that boundary.
- **How to take it:** Answer each question yourself before expanding its **Answer**
  section. The answers are collapsed by default specifically so you can self-test one
  question at a time without losing your place.

---

## Section 1 — Concepts (Q1–Q4)

### Q1. Name the pattern (2 points)
**Difficulty:** Foundational · **Competency:** C1 · **Type:** Multiple choice

A support lead's prompt reads: "You are a senior support operations lead. Review this
ticket response and flag anything that would embarrass us if a customer saw it." Which
pattern is this primarily demonstrating?

A. Few-Shot
B. Persona
C. Flipped Interaction
D. Semantic Filter

<details>
<summary><strong>Answer</strong></summary>

**Answer:** B (2 points)

**Explanation:** Assigning a role ("senior support operations lead") and an implicit
quality bar ("would embarrass us") is the Persona Pattern. No worked examples (Few-Shot),
no request for the model to ask questions back (Flipped Interaction), and no theme
grouping (Semantic Filter) are present.

**Misconception:** Any instruction containing "review" or "check" is Chain-of-Thought.

</details>

### Q2. Match the gap to the pattern (4 points)
**Difficulty:** Foundational · **Competency:** C1 · **Type:** Matching

Match each situation to the pattern that most directly closes the gap: **Few-Shot**,
**Question Refinement**, **Semantic Filter + Recipe**, or **Flipped Interaction**.

| Situation | Pattern |
|---|---|
| a. A model's classification labels are inconsistent across similar comments | |
| b. A stated goal is too vague to act on yet | |
| c. 500 free-text comments need to become four actionable themes | |
| d. You want the model to check your own understanding, one question at a time | |

<details>
<summary><strong>Answer</strong></summary>

**Answer:** a: Few-Shot; b: Question Refinement; c: Semantic Filter + Recipe; d: Flipped Interaction (4 points)

**Explanation:** Few-Shot pins down boundary cases through worked examples; Question
Refinement turns a vague goal into clarifying questions; Semantic Filter + Recipe groups
unstructured text by meaning into a repeatable categorization; Flipped Interaction puts
the model in the questioner's seat.

**Misconception:** Treating "ask clarifying questions" (b) and "ask the model to quiz you"
(d) as the same pattern — the direction of who's asking whom is the distinguishing feature.

</details>

### Q3. "I added 'think step by step'" (4 points)
**Difficulty:** Foundational · **Competency:** C1 · **Type:** Short answer

A developer says: "I added 'Think step by step' to my prompt, so this is now
Chain-of-Thought." Identify **two concerns** with treating that alone as sufficient for
reliably useful step-by-step reasoning.

<details>
<summary><strong>Answer</strong></summary>

**Strong answer examples (4 points, 2 each):** (1) "Think step by step" with no concrete
data or stated trade-off supplied just produces generic-sounding steps — CoT needs
something specific to reason *over*, not just an instruction to reason; (2) there's no
instruction for what the reasoning should conclude with, so a reviewer can't tell which
claim the final answer actually rests on. Also acceptable: no stated stop condition, or no
acknowledgment that reasoning text is not guaranteed to reflect the model's actual internal
process.

**Misconception:** That the phrase itself is the mechanism, rather than a prompt that gives
the model real material to reason about.

</details>

### Q4. What a persona prompt actually guarantees (2 points)
**Difficulty:** Intermediate · **Competency:** C1 · **Type:** Multiple choice

Which claim about the Persona Pattern is justified?

A. A persona prompt guarantees a factually correct answer.
B. A persona narrows the implicit audience and quality bar the model answers to, but doesn't verify correctness.
C. Personas only work for playful or informal use cases.
D. A persona prompt removes the need for a reviewer.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** B (2 points)

**Explanation:** A persona changes framing and audience-appropriateness, not factual
correctness — that still requires review. This mirrors S02's schema-validity-versus-
correctness distinction, applied to prompting instead of typed outputs.

**Misconception:** That a confident, well-framed persona response is thereby a verified one.

</details>

## Section 2 — Apply the patterns (Q5–Q9)

### Q5. Write a Persona prompt (6 points)
**Difficulty:** Intermediate · **Competency:** C1, C6 · **Type:** Prompt writing

Northstar's VP keeps getting dashboard-chart suggestions that are technically correct but
read like something a junior analyst would produce. Write one Persona-pattern prompt
(2–3 sentences) that addresses this, **and** state the one risk your prompt does *not*
solve.

<details>
<summary><strong>Answer</strong></summary>

**Example strong answer (6 points):**

**Example prompt:** "You are a senior BI consultant with 10+ years of dashboard design
experience, briefing a VP who has 30 seconds to decide. Suggest the charts you'd actually
ship for tracking customer engagement, and flag any choice here that would mislead a
non-technical reader."

**Risk not solved:** The persona does not verify that the suggested charts are factually
appropriate for Northstar's actual data — a reviewer still has to check that.

**Grading:** 4 points for a prompt with role + expertise + explicit audience/quality bar;
2 points for correctly naming a risk the persona doesn't address.

</details>

### Q6. Debug the few-shot set (6 points)
**Difficulty:** Intermediate · **Competency:** C1, C4 · **Type:** Debugging

A colleague's few-shot classification prompt shows only these examples:

```
"Fantastic purchase, will buy again!" --> Positive
"Terrible quality, broke in a day!" --> Negative
```

Of these three unseen test comments, which is **most at risk** of being mislabeled, and
why: *"Would not recommend to anyone."*, *"Not bad, but could be better."*,
*"Fantastic purchase, will buy again!"*? Then state the one-sentence fix.

<details>
<summary><strong>Answer</strong></summary>

**Answer:** "Would not recommend" and "Not bad, but could be better" are both at risk (6 points)

**Explanation:** Both unseen examples require correctly handling a negation or hedge
("would not," "not bad, but"), and the shown few-shot set contains no example of that
language pattern — only unambiguous positive/negative cases. "Fantastic purchase..." is
low risk because it closely matches the shown positive example.

**Fix:** Add at least one negated or hedged example per label to the few-shot set.

**Misconception:** That two examples (one clearly positive, one clearly negative) are
"enough" few-shot coverage regardless of what language patterns they actually demonstrate.

</details>

### Q7. Hand-classify (4 points)
**Difficulty:** Foundational · **Competency:** C1 · **Type:** Short answer

Classify each as Positive, Neutral, or Negative, the way you'd want a well-prompted model
to:

| Comment | Your label |
|---|---|
| a. "Neither good nor bad." | |
| b. "Packaging was damaged upon arrival." | |
| c. "Exceeded my expectations." | |
| d. "It does the job, but not great." | |

<details>
<summary><strong>Answer</strong></summary>

**Answer:** a: Neutral; b: Negative; c: Positive; d: Neutral (4 points)

**Explanation:** (a) cancels to neutral by design; (b) is an unambiguous product/shipping
complaint; (c) is unambiguous praise; (d) is a mixed/hedged statement that nets to neutral
rather than negative, despite "but not great" reading as a complaint on its own.

**Misconception:** Reading (d) as Negative because of "not great," ignoring that "does the
job" is a genuine (if lukewarm) positive claim about the product working.

</details>

### Q8. Theme the negative feedback (6 points)
**Difficulty:** Intermediate · **Competency:** C1, C6 · **Type:** Applied categorization

Northstar asked for **negative-feedback themes only** (Delivery, Pricing, Product Quality,
Customer Support). Assign each snippet to a theme, or mark it "does not belong" if it
isn't negative feedback at all:

1. "Delivery was late again. This keeps happening."
2. "Support team was slow to respond."
3. "Easy checkout experience. Very smooth!"
4. "Poor quality and overpriced."

<details>
<summary><strong>Answer</strong></summary>

**Answer:** 1: Delivery; 2: Customer Support; 3: Does not belong; 4: Product Quality (and/or Pricing) (6 points)

**Explanation:** (1) and (2) are grouped by meaning, not the literal words "delivery" or
"support." (3) is positive feedback and should be excluded from a negative-feedback
theming pass — including it would corrupt the count a support lead later acts on. (4)
spans quality and price; crediting either theme (or noting it spans both) is acceptable.

**Misconception:** Forcing every snippet into a theme, including ones that don't belong
there at all — a correct "does not belong" call is itself a scored outcome, not a skipped one.

</details>

### Q9. Spot real Question Refinement (4 points)
**Difficulty:** Intermediate · **Competency:** C1 · **Type:** Multiple choice

Which of these is an example of the Question Refinement pattern, not just a vague prompt?

A. "Help me reduce churn. Make it detailed."
B. "Help me reduce churn. Before answering, ask me 3–5 clarifying questions about what's driving it for us, then help me turn this into specific, measurable questions."
C. "You are a churn expert. Help me reduce churn."
D. "Reduce churn for me using the attached data."

<details>
<summary><strong>Answer</strong></summary>

**Answer:** B (4 points)

**Explanation:** Only (B) actually instructs the model to ask clarifying questions before
answering — the defining move of Question Refinement. (A) just asks for more detail in the
same unrefined direction, (C) is Persona, (D) adds data but no refinement step.

**Misconception:** Treating "be more specific" instructions as refinement, when the pattern
specifically means the *model* drives toward precision by asking, not the user restating
the same vague goal with more adjectives.

</details>

## Section 3 — Evaluation and FDE judgment (Q10–Q14)

### Q10. Beyond the accuracy gap (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Short answer

On the lab's 28-comment hand-labeled gold set, a naive keyword classifier scores 86%
accuracy (4 misses) and a few-shot-informed classifier scores 96% (1 miss). Besides the
accuracy gap itself, what is the **more important question** to ask before telling
Northstar "few-shot is better"?

<details>
<summary><strong>Answer</strong></summary>

**Answer (6 points):** Whether the two classifiers fail on the same *kind* of comment.

**Explanation:** The headline accuracy gap doesn't say whether the extra 10 points are
spread across genuinely hard cases (negation, hedging — meaningful, generalizable
improvement) or concentrated in one lucky template phrase (fragile, non-generalizable).
Also relevant: whether the failures are evenly costly — misreading a strongly negative
comment as neutral is a worse business error than a neutral/positive mixup, and an
accuracy percentage treats both the same.

**Misconception:** That a higher aggregate percentage is sufficient justification on its
own, independent of what specifically improved.

</details>

### Q11. Small-sample risk (6 points)
**Difficulty:** Intermediate · **Competency:** C4 · **Type:** Short answer

The gold set above is drawn from only ~28 unique phrasings out of 100 total rows (heavy
repetition), labeled by one person. Name **two** reasons this isn't yet a defensible claim
that "our few-shot prompt reaches 96% accuracy on customer feedback" in general.

<details>
<summary><strong>Answer</strong></summary>

**Strong answer (6 points, any two):** Small/non-representative sample; single-rater
labels; templated, repetition-heavy text.

**Explanation:** 28 unique phrasings is far too small a sample to generalize from; the
labels come from one person's judgment with no inter-rater check; and the comments
themselves are clean, short, single-sentence templates — real customer feedback includes
sarcasm, typos, multi-sentence reviews, and mixed sentiment within one comment that this
set doesn't test at all.

**Misconception:** That a clean accuracy number from a small illustrative exercise is
itself evidence ready to present to a customer as a validated result.

</details>

### Q12. Find the failure mode (6 points)
**Difficulty:** Advanced · **Competency:** C4 · **Type:** Failure analysis

A naive keyword rule flags any comment containing the word "recommend" as Positive. Using
*"Would not recommend to anyone."*, explain exactly why this rule fails, and name the
general class of language pattern it's blind to.

<details>
<summary><strong>Answer</strong></summary>

**Answer (6 points):** The rule ignores the negation "would not"; it's blind to
negation/polarity-flipping modifiers generally.

**Explanation:** The rule matches on the presence of the word "recommend" without
accounting for what precedes it. The same blindness affects any negated or hedged phrase
("never disappoints," "not bad," "wouldn't call it great") — the general class is
**negation/polarity-flipping language**, not a one-off bug specific to this sentence.

**Misconception:** Treating this as an isolated edge case rather than a predictable,
recurring class of failure for any keyword-only approach.

</details>

### Q13. Customer-facing recommendation (8 points)
**Difficulty:** Advanced · **Competency:** C6, C4 · **Type:** Communication

Write the 3–5 sentence note you'd send Northstar's VP of Support after running the lab's
churn and feedback analysis. Include the headline finding, one honest caveat about the
data or method, and a concrete next step.

<details>
<summary><strong>Answer</strong></summary>

**Example strong answer (8 points):**

"Our initial review found Northstar's overall churn rate is roughly 20%, and the clearest,
best-supported pattern is that customers with just one product churn at 28% versus 8% for
customers with two — across nearly 9,700 customers, so this is a strong signal. Two much
smaller groups (customers with 3 or 4 products, under 350 combined) show even higher
churn, but that group is too small to generalize from yet. The analysis used a
hand-reviewed sample and a prompt-driven read of the data, not a validated statistical
model, so treat the magnitude as directional rather than precise. I'd recommend we scope a
proper churn-driver analysis against the full account base next, starting with why
single-product customers churn at more than 3x the rate of two-product customers."

**Grading:** 3 points for a plainly stated headline finding; 3 points for an honest,
specific caveat (not a generic disclaimer); 2 points for a concrete, scoped next step.

**Misconception:** Either overstating the finding as proven, leading with the dramatic but
small-sample 100%-churn number instead of the large-sample finding, or hedging so heavily
the note gives the VP nothing to act on.

</details>

### Q14. When prompt-only stops being enough (6 points)
**Difficulty:** Advanced · **Competency:** C2, C6 · **Type:** Judgment

Northstar liked the prompt-driven churn summary so much that they now want the same
prompt to automatically decide which at-risk customers get a retention discount, running
nightly with no human review. Is a prompt-only workflow still the right tool? Justify your
answer in 2–3 sentences, and name which later session — S01 or S02 — covers the mechanism
that's now missing.

<details>
<summary><strong>Answer</strong></summary>

**Answer (6 points):** No, not as-is; S01 and S02 are both relevant.

**Explanation:** The moment the output directly triggers an unreviewed business action
(issuing a discount) on a recurring, automated schedule with no human check, this has
become a production decision system, not a one-off analytical read. That needs the
verification/harness mechanics from **S01** (who's allowed to act, bounded retries, when to
escalate to a human) and/or the typed, validated decision contract from **S02** (a
structured, checked output the business process can safely consume). Naming either session
with correct reasoning earns full credit; naming both with the distinction between them
earns the strongest answer.

**Misconception:** That because the prompt "worked" for the one-off summary, it's already
fit for an automated, consequential, recurring decision.

</details>

---

## Submission checklist

- [ ] I matched each situation in Q2/Q9 to the pattern that closes that specific gap, not just a plausible-sounding one.
- [ ] I identified which comments are at risk *before* expanding the answer, based on what the few-shot examples actually demonstrate.
- [ ] I treated an accuracy percentage as the start of the evaluation question, not the end of it.
- [ ] I named a concrete next step in the customer-facing note, not just a restated finding.
- [ ] I recognized the specific signal that moves a task out of "prompt-only is enough."

## 🔍 Interpret your results

**Suggested self-assessment ranges (not certification thresholds):** 60–70 strong; 48–59
developing; 0–47 revisit relevant concepts. These are not empirically validated cut
scores.

**Diagnose by concept:**
- Q1, Q2, Q4, Q9: pattern identification and what each pattern actually guarantees.
- Q3, Q5, Q8: writing an effective, well-scoped prompt for a stated need.
- Q6, Q7, Q12: predicting and explaining a specific failure mode.
- Q10, Q11: evaluation rigor and small-sample risk, applied to prompting instead of model choice.
- Q13, Q14: customer-facing communication and recognizing when prompt-only stops being enough.

**Coverage note:** This quiz assesses the six prompt patterns introduced in this session
and the judgment to evaluate and communicate their results — not agent loops, harness
design, or typed-output validation. Those remain **S01** and **S02** topics respectively.

> [!NOTE]
> The naive/few-shot accuracy figures in Q10 come from the lab's own deterministic
> mock-classifier run, not a real model. The comment snippets throughout are drawn from the
> lab's synthetic feedback set; the churn figures in Q13's example answer come from the
> lab's actual `data/churn_modelling.csv`.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
