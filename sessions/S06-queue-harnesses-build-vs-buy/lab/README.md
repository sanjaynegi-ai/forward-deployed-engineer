# S06 — Northstar Queue Harness Lab

**Audience:** Experienced software professionals who have done S01. **Duration:** 90-minute live session, plus optional extensions. All data is synthetic.

## 💻 Quick start (VS Code terminal)

1. Open this folder in VS Code.
2. Install `uv` during pre-course onboarding; verify with `uv --version`.
3. Run `uv sync --group dev` (generates `uv.lock` if missing; commit it after resolution).
4. Run `uv run python main.py --mode queue --cap 3`. It processes the first 3 pending
   tickets, saves state, and tells you how many are still pending.
5. Run the exact same command again. It resumes from exactly where it left off — watch
   the task list printed at the start of the run to confirm nothing was lost or redone.
6. Run `uv run python main.py --mode queue --cap 3 --fail-first T-402 --fail-always T-406 --reset`
   to start over and watch a one-time failure (retried and resolved) and a chronic
   failure (eventually escalated) happen live. Keep running the same command until the
   queue reports `pending: 0`.
7. Run `uv run pytest` to execute the tests (17, covering idempotency, crash-safe
   resumption, bounded retry, chronic-failure escalation, and the no-lost-no-double-
   counted invariant).

`uv` may install the pinned Python 3.12 if not available; network access is required
for initial environment setup. The queue harness itself uses only the Python standard
library.

## 🧩 Concept map

- **State machine, not a loop with a counter:** every ticket is `pending`, `done`, or
  `needs_review` — the harness's entire job is moving tickets between these states
  correctly, under a cap, across however many times it's called.
- **Idempotency by construction:** once a ticket leaves `pending`, no code path in
  `work_queue` can touch it again — see `queue_harness/core.py`'s docstring for why this
  doesn't need a separate duplicate check, unlike S01's `create_escalation`.
- **Fresh subagent per item:** `decide_fn(ticket_id)` receives nothing but the ticket's
  identity — no shared history across items, by construction, not by convention.
- **Crash-safety, demonstrated live:** `main.py` persists the exact state `work_queue`
  mutates, after every run — the CLI's resume-across-restart behavior in step 5/6 above
  is the same property the test suite checks, made visible on the command line.

> [!NOTE]
> This lab does not re-teach how one ticket gets decided or verified — `decide_fn` here
> is a deterministic stand-in (`queue_harness/tickets.py`). If you want the model-
> directed decision and verification mechanics, see the **S01** lab
> (`../../S01-verified-agent-loops/lab/`).

## 🛠️ Checkpoints / exercises

**00 — Starter:** inspect `data/tickets.json`, `queue_harness/core.py`, and `main.py`;
run the queue uncapped (`uv run python main.py --mode queue --reset`) and confirm all 7
tickets finish in one run.

**01 — Capped runs:** use `--cap 2` repeatedly and trace, by hand, how `done`/`pending`
change after each run before checking the printed summary.

**02 — Transient failure:** use `--fail-first T-402`. Confirm it's `pending` after the
run that first attempts it, and `done` (with `attempts=2`) after the next run that
reaches it.

**03 — Chronic failure:** use `--fail-always T-406`. Confirm it takes exactly two runs
that reach it to become `needs_review`, and that a third run never attempts it again.

**04 — Idempotency:** after a ticket is `done`, add a `print` statement inside
`decide_fn` and confirm, by rerunning the CLI, that it never prints for that ticket
again — the skip happens before `decide_fn` is ever called.

**Challenge A:** Reintroduce the bug described in the handout's §3 (track attempts in a
separate, unpersisted dictionary instead of reading `state`) and confirm you can
reproduce "fail once, then fail forever across restarts" live, not just read about it.

**Challenge B:** Add a fourth ticket state, `cancelled`, reachable only from `pending`,
and update `report()`'s invariant to account for it without breaking any existing test.

**Challenge C:** Write a test that starts a queue, processes some tickets, serializes
the state, deserializes it into a *new* `QueueState` object (simulating a real restart
more literally than calling `work_queue` twice on the same object), and confirms the
queue still finishes correctly.

## 💻 Optional live model mode (requires credentials and provider validation)

1. Run `uv sync --group live --group dev`.
2. Copy `.env.example` to `.env` (create one if it doesn't exist) and set
   `OPENROUTER_API_KEY`. Never commit `.env`.
3. Replace `queue_harness/tickets.py`'s `decide_ticket` with a real single structured
   call (S02's `TicketDecision` contract), and rerun `main.py`.

The queue harness itself is completely unaware of whether `decide_fn` is a mock or a
real model call — that's the point of the `decide_fn` boundary. Swapping it is a
one-function change, not a change to anything in `queue_harness/core.py`.

> [!CAUTION]
> Providers differ in structured-output support; the live path is **not prevalidated**
> and may incur charges. Only ever use synthetic tickets, never real customer data.

## 🔍 Troubleshooting

- `uv` not found: complete pre-course installation and restart terminal.
- A ticket you expect to be `pending` shows as `done`: you're probably running against a
  saved `data/queue_state.json` from an earlier session — run with `--reset`.
- `--fail-first` seems to fail every run, not just once: this is the exact bug the
  handout's §3 describes if `get_attempt` isn't wired to the harness's persisted state —
  check `main.py`'s `decide_fn` construction.
- Tests fail after a local edit: run `uv run pytest -v` and check which invariant broke
  first — `test_report_never_loses_or_double_counts_a_ticket` and
  `test_invariant_holds_at_every_cap_size` are the two most likely to catch a state-
  machine regression early.

## ✅ Validation checklist

- [ ] `uv run pytest` passes all 17 tests.
- [ ] A capped CLI run leaves the correct number of tickets pending, and a repeat run
      resumes without reprocessing anything already `done`.
- [ ] `--fail-first` resolves to `done` within two runs; `--fail-always` resolves to
      `needs_review` within two runs that reach it, never more.
- [ ] No ticket is ever lost or double-counted (`done + needs_review + pending == total`
      on every reported run).
- [ ] No secrets or real customer data included.

## Scope / limitations

This is an instructional prototype, not a production queue system. `decide_fn`'s mock
implementation returns a fixed, correct-by-construction decision per ticket — it makes
no claim about real decision accuracy, which is S01's and S02's scope, not this one's.
The persistence mechanism is a single local JSON file, adequate for a teaching demo of
the resume-across-restart property but not a real durability guarantee at production
scale (a real system would need a transactional data store, not a flat file a
concurrent second process could corrupt). The fault-injection mechanism is a controlled
teaching tool, not a real chaos-engineering harness. The build-vs-buy comparison in the
handout's §5 is illustrative, not a benchmark of any specific real framework — the FDE
decision exercise asks you to design a real verification plan precisely because this
lab can't substitute for one.

---

## About the mentor

**Sanjay Negi** brings 23+ years of industry experience and helps experienced software engineers and technology leaders transition into high-value AI roles, including **AI Engineer**, **Forward Deployed Engineer**, and **GenAI Architect**. He has trained more than 1,100 experienced engineers.

<p align="center"><img src="../../../assets/diagrams/SkillUpWithSanjay.png" alt="SkillUp with Sanjay logo" width="60"></p>

<p align="center"><strong>#SkillUpWithSanjay</strong></p>

<p align="center"><a href="https://www.sanjaynegi.in" target="_blank" rel="noopener noreferrer">Website</a>&nbsp;&middot;&nbsp;<a href="https://www.linkedin.com/in/sanjay-negi-ai/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
