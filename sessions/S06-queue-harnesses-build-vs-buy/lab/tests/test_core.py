"""Tests for the queue harness itself — orchestration mechanics, not ticket decisions.

Every fake decide_fn here is deliberately trivial: the point is to prove the harness's
state machine, not to re-test business logic S01 and S02 already cover.
"""

import pytest

from queue_harness.core import QueueState, TransientError, report, with_fault_injection, work_queue


def always_succeeds(ticket_id):
    return {"category": "general", "priority": "low", "needs_human": False}


def always_fails(ticket_id):
    raise TransientError("simulated permanent failure")


def test_processes_pending_tickets_up_to_cap():
    state = QueueState.from_ticket_ids(["A", "B", "C"])
    result = work_queue(state, always_succeeds, cap=2)
    assert result == {"done": 2, "needs_review": 0, "pending": 1, "total": 3}


def test_leaves_remaining_tickets_pending_when_capped():
    state = QueueState.from_ticket_ids(["A", "B", "C"])
    work_queue(state, always_succeeds, cap=1)
    statuses = {tid: t.status for tid, t in state.tickets.items()}
    assert statuses == {"A": "done", "B": "pending", "C": "pending"}


def test_done_ticket_is_never_reprocessed():
    state = QueueState.from_ticket_ids(["A"])
    work_queue(state, always_succeeds)
    attempts_after_first_run = state.tickets["A"].attempts

    calls = []

    def spy(ticket_id):
        calls.append(ticket_id)
        return always_succeeds(ticket_id)

    work_queue(state, spy)  # simulates a restart on the same (already-done) state
    assert calls == []
    assert state.tickets["A"].attempts == attempts_after_first_run


def test_needs_review_ticket_is_never_reprocessed():
    state = QueueState.from_ticket_ids(["A"])
    work_queue(state, always_fails, max_attempts=1)
    assert state.tickets["A"].status == "needs_review"

    calls = []

    def spy(ticket_id):
        calls.append(ticket_id)
        raise TransientError("should never be called")

    work_queue(state, spy)
    assert calls == []


def test_transient_failure_retries_and_succeeds_within_budget():
    decide_fn = with_fault_injection(always_succeeds, fail_first={"A"})
    state = QueueState.from_ticket_ids(["A"])

    work_queue(state, decide_fn, max_attempts=2)  # attempt 1 fails, stays pending
    assert state.tickets["A"].status == "pending"
    assert state.tickets["A"].attempts == 1

    work_queue(state, decide_fn, max_attempts=2)  # attempt 2 succeeds
    assert state.tickets["A"].status == "done"
    assert state.tickets["A"].attempts == 2


def test_chronic_failure_escalates_after_max_attempts():
    decide_fn = with_fault_injection(always_succeeds, fail_always={"A"})
    state = QueueState.from_ticket_ids(["A"])

    work_queue(state, decide_fn, max_attempts=2)
    assert state.tickets["A"].status == "pending"

    work_queue(state, decide_fn, max_attempts=2)
    assert state.tickets["A"].status == "needs_review"
    assert state.tickets["A"].attempts == 2


def test_report_never_loses_or_double_counts_a_ticket():
    state = QueueState.from_ticket_ids(["A", "B", "C", "D"])
    work_queue(state, with_fault_injection(always_succeeds, fail_always={"B"}), max_attempts=1, cap=3)
    result = report(state)
    assert result["done"] + result["needs_review"] + result["pending"] == result["total"] == 4


def test_resuming_state_across_two_calls_completes_the_queue():
    state = QueueState.from_ticket_ids(["A", "B", "C"])
    work_queue(state, always_succeeds, cap=2)  # simulates a crash after 2 of 3

    resumed = QueueState.from_dict(state.to_dict())  # simulates reloading from disk
    final = work_queue(resumed, always_succeeds, cap=2)
    assert final == {"done": 3, "needs_review": 0, "pending": 0, "total": 3}


def test_decide_fn_receives_only_the_ticket_id():
    state = QueueState.from_ticket_ids(["A", "B"])
    seen_args = []

    def spy(*args, **kwargs):
        seen_args.append((args, kwargs))
        return always_succeeds(*args)

    work_queue(state, spy)
    assert all(args == (tid,) and kwargs == {} for (args, kwargs), tid in zip(seen_args, ["A", "B"]))


def test_zero_cap_processes_nothing():
    state = QueueState.from_ticket_ids(["A", "B"])
    result = work_queue(state, always_succeeds, cap=0)
    assert result == {"done": 0, "needs_review": 0, "pending": 2, "total": 2}


def test_empty_queue_returns_all_zero_report():
    state = QueueState.from_ticket_ids([])
    result = work_queue(state, always_succeeds)
    assert result == {"done": 0, "needs_review": 0, "pending": 0, "total": 0}


def test_one_failure_short_of_cap_still_pending_not_escalated():
    decide_fn = with_fault_injection(always_succeeds, fail_first={"A"})
    state = QueueState.from_ticket_ids(["A"])
    work_queue(state, decide_fn, max_attempts=3)
    assert state.tickets["A"].status == "pending"
    assert state.tickets["A"].attempts == 1


@pytest.mark.parametrize("cap", [1, 2, 3, 4, 5])
def test_invariant_holds_at_every_cap_size(cap):
    state = QueueState.from_ticket_ids(["A", "B", "C", "D", "E"])
    result = work_queue(state, with_fault_injection(always_succeeds, fail_always={"C"}), max_attempts=1, cap=cap)
    assert result["done"] + result["needs_review"] + result["pending"] == 5
