"""The 'subagent': decides one Northstar ticket. Not this session's content.

This is a deterministic stand-in, not a real model — S01 and S02 already teach how a
single decision gets made and verified. Here it exists only so `main.py` has something
real to plug into the queue harness as `decide_fn`.
"""

import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

# The gold decision for each ticket, as if a verified single call or agent loop (S01/S02)
# had already produced and validated it. The queue harness never sees this dict directly —
# only through decide_fn.
_DECISIONS = {
    "T-401": {"category": "billing", "priority": "medium", "needs_human": True},
    "T-402": {"category": "technical", "priority": "medium", "needs_human": False},
    "T-403": {"category": "access", "priority": "medium", "needs_human": False},
    "T-404": {"category": "general", "priority": "low", "needs_human": False},
    "T-405": {"category": "billing", "priority": "low", "needs_human": False},
    "T-406": {"category": "technical", "priority": "high", "needs_human": True},
    "T-407": {"category": "access", "priority": "high", "needs_human": True},
}


def load_tickets():
    """Load the ticket queue's IDs and text from data/tickets.json."""
    return json.loads((DATA / "tickets.json").read_text(encoding="utf-8"))


def decide_ticket(ticket_id):
    """The mock subagent: decide one ticket, with no knowledge of any other ticket."""
    if ticket_id not in _DECISIONS:
        raise KeyError(f"no decision defined for {ticket_id}")
    return dict(_DECISIONS[ticket_id])
