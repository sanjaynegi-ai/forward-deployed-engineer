# Glossary

Terms this course defines or uses in a specific way, kept here once instead of being
redefined in every session that touches them. Standard engineering/AI terms (agent loop,
harness, verification, tool calling) are taught in depth where they're introduced and
aren't duplicated here — this file is only for terms the course itself coins.

### Loop Engineering
*(introduced in S01)*

This course's own umbrella term for **deliberately designing the feedback, stopping, and
improvement behavior around iterative agent execution** — what happens after a model
proposes a result or requests a tool: how failures produce specific feedback, when a retry
is justified, when to stop and escalate instead, and how a change gets measured before
it's kept.

It is **not** a universally standardized architecture or industry term. It names a
perspective that connects the agent loop (the mechanism), the harness (the controls around
it), and verification (the evidence a result is acceptable) — not a new runtime component.

Three sub-ideas sessions build on:
- **Event-driven continuation** — the next step happens because something meaningful
  changed (a tool result arrived, verification failed), not on a timer or an uncontrolled
  loop. Doesn't imply any particular messaging infrastructure.
- **Bounded retry/recovery** — a failure gets specific feedback and a limited number of
  attempts, then escalates; never an unbounded retry loop.
- **Hill-climbing** — measure a baseline, make one targeted change, measure again, keep the
  change only if it improves the chosen metric without violating constraints. A local
  search heuristic, not reinforcement learning, and vulnerable to small-sample noise and
  overfitting to the test set.

### Tiered Dispatch
*(introduced in S04)*

Routing a request to a **cheap technique by default**, and escalating to a more
expensive, higher-capability technique **only when a cheap signal says the cheap
technique's answer can't be trusted**. Not a new model or mechanism — a dispatch
decision between two techniques a system already has (e.g., S02's single structured
call and S01's verified agent loop).

Tiered dispatch is only as trustworthy as its routing signal. The signal has two
distinct failure directions, and they are not equally dangerous:
- **False "stay cheap"** — the signal wrongly trusts the cheap technique on a case it
  can't actually handle. This silently ships a wrong decision; nothing downstream
  catches it.
- **False "escalate"** — the signal wrongly distrusts the cheap technique on a case it
  could have handled. This only costs the extra expense of the escalated technique; the
  case still gets decided correctly.

A routing signal must be validated on representative, held-out data — specifically for
its false-negative ("stay cheap") rate — before it's trusted in production. A clean
separation on a small curated trial is a hypothesis about the signal, not evidence for
it.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
