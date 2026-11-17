# FDE Decision Exercise — Verified Agent Loops

**Targets session:** S01 — Verified Agent Loops
**Run after:** §5 (Verify, then decide what happens next) and before §7's hands-on
challenge in the handout — this exercise sets the authorization/escalation policy the
hands-on trace challenge then tests against. **Timebox:** 10–15 minutes. **Artifact:** a
workflow authorization-and-escalation design one-pager.

---

## 1. Customer situation

Northstar's Head of Support Operations saw a demo of the triage system looking up an
account and proposing a category, and now wants to go further: let "the AI" retrieve
account details **and** automatically route tickets end-to-end — including billing
disputes — without engineering reviewing most of them. Northstar's security/compliance
contact hasn't signed off on anything yet, and is specifically concerned about what
account data an automated workflow is allowed to touch.

## 2. Customer stakeholder

**Northstar's Head of Support Operations** (wants broad autonomy, measured by how much
manual routing work disappears) and **Northstar's Security/Compliance contact** (must
approve what data the workflow can access, measured by whether account-data exposure
stays bounded and auditable). Your recommendation has to satisfy both, not pick a side.

## 3. Business objective

Reduce manual ticket-routing work without creating an unreviewed channel for account-data
exposure or a wrong, consequential routing decision (for example, misrouting a billing
dispute to the wrong queue, or exposing one customer's account data while handling
another's ticket).

## 4. Available information

- An existing read-only `lookup_account` tool, scoped to a single account per call.
- Ticket categories and priority levels (reuse this course's canonical taxonomy:
  `billing`/`technical`/`access`/`general`; `low`/`medium`/`high`).
- A stated compliance constraint: a workflow may never view an account's data except the
  one tied to the ticket it's currently handling.
- No write-capable tools exist yet (no refund tool, no reassignment tool).

## 5. Missing information and reasonable assumptions

- No documented list yet of which actions should be fully automated versus
  human-reviewed — assume billing disputes specifically are more consequential than a
  routine access question, and should be treated more conservatively until proven
  otherwise.
- No agreed step or retry budget yet — assume an unbounded loop is never acceptable,
  regardless of what number you pick.
- No agreed definition yet of what counts as a "wrong" routing decision serious enough to
  need escalation — assume a wrong category costs less than a wrong account-data
  disclosure, and your policy should reflect that asymmetry.

## 6. Technical decision required

1. **Which tools are authorized** — and explicitly, which are not (yet).
2. **Prohibited actions**, stated specifically enough that a reviewer could check
   compliance against them (not "be careful with data").
3. **Verification rules** — what gets checked before a result is accepted, including
   both structural checks and the account-ticket authorization binding.
4. **Retry and stopping limits** — a concrete bound, not "retry until it works."
5. **Human escalation design** — what specifically triggers it.
6. **The recommendation this exercise is actually testing:** is a bounded tool-using
   loop even the right scope for this first phase, or does a simpler rules-based /
   single-call approach meet the actual need with less risk?

## 7. Expected learner artifact

A short **workflow authorization-and-escalation design** one-pager:

- Tool allowlist (what's authorized now).
- Prohibited actions (at least one, stated specifically).
- Verification checklist (schema + authorization/account-binding, not schema alone).
- Retry/stop policy (a number, plus what happens at the limit).
- Escalation triggers (specific conditions, not "when something seems wrong").
- One-line recommendation on autonomy level — bounded tool loop vs. simpler
  rules/single-call — with a reason.

## 8. Evaluation rubric

| Criterion | What a passing answer shows | Points |
|---|---|---:|
| Tools correctly scoped | Authorizes only the existing read-only lookup; does not invent or assume write capability that doesn't exist | 3 |
| Prohibited action is specific | Names a concrete forbidden case (e.g., looking up an account not tied to the current ticket) with a reason, not a vague caution | 3 |
| Verification includes authorization, not just schema | Explicitly checks the account-ticket binding, not only field types/enum membership | 3 |
| Retry/stop policy is bounded | Gives a specific limit and a defined terminal state (escalate/fail), not "retry until success" | 2 |
| Escalation trigger is concrete | Names specific conditions (e.g., billing-dispute category, or verification failure at retry limit), not "escalate when needed" | 2 |
| Autonomy recommendation is justified by risk/evidence | Gives a reasoned answer either way, not a reflexive "agents are better" or "agents are risky" | 2 |
| **Total** | | **15** |

## 9. Instructor guidance

- **Timing:** 3 minutes to read the two stakeholders' competing asks, 8 minutes to draft
  the one-pager, 3–5 minutes to compare, especially on the autonomy-level call, where
  reasonable answers can differ.
- **Run it right before** the handout's §7 hands-on trace challenge — that challenge
  tests whether a *given* trace violated the policy a learner just designed here, which
  makes the stakes of a vague policy concrete almost immediately.
- **Watch for the single most common failure:** treating the tool's existing schema (what
  arguments `lookup_account` accepts) as if it were the authorization boundary. It isn't —
  a schema only describes what a well-formed call looks like, not who's allowed to make
  it or on which account. This is this session's central warning, and this exercise is
  designed to surface it before learners see it fail in the hands-on trace.
- **On the autonomy-level question:** there's no single correct answer, but a strong
  answer treats billing disputes more conservatively than, say, a routine access
  question, and justifies that asymmetry rather than applying one policy uniformly for
  convenience.

## 10. Example of a strong answer

> **Authorized tools:** `lookup_account`, read-only, scoped to the account tied to the
> current ticket only.
>
> **Prohibited:** looking up any account other than the one tied to the current ticket,
> under any circumstance, including if the model claims it's needed — this is enforced in
> the tool dispatcher, not requested of the model via prompt.
>
> **Verification:** schema/enum checks on the final category and priority, **plus** a
> check that the looked-up account ID matches the ticket's own account ID before the tool
> result is trusted.
>
> **Retry/stop:** up to 2 retries with specific verifier feedback; on the third failure,
> return a structured `needs_review` result rather than a best-guess category.
>
> **Escalation triggers:** any billing-dispute ticket, regardless of model confidence
> (treated as inherently higher-consequence); any verification failure at the retry
> limit; any attempted out-of-scope account lookup (also an audit-log event, not just an
> escalation).
>
> **Recommendation:** start with the existing bounded, read-only tool loop for
> access/technical/general tickets, but route billing disputes to human review
> unconditionally for this first phase — the cost of a wrong billing decision is high
> enough that "the loop worked in testing" isn't sufficient evidence yet. Revisit once
> there's a measured track record on the lower-stakes categories.

**Why it works:** the prohibited action is specific and enforced in code, not prompted;
verification explicitly includes the authorization binding, not just schema; the
escalation trigger for billing disputes is a deliberate, justified asymmetry rather than a
uniform policy; the autonomy recommendation is staged and evidence-seeking, not a flat
yes or no.

## 11. Example of an inadequate answer, and why it fails

> "Give the agent the `lookup_account` tool with its existing schema — that already
> defines what arguments it takes, so it's safe. Let it retry until it gets a valid
> answer. Route everything automatically, including billing, since the demo worked well."

**Why it fails:**
- "The schema already defines what's safe" is exactly the misconception this session's
  handout calls out explicitly: a tool schema is not a security boundary. Nothing here
  stops the model from requesting a lookup on an unrelated account — the schema permits
  the argument shape, not the authorization.
- "Retry until it gets a valid answer" has no bound and no terminal failure state — an
  unbounded retry policy, exactly what this session's verification/recovery sections warn
  against.
- "Route everything automatically, including billing, since the demo worked well" treats
  a successful demo as equivalent to a validated, risk-appropriate production policy, and
  applies one autonomy level uniformly regardless of a billing dispute's higher
  consequence — no asymmetry, no staged rollout, no escalation path at all.
