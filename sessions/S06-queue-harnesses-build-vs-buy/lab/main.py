"""Northstar queue lab CLI.

Run `uv run python main.py --mode queue` repeatedly to watch one run resume exactly
where the last one left off — the same crash-safety property the test suite checks,
made visible on the command line.
"""

import argparse
import json
from pathlib import Path

from queue_harness.core import QueueState, with_fault_injection, work_queue
from queue_harness.tickets import decide_ticket, load_tickets

STATE_PATH = Path(__file__).parent / "data" / "queue_state.json"


def load_state(ticket_ids):
    """Resume from a saved state if one exists, otherwise start a fresh queue."""
    if STATE_PATH.exists():
        return QueueState.from_dict(json.loads(STATE_PATH.read_text(encoding="utf-8")))
    return QueueState.from_ticket_ids(ticket_ids)


def save_state(state):
    STATE_PATH.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")


def print_task_list(state):
    print("Task list:")
    for ticket_id, ticket in state.tickets.items():
        note = f" ({ticket.note})" if ticket.note else ""
        print(f"  [{ticket.status:^12}] {ticket_id}  attempts={ticket.attempts}{note}")


def main():
    parser = argparse.ArgumentParser(description="Work the Northstar ticket queue.")
    parser.add_argument("--mode", choices=["queue"], default="queue")
    parser.add_argument("--cap", type=int, default=None, help="Process at most this many pending tickets this run.")
    parser.add_argument("--fail-first", action="append", default=[], help="Ticket ID whose first attempt should simulate a one-time failure.")
    parser.add_argument("--fail-always", action="append", default=[], help="Ticket ID that should simulate a chronic failure (ends in escalation).")
    parser.add_argument("--reset", action="store_true", help="Discard saved state and start the queue over.")
    args = parser.parse_args()

    if args.reset and STATE_PATH.exists():
        STATE_PATH.unlink()
        print("Reset: cleared saved queue state.\n")

    tickets = load_tickets()
    ticket_ids = [t["ticket_id"] for t in tickets]
    state = load_state(ticket_ids)

    # get_attempt reads the harness's own persisted attempt count (loaded above from
    # queue_state.json), so fault injection stays correct across a process restart —
    # see with_fault_injection's docstring for why this matters.
    decide_fn = with_fault_injection(
        decide_ticket,
        fail_first=set(args.fail_first),
        fail_always=set(args.fail_always),
        get_attempt=lambda tid: state.tickets[tid].attempts,
    )

    print_task_list(state)
    print()
    result = work_queue(state, decide_fn, max_attempts=2, cap=args.cap)
    save_state(state)
    print()
    print_task_list(state)
    print()
    print(f"Run summary: {result}")
    if result["pending"] > 0:
        print(f"{result['pending']} ticket(s) still pending — run again to continue the queue.")
    else:
        print("Queue fully worked. Run again with --reset to start over.")


if __name__ == "__main__":
    main()
