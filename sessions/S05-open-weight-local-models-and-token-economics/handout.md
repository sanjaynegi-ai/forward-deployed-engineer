# S05 Learner Handout — Open-Weight, Local Models, and Token Economics in Practice

**AI-Focused Forward Deployed Engineering · Session 05 · 90 minutes**
**Case study:** Northstar Support Systems (fictional) · Where the model runs, and what you send it
**Prerequisites:** **S02: Structured Outputs and Model Selection** (the contract and the
task-first comparison discipline) and **S03: LLM Fundamentals** (tokens, context windows,
and why token counts — not word counts — drive cost). Independent of S01 and S04.

S02 taught you to compare model configurations on the same task instead of trusting a
leaderboard. This session adds two axes that comparison didn't touch: **which weights you
can actually put where**, and **how much of the context you send actually earns its
tokens**. Both turn out to move cost and latency more than swapping models does.

## 🎯 What you will learn

By the end of this session, you should be able to:

1. Distinguish an **open-weight** model from a **closed-weight** one, and explain what that distinction actually controls — not accuracy, but *where you're allowed to run it*.
2. Compare the same open-weight model **hosted** versus run **locally**, and explain why that choice changes cost, latency, and memory footprint without changing accuracy.
3. Measure what trimming a prompt's context to only the relevant reference material actually costs and saves, using real token counts, not estimates.
4. Explain why a smaller, more relevant context can be *more* accurate than a larger one — not just cheaper.
5. Treat data residency as a hard architectural constraint, separate from and sometimes overriding a cost-and-accuracy recommendation.

> [!NOTE]
> This session does not build a tool-using agent (S01) or compare single-call against
> agent-loop techniques (S04) — it holds the technique constant (a single structured
> call) and varies the model, where it runs, and what you send it.

## 1. 🧩 Open-weight versus closed-weight: a deployment question, not an accuracy question

| | Closed-weight | Open-weight |
|---|---|---|
| **Where can you run it?** | Only wherever the provider lets you call its API | Anywhere you have the hardware — their infrastructure, yours, or your customer's |
| **Can a customer's data stay entirely on their premises?** | No — a call always leaves the premises to reach the provider | Yes, if you run the weights locally |
| **Does "open-weight" mean free to run?** | N/A | No — compute, hosting, and operational burden still cost something; "open" is about licensing and portability, not about being free |

> [!IMPORTANT]
> Open-weight versus closed-weight controls **where you're allowed to deploy**, not how
> accurate the model is. A closed model can be more capable *and* categorically
> unavailable for an on-premises requirement — the two facts don't trade off against each
> other; the second one simply removes the first from consideration.

## 2. 🧩 Hosted versus local: same weights, different cost shape

Once a model is open-weight, you still choose *where* to run it: through a hosted
provider/router (like S02's and S04's examples so far), or locally, on your own or your
customer's hardware.

| | Hosted | Local |
|---|---|---|
| **Marginal cost per call** | Provider's per-token rate | Effectively zero once the hardware is paid for |
| **Latency** | Network round trip, provider's serving stack | No network hop, but bounded by your own hardware — often slower without a GPU |
| **Memory footprint** | Not your problem | Yours: the model has to actually fit in RAM/VRAM |
| **Does the data leave the premises?** | Yes | No |

**The same open-weight model, run hosted versus locally, should score identically on
accuracy** — it's the same weights. What changes is cost, latency, and memory. If a
comparison shows an accuracy *difference* between hosted and local for the supposedly
same model, suspect a quantization difference, a version mismatch, or a serving-stack
bug — not a deployment-location effect.

## 3. 💻 The same comparison discipline, one more axis

The lab reuses S02's exact measurement method — same tickets, same contract, same
scoring rule, change one variable at a time — on three configurations of the same
underlying classification task:

| Configuration | Capability | Self-hostable | Illustrative cost | Illustrative latency | Memory |
|---|---|---|---:|---:|---:|
| **Closed, hosted** | Highest | No | Highest $/1K tokens | Fastest | N/A |
| **Open-weight, hosted** | Lower on hard cases | Yes | Mid $/1K tokens | Mid | N/A |
| **Open-weight, local** | Same as open-hosted | Yes | ~$0 marginal | Slowest (CPU-bound) | Several GB |

On the lab's 10-ticket set, holding context constant (the full knowledge base, every
time):

| Configuration | Accuracy | Illustrative total cost | Illustrative total seconds |
|---|---:|---:|---:|
| Closed, hosted | 10/10 (100%) | ~17.7 units | ~5.3 s |
| Open-weight, hosted | 8/10 (80%) | ~7.1 units | ~7.1 s |
| Open-weight, local | 8/10 (80%) | ~0 units | ~31.9 s |

The two open-weight rows score **identically** — same weights, same errors, same two
missed tickets — exactly as §2 predicts. The closed model earns its higher cost on one
specific kind of ticket (§4 below); the deployment-location choice between the two
open-weight rows is a pure cost/latency/memory/data-residency trade-off, not an accuracy
one.

> [!WARNING]
> These are this lab's own illustrative units, not a benchmark of any real provider,
> model, or hardware. The *shape* — hosted-vs-local changes cost/latency/memory, not
> accuracy; open-vs-closed can change accuracy — is the lesson, not these specific
> numbers.

## 4. 🧩 What the closed model's accuracy edge is actually buying

The one ticket only the closed model gets right asks the reader to reconcile two
disagreeing internal data sources (a usage dashboard versus raw logs) before deciding
whose number to trust for billing. Both open-weight configurations default to treating
it as a simple dashboard glitch report — a plausible-sounding but wrong shortcut that a
less capable model takes under exactly this kind of cross-reference task.

That's a real, measured capability gap — not a knock against open-weight models in
general, just evidence about *this specific task's hardest case*. The recommendation
question is the same one S04 asked about technique: **what fraction of real traffic
looks like this hard case, and does that fraction justify the cost gap across the whole
queue, or only on the subset that needs it?**

## 5. 💻 Trimming context: real tokens, not estimates

Northstar's knowledge base has a short general-rules section plus one section per
category (billing, technical, access, general). The **full** prompt sends every section,
every time. The **trimmed** prompt sends only the general rules plus the one section
matching a cheap, already-available routing hint — the category the customer picked on
the support portal's own intake form, free to obtain, not something you had to
infer. (If this sounds familiar: it's the same cheap-signal idea **S04**'s tiered
dispatch used to route between techniques, applied here to selecting context instead.)

Measured with a real tokenizer on this lab's actual knowledge-base text:

| Context | Avg. tokens/ticket | Accuracy (open-weight, hosted) | Illustrative cost | Illustrative seconds |
|---|---:|---:|---:|---:|
| Full (every section) | ~355 | 8/10 (80%) | ~7.1 units | ~7.1 s |
| Trimmed (relevant section only) | ~171 | 9/10 (90%) | ~3.4 units | ~3.4 s |

Trimming cut tokens, cost, and latency by roughly **half** — unsurprising, since it's
sending half the text. The accuracy *improvement* is the less obvious result.

> [!IMPORTANT]
> One of the full-context errors is a **context-dilution** failure, not a capability
> limit: a ticket mentioning "401 errors" gets mis-routed to the access category only
> when the access section's unrelated "401 after an SSO change" rule is sitting in
> context to distract a less capable model. The trimmed prompt never includes that
> section for a technical-topic ticket, so the error can't happen. More context didn't
> just cost more here — it actively hurt. This is S02 §2's "attach everything" warning,
> with a concrete mechanism behind it instead of just an assertion.

## 6. 🧩 Data residency is a constraint, not a cost line

A customer's data-handling requirement — "ticket text may never leave our
infrastructure" — doesn't get weighed against cost and accuracy the way those two trade
against each other. It **rules out every closed-weight configuration outright**, no
matter how accurate, before cost ever enters the comparison. What's left to actually
choose between is open-weight hosted (data still leaves the premises, just to your own
infrastructure provider instead of a frontier lab) and open-weight local (data never
leaves at all) — and that choice is governed by exactly the residency requirement's exact
wording, not by which option scores better on the chart.

## 🛠️ Forward Deployed Engineer Decision Challenge

**Customer scenario:** A regulated-industry prospect will only sign if ticket text never
leaves their own infrastructure — full stop. Their current trial used the closed, hosted
configuration, which scored best on accuracy. Sales wants to know whether this deal is
even possible with "the good model," and if not, what the honest trade-off is.

**Engineering decision:** Rule out what the constraint actually rules out, recommend
what's left with real numbers, and state what capability gap the customer is actually
accepting.

**Your deliverable:** a constraint-first recommendation, ~10–15 minutes.

**Full exercise, rubric, and worked examples:**
[`docs/fde-exercises/open-weight-local-deployment-decision.md`](../../docs/fde-exercises/open-weight-local-deployment-decision.md)

## 7. 🔍 Common pitfalls

> [!WARNING]
> Watch for these five claims — each sounds reasonable and each is wrong.

- **"Open-weight means free."** The weights are free to license; the compute, hosting, and operations are not.
- **"Local deployment is always slower, so it's always worse."** It's a trade against cost, memory, and data residency — "worse" depends on which of those the customer actually cares about.
- **"The hosted and local versions of the same model should be compared on accuracy."** They're the same weights; a real accuracy difference there is a bug to find, not a result to report.
- **"A bigger context window means you should fill it."** This session measured a case where trimming context *improved* accuracy, not just cost — the model's job is easier with less irrelevant material, not harder.
- **"We can always just use the better model."** Not when a hard constraint — like data residency — removes it from the candidate list before cost or accuracy is even discussed.

## ✅ Check your understanding

1. Two configurations run the same open-weight model, one hosted and one locally, and get different accuracy. What does that difference actually tell you?
2. Why did trimming context *improve* accuracy on this lab's ticket set, not just lower cost?
3. A customer requires their data never leave their infrastructure. Does a slightly more accurate closed-weight model remain a candidate? Why or why not?
4. What's the difference between "open-weight" and "free to run"?
5. The closed model's accuracy edge showed up on exactly one of ten tickets. What production question does that single data point raise, that this lab's 10-ticket trial can't answer by itself?

<details>
<summary>Suggested answers</summary>

1. It tells you something is wrong — likely a quantization difference, a version
   mismatch, or a serving-stack bug — not that deployment location itself changed the
   model's capability. Same weights should produce the same accuracy.
2. Full context included an unrelated section whose own wording happened to distract a
   less capable model into mis-categorizing one ticket; trimming removed that
   distraction entirely, fixing the error rather than just shortening the prompt.
3. No — data residency rules out any configuration that requires data to leave the
   premises, which every closed-weight API call does by definition. The model's
   accuracy never enters that part of the decision.
4. "Open-weight" is a licensing/distribution fact about the model itself — you can run
   it anywhere you have the hardware. "Free to run" would mean zero cost to operate it,
   which compute, hosting, and operational burden make untrue in practice.
5. What fraction of real traffic actually looks like that one hard, cross-reference
   case — a single example on a 10-ticket trial can't establish a production rate, the
   same small-sample caution S02 and S04 already raised.

</details>

## 📚 Further reading

- This course's **S02: Structured Outputs and Model Selection** §5–§6 — the task-first comparison discipline this session reuses on a new axis.
- This course's **S03: LLM Fundamentals** §1, §6 — tokens, tokenization, and context windows, the mechanism this session's cost measurement is built on.
- [tiktoken](https://github.com/openai/tiktoken) — the tokenizer library this session's lab uses to measure real prompt token counts.

---

> [!TIP]
> **Expected takeaways:** where a model runs changes cost, latency, memory, and data
> residency — not accuracy. Which weights you run changes accuracy — and whether you're
> even allowed to self-host at all. Trimming context to what a ticket actually needs can
> cut cost *and* fix the kind of error irrelevant material causes, which is a different
> and more concrete claim than "shorter prompts are cheaper."

## 🗺️ What you have built, and what's next

**What you have built:** a three-way deployment comparison (closed-hosted, open-hosted,
open-local) on the same task, isolating accuracy effects (open vs. closed) from
cost/latency/memory effects (hosted vs. local); a measured, real-token comparison of full
versus trimmed context, including one concrete context-dilution failure fixed by
trimming, not just made cheaper.

**What limitations remain:** the one hard ticket establishes a capability gap exists, not
its real-traffic rate. The illustrative cost/latency/memory figures are this lab's own
invented stand-ins. The topic-hint used to trim context is assumed accurate here — a real
intake-form hint can be wrong, which would need its own validation, the same discipline
S04 applied to a routing signal.

**What a later session adds:** **S06: Queue Harnesses: Orchestrating at Scale, Build vs.
Buy** extends S01's single-item agent loop into one agent orchestrating an entire
queue — independent of the model/deployment choice this session makes. Neither session
depends on the other being read first.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
