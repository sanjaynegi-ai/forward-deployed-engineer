"""The queue harness: orchestration mechanics only.

Deciding one ticket is S01's and S02's content, already taught. This module never
re-teaches that — `decide_fn` below is an injected callable, and the harness itself
knows nothing about tickets, categories, or priorities. It only knows: pending,
in-progress, done, or needs_review; how many attempts an item has had; and the one
invariant it enforces on every call: no item may be lost or double-counted.
"""

from dataclasses import dataclass, field


class TransientError(Exception):
    """Raised by decide_fn for a safe-to-retry failure (e.g., a tool timeout)."""


@dataclass
class TicketState:
    ticket_id: str
    status: str = "pending"  # "pending" | "done" | "needs_review"
    attempts: int = 0
    decision: dict | None = None
    note: str | None = None


@dataclass
class QueueState:
    tickets: dict[str, TicketState] = field(default_factory=dict)

    @classmethod
    def from_ticket_ids(cls, ticket_ids):
        """Build a fresh queue with every ticket pending."""
        return cls(tickets={tid: TicketState(ticket_id=tid) for tid in ticket_ids})

    def to_dict(self):
        """Serialize to a plain dict, for persisting between runs."""
        return {
            "tickets": {
                tid: {
                    "ticket_id": t.ticket_id,
                    "status": t.status,
                    "attempts": t.attempts,
                    "decision": t.decision,
                    "note": t.note,
                }
                for tid, t in self.tickets.items()
            }
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild from a dict previously produced by to_dict() — the resume path."""
        return cls(tickets={tid: TicketState(**fields) for tid, fields in data["tickets"].items()})


def work_queue(state: QueueState, decide_fn, max_attempts: int = 2, cap: int | None = None) -> dict:
    """Advance the queue by at most `cap` pending tickets.

    Every still-pending ticket gets exactly one attempt per call: `decide_fn(ticket_id)`
    is invoked, with no access to any other ticket's state or history — a fresh
    subagent, by construction, not by convention. A successful attempt marks the
    ticket "done" and records its decision. A failed attempt (decide_fn raises
    TransientError) either leaves the ticket "pending" for a future call, or, once
    `max_attempts` is reached, marks it "needs_review" instead of retrying forever.

    Idempotent and crash-safe: a ticket already "done" or "needs_review" is never
    reprocessed, even if this function is called again on the same state after a
    simulated restart — the state machine itself is what guarantees this, not a
    separate duplicate check.
    """
    processed = 0
    for ticket_id, ticket in state.tickets.items():
        if cap is not None and processed >= cap:
            break
        if ticket.status != "pending":
            continue

        ticket.attempts += 1
        try:
            ticket.decision = decide_fn(ticket_id)
        except TransientError as exc:
            ticket.note = f"attempt {ticket.attempts} failed: {exc}"
            if ticket.attempts >= max_attempts:
                ticket.status = "needs_review"
            processed += 1
            continue

        ticket.status = "done"
        ticket.note = None
        processed += 1

    return report(state)


def report(state: QueueState) -> dict:
    """Summarize the queue's state, enforcing the no-lost-no-double-counted invariant."""
    done = sum(1 for t in state.tickets.values() if t.status == "done")
    needs_review = sum(1 for t in state.tickets.values() if t.status == "needs_review")
    pending = sum(1 for t in state.tickets.values() if t.status == "pending")
    total = len(state.tickets)

    if done + needs_review + pending != total:
        raise AssertionError("a ticket was lost or double-counted — this must never happen")

    return {"done": done, "needs_review": needs_review, "pending": pending, "total": total}


def with_fault_injection(decide_fn, fail_first=frozenset(), fail_always=frozenset(), get_attempt=None):
    """Wrap decide_fn to deterministically simulate transient and chronic failures.

    fail_first: ticket IDs whose very first attempt raises TransientError, then
    succeeds on every attempt after that — a one-time tool hiccup.
    fail_always: ticket IDs that raise TransientError on every attempt — a chronic
    failure that should end in escalation, never an infinite retry.

    By default this wrapper tracks attempt numbers itself, in memory — fine within a
    single process (what the test suite exercises). A caller that restarts the process
    between calls (main.py's CLI, resuming from disk) must pass `get_attempt`, a
    callable that returns the *harness's own* persisted attempt count for a ticket —
    otherwise the injector's in-memory counter resets on every restart and "fail once,
    then succeed" quietly becomes "fail every time," independent of the harness's own
    (correctly persisted) bookkeeping. This is a real, easy-to-make bug, not a
    hypothetical one — building this lab caught exactly this mismatch.
    """
    internal_counts: dict[str, int] = {}

    def attempt_number(ticket_id):
        if get_attempt is not None:
            return get_attempt(ticket_id)
        internal_counts[ticket_id] = internal_counts.get(ticket_id, 0) + 1
        return internal_counts[ticket_id]

    def wrapped(ticket_id):
        attempt = attempt_number(ticket_id)
        if ticket_id in fail_always:
            raise TransientError(f"{ticket_id}: simulated chronic failure")
        if ticket_id in fail_first and attempt == 1:
            raise TransientError(f"{ticket_id}: simulated one-time failure")
        return decide_fn(ticket_id)

    return wrapped
