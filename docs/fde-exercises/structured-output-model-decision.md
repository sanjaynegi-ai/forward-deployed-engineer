# FDE Decision Exercise — Structured Outputs and Model Selection

**Targets session:** S02 — Structured Outputs and Model Selection
**Run after:** §2 (LLM operational vocabulary) and **before §3** (the Pydantic contract)
of the handout — the taxonomy decision below must exist *before* learners see the
contract's category enum, or the exercise just asks them to restate an answer they've
already read. **Timebox:** 10–15 minutes. **Artifact:** a contract-and-taxonomy
acceptance checklist.

---

## 1. Customer situation

Two earlier prototype scripts for Northstar's ticket-triage feature already disagree with
each other: one uses categories `{billing, technical, account, general}`, the other uses
`{billing, technical, access, other}` — and a third script names the human-escalation
field differently in each place it appears. Nobody did this on purpose; it happened
because no one ever wrote the taxonomy down and different people built different pieces
assuming their own version was obviously right. Northstar's downstream ticketing system
now needs to route automatically on whatever category comes back, and it needs **one**
answer, not two.

> [!NOTE]
> This situation is deliberately realistic, not exaggerated: it mirrors an actual
> inconsistency this course's own S01 and S02 lab materials had, between a `requires_human_review`
> field in one place, `needs_human` in another, and `requires_human` in a third — caught
> only by a later audit, not by a customer conversation that should have surfaced it on
> day one. That's exactly the gap this exercise is designed to close before it reaches
> production.

## 2. Customer stakeholder

**Northstar's Head of Support Operations** (talks about "account issues") and
**a representative from Engineering** (talks about "access issues" for the same
login/SSO problems) — two stakeholders who need to agree on one shared vocabulary before
any code ships.

## 3. Business objective

Ship a classification feature the downstream routing system can trust within the next
sprint — without the FDE unilaterally inventing category names that match neither
stakeholder's existing vocabulary, and without shipping a third, different taxonomy that
makes the disagreement worse.

## 4. Available information

- The Head of Support's informal usage: "account issues" for anything login/profile/
  subscription-related.
- Engineering's informal usage: "access issues" specifically for authentication/SSO
  failures, distinct from general account management.
- Two existing prototype scripts, each with its own category enum and its own name for
  the human-escalation flag (see the Note above).
- No agreed priority rubric yet either.

## 5. Missing information and reasonable assumptions

- No single documented source of truth exists yet — assume you get one 20-minute
  alignment conversation with both stakeholders (simulate it in your own reasoning) before
  you have to commit to a contract.
- No agreed definition yet of what makes a misclassification "critical" versus a minor
  error — assume the business cares most about a high-priority ticket being
  under-prioritized, not about every possible mismatch equally.
- No confirmed labeled evaluation set yet — assume you'll need one before recommending a
  model configuration, not just a demo run.

## 6. Technical decision required

1. **One canonical taxonomy** — category enum, priority enum, and a single name for the
   human-escalation field — that resolves, rather than ignores, the stakeholders'
   disagreement.
2. **A typed response contract** (Pydantic-style) implementing that taxonomy.
3. **A critical-error definition** — specifically, which kind of misclassification is
   unacceptable, not just "any mismatch."
4. **A model-comparison protocol** — same test set, same rubric, failures counted not
   discarded — and a recommendation with at least one explicit caveat.

## 7. Expected learner artifact

A short **acceptance-criteria checklist**, in four parts:

- **Taxonomy table** — final category names, priority values, and the escalation-flag
  field name, with one line each on which stakeholder's language it reconciles.
- **Contract sketch** — the field list and types (a few lines of Pydantic or equivalent
  pseudocode is fine; this isn't a full implementation exercise).
- **Critical-error definition** — one sentence, specific and severity-aware.
- **Model recommendation** — 2–3 bullets: which configuration, the evidence, and one
  caveat.

## 8. Evaluation rubric

| Criterion | What a passing answer shows | Points |
|---|---|---:|
| Taxonomy actually reconciles the conflict | Doesn't just pick one stakeholder's language and ignore the other — names how each side's concept maps into the final set | 3 |
| Contract is minimal and well-typed | Enumerated category/priority, boolean escalation flag, bounded text field — no untyped catch-alls | 2 |
| Critical-error definition is specific | Names a severity-aware failure (e.g., high-priority predicted as low), not just "any wrong category" | 3 |
| Model comparison uses evidence | Cites a specific measurement (agreement rate, critical-miss count), not "model B felt better" | 3 |
| Recommendation includes a real caveat | States a specific limitation (sample size, label source), not a generic disclaimer | 2 |
| Separates schema validity from correctness | Doesn't claim the contract itself proves the classification is right | 2 |
| **Total** | | **15** |

## 9. Instructor guidance

- **Timing:** 3 minutes to read the two conflicting stakeholder positions, 8 minutes to
  draft the checklist, 3–5 minutes to compare taxonomies across pairs/groups — expect
  genuine variation here, which is the point.
- **The teaching hook:** make the connection to the real course-material inconsistency
  explicit (see the Note in §1) — it's a concrete, true example of exactly the failure
  this exercise is rehearsing, and it lands harder than a purely hypothetical one.
- **Watch for:** learners who invent a taxonomy neither stakeholder suggested (common,
  and not automatically wrong, but they should be able to justify why it's better than
  reconciling the two given ones); learners who skip the critical-error definition
  entirely and jump straight to "which model is more accurate," missing that aggregate
  accuracy hides exactly this distinction (this session's §5–§7 content directly).
- **A reasonable canonical answer**, if you want one to anchor discussion: categories
  `{billing, technical, access, general}` (keeps engineering's more specific "access,"
  keeps support's broader "general" over the vaguer "other"), priority
  `{low, medium, high}`, escalation flag `needs_human: bool`.

## 10. Example of a strong answer

> **Taxonomy:** `billing`, `technical`, `access`, `general` — keeps Engineering's `access`
> (reconciles their SSO/login use case, which "account" was too broad to distinguish) and
> keeps Support's `general` (broader and clearer than an unqualified `other`). Priority:
> `low`/`medium`/`high`. Escalation flag: `needs_human: bool` (shorter and clearer than
> either prior script's name for it).
>
> **Contract:** `category: Literal[...]`, `priority: Literal[...]`, `needs_human: bool`,
> `summary: str` (bounded length).
>
> **Critical error:** a `high`-priority ticket predicted as `low` — this is the failure
> that actually costs Northstar (a missed urgent issue), not a `medium`/`high` mixup.
>
> **Recommendation:** Configuration A matches reference labels on 8/10 test tickets with
> zero critical misses; Configuration B matches 8/10 but has one critical miss.
> Recommend A, with the caveat that 10 tickets is too small a sample to treat this as a
> validated production accuracy figure — a larger, reviewed set is needed before
> committing.

**Why it works:** the taxonomy decision explicitly reconciles both stakeholders' real
vocabulary rather than picking a side; the critical-error definition is severity-specific;
the model recommendation is evidence-based with an honest caveat about sample size.

## 11. Example of an inadequate answer, and why it fails

> "We'll use categories `billing`, `technical`, `other`, and add a 5th category `access`
> too, so everyone's happy. The contract just needs `category` and `priority` as
> strings. Model B is better because it's more accurate. Ship it."

**Why it fails:**
- Adding a 5th category to avoid a decision isn't reconciliation — it reintroduces
  exactly the ambiguity (does an SSO issue go in `access` or `technical`?) the exercise
  asked to resolve, and still never addresses the human-escalation field-naming conflict
  at all.
- `category` and `priority` as unconstrained strings isn't a contract — nothing stops an
  out-of-enum value from reaching the downstream router, which is the entire problem this
  session's Pydantic section exists to prevent.
- "Model B is better because it's more accurate" with no critical-error analysis is
  exactly the aggregate-accuracy trap this session's §5–§7 warn against — it could be
  hiding a dangerous high-to-low priority miss behind a slightly better overall score.
- "Ship it" with no caveat presents an unvalidated small-sample comparison as a finished
  decision.
