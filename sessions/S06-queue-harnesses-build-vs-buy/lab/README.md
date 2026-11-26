# S06 — Northstar Queue Harness Lab

## Why this lab exists

Earlier sessions decide one ticket at a time. A production workload must also answer a
different set of questions: Which ticket should run next? What happens when one attempt
fails? How does work resume after a completed run? How do we guarantee that no ticket is
lost, processed twice, or retried forever?

This lab builds a small queue harness around an already-defined ticket decision function.
The decision function is intentionally simple so you can focus on orchestration: persisted
state, capped batches, bounded retry, escalation, idempotency, and observable invariants.
All tickets and failures are synthetic and deterministic.

## What you will learn

By the end of the lab, you should be able to:

1. Model queued work as explicit states instead of an unstructured loop.
2. Process only a bounded number of pending items in one run.
3. Resume from state saved by an earlier completed run without reprocessing finished work.
4. Distinguish a transient failure from a chronic failure that needs human review.
5. Explain how idempotency follows from allowed state transitions.
6. State what this local harness proves—and what still requires a production queue or workflow system.

## How the pieces fit together

| File | Responsibility |
|---|---|
| `data/tickets.json` | Synthetic workload to be processed |
| `queue_harness/tickets.py` | Deterministic decision function for one ticket |
| `queue_harness/core.py` | Queue state, bounded processing, retries, and invariants |
| `main.py` | Command-line entry point and persistence between runs |
| `tests/test_core.py` | Executable checks for the harness guarantees |

## 💻 Quick start

Run these examples from this lab folder:

1. Run `uv run python main.py --mode queue --cap 3 --reset`. It starts a fresh queue,
   processes the first three pending
   tickets, saves state, and tells you how many are still pending.
2. Run `uv run python main.py --mode queue --cap 3` without `--reset`. It resumes from
   the saved state — watch
   the task list printed at the start to confirm finished tickets are not processed again.
3. Run `uv run python main.py --mode queue --cap 3 --fail-first T-402 --fail-always T-406 --reset`
   to start over and watch a one-time failure (retried and resolved) and a chronic
   failure (eventually sent to review). Repeat without `--reset` until the queue reports
   `pending: 0`.
4. Run `uv run pytest` to execute the automated checks.

The queue harness itself uses only the Python standard library.

## 🧩 Concept map

- **State machine, not just a loop with a counter:** every ticket is `pending`, `done`, or
  `needs_review` — the harness's entire job is moving tickets between these states
  correctly, under a cap, across however many times it's called.
- **Idempotency by construction:** once a ticket leaves `pending`, no code path in
  `work_queue` can touch it again — see `queue_harness/core.py`'s docstring for why this
  doesn't need a separate duplicate check, unlike S01's `create_escalation`.
- **Isolated decision per item:** `decide_fn(ticket_id)` receives only one ticket's
  identity, with no shared conversation history from other tickets.
- **Resume between completed runs:** `main.py` saves the state after `work_queue` returns.
  A later process can reload that file and continue. This demonstrates restartable batch
  processing, but not transaction-level recovery from a crash in the middle of a run.
- **Bounded failure handling:** one failed attempt leaves work pending; reaching the
  configured attempt limit moves it to `needs_review` instead of retrying forever.

> [!NOTE]
> This lab does not re-teach how one ticket gets decided or verified — `decide_fn` here
> is a deterministic stand-in (`queue_harness/tickets.py`). If you want the model-
> directed decision and verification mechanics, see the **S01** lab
> (`../../S01-verified-agent-loops/lab/`).

## 🛠️ Guided exercises

### 1. Read the state model

Inspect `TicketState`, `QueueState`, and `report()` in `queue_harness/core.py`. Before
running anything, write down the three allowed states and the invariant that must hold.

### 2. Process an uncapped queue

Run `uv run python main.py --mode queue --reset`. Confirm all seven tickets finish in one
run and that `done + needs_review + pending == total`.

### 3. Resume capped batches

Use `--cap 2` repeatedly. Predict how `done` and `pending` will change before each run,
then compare your prediction with the printed task list.

### 4. Observe a transient failure

Use `--fail-first T-402`. Confirm it remains `pending` after the
run that first attempts it, and `done` (with `attempts=2`) after the next run that
reaches it.

### 5. Observe a chronic failure

Use `--fail-always T-406`. Confirm it takes exactly two runs
that reach it to become `needs_review`, and that a third run never attempts it again.

### 6. Verify idempotency

After a ticket is `done`, add a temporary `print` statement inside
`decide_fn` and confirm, by rerunning the CLI, that it never prints for that ticket
again — the skip happens before `decide_fn` is ever called.

Remove the temporary print after the experiment.

## Extension challenges

**Challenge A:** Reintroduce the bug described in the handout's §3 (track attempts in a
separate, unpersisted dictionary instead of reading `state`) and confirm you can
reproduce "fail once, then fail forever across restarts" live, not just read about it.

**Challenge B:** Add a fourth ticket state, `cancelled`, reachable only from `pending`,
and update `report()`'s invariant to account for it without breaking any existing test.

**Challenge C:** Write a test that starts a queue, processes some tickets, serializes
the state, deserializes it into a *new* `QueueState` object (simulating a real restart
more literally than calling `work_queue` twice on the same object), and confirms the
queue still finishes correctly.

## 💻 Optional model-backed decision function

Replace `queue_harness/tickets.py`'s `decide_ticket` with a real single structured
call (S02's `TicketDecision` contract), and rerun `main.py`.

The queue harness itself is completely unaware of whether `decide_fn` is a mock or a
real model call — that's the point of the `decide_fn` boundary. Swapping it is a
one-function change, not a change to anything in `queue_harness/core.py`.

> [!CAUTION]
> Providers differ in structured-output support; the live path is **not prevalidated**
> and may incur charges. Only ever use synthetic tickets, never real customer data.

## 🔍 Troubleshooting the harness

- A ticket you expect to be `pending` shows as `done`: you're probably running against a
  saved `data/queue_state.json` from an earlier session — run with `--reset`.
- `--fail-first` seems to fail every run, not just once: this is the exact bug the
  handout's §3 describes if `get_attempt` isn't wired to the harness's persisted state —
  check `main.py`'s `decide_fn` construction.
- Tests fail after a local edit: run `uv run pytest -v` and check which invariant broke
  first — `test_report_never_loses_or_double_counts_a_ticket` and
  `test_invariant_holds_at_every_cap_size` are the two most likely to catch a state-
  machine regression early.

## ✅ Check your understanding

- [ ] The test suite passes.
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
concurrent second process could corrupt). State is saved only after a completed
`work_queue` call, so a process crash during a run can also lose that run's in-memory
progress. The fault-injection mechanism is a controlled teaching tool, not a real
chaos-engineering harness. The build-vs-buy comparison in the
handout's §5 is illustrative, not a benchmark of any specific real framework — the FDE
decision exercise asks you to design a real verification plan precisely because this
lab can't substitute for one.
