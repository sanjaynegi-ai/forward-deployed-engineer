# FDE Decision Exercise — Prompt Engineering Foundations

**Targets session:** S00 — Prompt Engineering Foundations
**Run after:** the lab's churn EDA and naive-vs-few-shot comparison (handout §1–§4), before
the handout's own closing stakeholder-note prompt. **This exercise formalizes and
replaces** the lighter "write the 3–5 sentence note" prompt already in the S00 lab's
Part 6 and quiz Q13 — same skill, now scoped with a full stakeholder brief.
**Timebox:** 10–15 minutes. **Artifact:** a one-page pre-engagement readout memo.

---

## 1. Customer situation

Northstar leadership has not yet funded a custom data pipeline or AI build. Before they
will, they've asked for two things in one week: a believable explanation of why customers
are churning, and a read on what customers' written feedback is actually about. There is
no signed data-processing agreement for a production integration — only two CSV exports
and a deadline. The deliverable has to come from a well-constructed prompt, not a build.

## 2. Customer stakeholder

**Northstar's VP of Support**, who will decide whether the engagement gets funded past
this first week. She has roughly 20 minutes to review your readout before her own
leadership meeting — she needs something she can act on or forward, not a raw data dump.

## 3. Business objective

Decide whether a larger AI engagement is worth funding, based on whether this first,
prompt-only read is credible, specific, and actionable — without spending any engineering
budget on a custom build yet.

## 4. Available information

- `churn_modelling.csv` — 10,000 synthetic-style bank customer records, including an
  `Exited` churn flag, geography, number of products held, tenure, and activity status.
- `user_comments.csv` — 100 customer feedback rows (~28 unique phrasings).
- A one-week timeline, no existing AI tooling, no production data-processing agreement.
- The six prompt patterns from this session's handout.

## 5. Missing information and reasonable assumptions

- No agreed definition of "churn driver" beyond the raw `Exited` flag — assume you're
  looking for the clearest, largest, best-supported pattern, not every statistically
  interesting one.
- No sign-off yet on what counts as "actionable" — assume the VP wants one headline
  finding and one concrete next step, not a full analysis.
- No guarantee the sample is representative of Northstar's full customer base — assume
  it's directional evidence, not a validated statistical result.
- No budget yet for engineering work — assume nothing you recommend can require funding
  that hasn't been approved.

## 6. Technical decision required

1. Which prompt pattern(s) actually fit this ask, and why — not every pattern, applied by
   default.
2. How to turn the raw churn numbers into a narrative a non-technical VP can act on in
   under a minute (Meta Prompt + Role + Structure, per the handout's §4).
3. **The decision this exercise is actually testing:** where does this prompt-only
   workflow stop being trustworthy enough to act on without further work — and what,
   specifically, would a real integration need that this prototype doesn't have?

## 7. Expected learner artifact

A **one-page pre-engagement readout memo**, four short sections, ~150–200 words total:

- **Headline finding** — the single clearest, best-supported pattern in the data.
- **Evidence** — the number(s) behind it, including sample size where it matters.
- **Caveat** — one honest, specific limitation of this method or data (not a generic
  disclaimer).
- **Recommended next step** — one concrete, scoped action, distinct from "build the full
  product."

## 8. Evaluation rubric

| Criterion | What a passing answer shows | Points |
|---|---|---:|
| Clarified business question | States what Northstar actually needs to decide (fund or not), not just "analyze the data" | 2 |
| Pattern choice justified | Names which pattern(s) were used and the specific gap each one closes — not "I used AI to look at it" | 3 |
| Headline finding is well-supported | Leads with the largest, best-supported pattern, not the most dramatic small-sample number | 3 |
| Honest, specific caveat | Names a real limitation (sample size, single-rater labels, template-like comments) — not a boilerplate hedge | 3 |
| Concrete next step | Scoped, specific, and distinct from "build everything now" | 2 |
| Recognizes the prompt-only boundary | States explicitly what would have to change (verification, a typed contract, or both) before this becomes an automated, recurring decision | 3 |
| **Total** | | **16** |

## 9. Instructor guidance

- **Timing:** 3 minutes to skim the data/prompts already run in the lab, 7 minutes to
  draft the memo, 3–5 minutes to compare answers in pairs or as a group.
- **Run it:** individually or in pairs, after the lab's Part 4 (churn EDA) and Part 2
  (naive-vs-few-shot) are both done — the memo should draw on real numbers from Part 4,
  not invented ones.
- **Watch for:** learners leading with the most dramatic number instead of the
  best-supported one (the lab's own churn data has exactly this trap — a 100%-churn
  group of 60 customers vs. a 27.7%-vs-7.6% pattern across ~9,700 customers). This is the
  single most common failure mode and is worth calling out explicitly if it appears.
- **Connects forward to:** the moment this memo's recommendation crosses from "a one-off
  read" into "an automated, recurring decision" is exactly where S01 (verification/
  harness) or S02 (typed contract) becomes necessary — point learners there if their
  "next step" already describes that crossing.

## 10. Example of a strong answer

> **Headline finding:** Northstar's overall churn rate is roughly 20%, and the clearest,
> best-supported pattern is that customers with one product churn at 27.7% versus 7.6%
> for customers with two products — across nearly 9,700 customers, a strong signal.
>
> **Evidence:** Two smaller groups (3–4 products, under 350 customers combined) show even
> higher churn, but are too small to generalize from without further review.
>
> **Caveat:** This read used a hand-reviewed sample and a prompt-driven pass over the
> data, not a validated statistical model — treat the magnitude as directional, not
> precise.
>
> **Next step:** Scope a focused churn-driver analysis on the full account base, starting
> with why single-product customers churn at more than 3x the two-product rate — not a
> full automated pipeline yet.

**Why it works:** leads with the large-sample finding over the dramatic small-sample one;
states a specific, real caveat; proposes a scoped, fundable next step; implicitly respects
the prompt-only boundary by not proposing automation yet.

## 11. Example of an inadequate answer, and why it fails

> "Our analysis shows that customers with 3+ products have up to 100% churn risk — this
> is a critical finding. We recommend immediately building an AI system that
> automatically flags and offers retention discounts to any at-risk customer, so Northstar
> never loses another customer like this again."

**Why it fails:**
- Leads with the dramatic, small-sample (under 350 customers) number instead of the
  large-sample, more decision-relevant one — exactly the trap the lab's own data sets.
- States the finding with no caveat about sample size or method.
- Jumps straight to "automatically flags and offers retention discounts" — a recurring,
  unreviewed, consequential business action — with zero acknowledgment that a prompt-only
  read isn't verified or contracted well enough to drive that kind of automation. This is
  precisely the crossing S00's handout §5 warns about, crossed without noticing it.
- Proposes an unscoped, unfunded full build as the "next step," not something Northstar
  could actually greenlight from a one-week engagement.
