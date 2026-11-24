# FDE Decision Exercise — Open-Weight and Local Deployment

**Targets session:** S05 — Open-Weight, Local Models, and Token Economics in Practice
**Run after:** the lab's Part A (model/deployment comparison) numbers are on the screen —
before the learner has had time to treat the closed model's accuracy win as the end of
the conversation.
**Timebox:** 10–15 minutes. **Artifact:** a constraint-first recommendation.

---

## 1. Customer situation

A prospect in a regulated industry wants to adopt Northstar's support-ticket triage
feature, but their security team has one non-negotiable requirement: ticket text may
never leave their own infrastructure, under any circumstances. Their trial ran the
closed, hosted configuration — the one that scored highest in this session's
comparison — and the account team, excited about the accuracy numbers, has told the
prospect "we'll make this work with the model you tested." Nobody on the account team
has yet registered that the model they tested cannot be deployed under the prospect's
actual requirement.

## 2. Customer stakeholders

**The account team** — focused on closing the deal, currently unaware that the trial's
winning configuration is architecturally incompatible with the stated requirement.
**The prospect's security team** — holds the actual non-negotiable requirement and will
reject any proposal that doesn't satisfy it, regardless of accuracy numbers.

## 3. Business objective

Close the deal on a configuration that actually satisfies the data residency
requirement, with the account team and the prospect both clear on what accuracy
trade-off that involves — before a contract gets signed on a configuration that can't
ship.

## 4. Available information

- The trial's three-way comparison: closed-hosted (10/10, highest cost), open-hosted
  (8/10), open-local (8/10, same accuracy as open-hosted, ~$0 marginal cost, slowest,
  needs several GB of local memory).
- The one ticket both open-weight configurations missed: a cross-referencing billing
  dispute requiring the model to judge which of two internal data sources to trust.
- The security team's requirement, stated exactly as: "ticket text may never leave our
  infrastructure."

## 5. Missing information and reasonable assumptions

- No confirmed hardware budget yet from the prospect for running a model locally —
  assume you'll need to ask what they can actually provision, not assume it's available.
- No measurement yet of how often real tickets resemble the one hard, cross-referencing
  case the trial missed — assume you don't know if it's rare or common in this
  prospect's actual ticket mix.
- No confirmed tolerance from the prospect for the accuracy gap — assume you'll need to
  present it, not assume it's automatically acceptable because the requirement forces
  the choice anyway.

## 6. Technical decision required

1. **Which configurations remain candidates** once the residency requirement is applied
   — and which is ruled out entirely, not just disadvantaged on cost.
2. **A recommendation from what's left**, with the real accuracy trade-off stated
   explicitly, not minimized.
3. **What has to be confirmed with the prospect** before committing — hardware budget,
   tolerance for the known capability gap, or anything else the trial doesn't yet answer.

## 7. Expected learner artifact

A short constraint-first recommendation, in four parts:

- **Elimination step** — which configuration(s) the residency requirement rules out
  outright, and why (architectural, not economic).
- **Recommendation from what remains** — which configuration you'd propose, with its
  real cost/latency/memory profile.
- **Named trade-off** — the specific accuracy gap being accepted, described concretely
  (what kind of ticket it affects), not just as a percentage.
- **Open items** — what must be confirmed with the prospect before this becomes a
  committed proposal.

## 8. Evaluation rubric

| Criterion | What a passing answer shows | Points |
|---|---|---:|
| Correctly eliminates on architecture, not cost | States the closed model is ruled out because it cannot avoid sending data off-premises — not because it's "too expensive" | 3 |
| Recommends from the actually-remaining options | Proposes open-weight local (or hosted, if the requirement is somehow reinterpreted) with its real profile, not a configuration already eliminated | 2 |
| Names the specific capability gap | Describes the cross-referencing failure mode concretely, not just "slightly less accurate" | 3 |
| Flags volume/representativeness as unknown | States that the real rate of hard cases in this prospect's traffic is unmeasured | 2 |
| Identifies a real open item | Names a genuine unconfirmed fact (hardware budget, tolerance) rather than a generic disclaimer | 3 |
| Account-team-appropriate tone | Written so a non-technical account team member can act on it, without losing the technical substance | 2 |
| **Total** | | **15** |

## 9. Instructor guidance

- **Timing:** 3 minutes to read the situation, 8 minutes to draft the four-part
  artifact, 3–4 minutes to compare eliminations and recommendations across pairs/groups.
- **The teaching hook:** make explicit that the account team's mistake — assuming the
  trial's winning configuration is automatically available — is exactly the "open vs.
  closed controls deployment, not accuracy" distinction from the handout's §1, now
  costing a real deal if it isn't caught before a contract is signed.
- **Watch for:** learners who recommend open-weight *hosted* as if it satisfies the
  requirement — it doesn't; data still leaves the premises to reach the hosting
  provider, just not to the original closed-model vendor. Only a local deployment
  satisfies "never leaves our infrastructure" as stated. Also watch for learners who
  skip naming the specific capability gap and just say "slightly less accurate" —
  that's not something a security-conscious customer can actually evaluate.
- **A reasonable canonical answer**, if you want one to anchor discussion: eliminate the
  closed model outright (any API call leaves the premises); eliminate open-weight
  hosted too, for the same reason, once the requirement is read literally; recommend
  open-weight local, with its ~80% trial accuracy and the specific named gap (cross-
  referencing disputes between two data sources); flag that the prospect's real hardware
  capacity and their tolerance for that specific failure mode are both still unconfirmed.

## 10. Example of a strong answer

> **Eliminated:** The closed model and the open-weight *hosted* configuration are both
> ruled out — both require a call to leave the customer's infrastructure to reach a
> provider, which the stated requirement forbids outright, regardless of either
> configuration's accuracy or cost.
>
> **Recommendation:** Open-weight, deployed locally on the customer's own hardware. In
> our trial this configuration matched the hosted open-weight version's accuracy exactly
> (8/10), at effectively zero marginal cost but noticeably higher latency and a real
> memory footprint the customer's infrastructure will need to support.
>
> **Named trade-off:** The one failure mode this configuration shares with open-weight
> hosted is a cross-referencing billing dispute — a ticket asking the model to decide
> which of two disagreeing internal numbers to trust. The closed model handled this
> correctly; both open-weight configurations did not. We don't yet know how often this
> customer's real tickets look like that case.
>
> **Open items:** Confirm the customer can actually provision the memory this deployment
> needs, and confirm their tolerance for the specific cross-referencing failure mode
> above before this becomes a committed proposal — not just their tolerance for "lower
> accuracy" in the abstract.

**Why it works:** the elimination step is architectural, not a cost comparison; the
recommendation names a real, specific failure mode instead of a vague accuracy
percentage; the open items are genuine unconfirmed facts, not a boilerplate disclaimer.

## 11. Example of an inadequate answer, and why it fails

> "Since they need everything on-prem, we'll just run the closed model locally too —
> it's still the most accurate one, and we can probably negotiate something with the
> vendor. If not, the open-weight hosted version is basically as secure since we trust
> our hosting provider anyway."

**Why it fails:**
- Closed-weight models are closed precisely because their weights aren't distributed —
  "running it locally" isn't a real option to negotiate; this answer doesn't actually
  grapple with what open-weight versus closed-weight controls (handout §1).
- Treating open-weight *hosted* as satisfying an on-premises requirement because "we
  trust our hosting provider" misses that the requirement is about where the data goes,
  not about how much the account team trusts whoever it goes to.
- No accuracy trade-off is named at all — the customer would be signing a contract
  without knowing what capability gap they're accepting, which is exactly the gap this
  exercise exists to surface before it becomes a production incident instead of a
  trial-stage conversation.
