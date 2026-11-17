import pytest
from triage.core import MockModel, Decision, create_escalation, lookup_account, run_agent, verify

DIRECT = {"ticket_id":"T-101","message":"I was billed twice this month","account_id":None}
LOOKUP = {"ticket_id":"T-104","message":"Duplicate charge on account A-204","account_id":"A-204"}
CRITICAL_PREMIUM = {"ticket_id":"T-110","message":"Critical: production integration is down, escalate immediately","account_id":"A-417"}
CRITICAL_STANDARD = {"ticket_id":"T-111","message":"Critical: integration is down, escalate immediately","account_id":"A-310"}

def test_single_call():
    out = run_agent(DIRECT, MockModel())
    assert out["status"] == "accepted"
    assert out["result"]["category"] == "billing"
    assert not any(t["event"] == "tool_executed" for t in out["trace"])

def test_tool_loop():
    out = run_agent(LOOKUP, MockModel())
    assert out["status"] == "accepted"
    assert any(t["event"] == "tool_executed" for t in out["trace"])

def test_verification_and_recovery():
    out = run_agent(DIRECT, MockModel(inject_invalid_first=True))
    assert out["status"] == "accepted"
    assert any(t["event"] == "verification_failed" for t in out["trace"])

def test_exhausted_budget_escalates():
    assert run_agent(DIRECT, MockModel(inject_invalid_first=True), max_steps=1)["status"] == "needs_review"

def test_account_scope():
    with pytest.raises(PermissionError):
        lookup_account("A-310", expected_account_id="A-204")

def test_unsupported_evidence():
    candidate = {"ticket_id":"T-101","category":"billing","priority":"medium","needs_human":False,"evidence_source":"account_lookup"}
    assert verify(candidate, DIRECT, [])

def test_unknown_tool_denied():
    class Malicious:
        def decide(self, *args):
            return Decision(kind="tool",name="delete_database",arguments={"account_id":"A-204"})
    out = run_agent(LOOKUP, Malicious())
    assert out["status"] == "needs_review"
    assert any(t["event"] == "tool_denied" for t in out["trace"])

def test_repeated_tool_request_stops():
    class Repeating:
        def decide(self, *args):
            return Decision(kind="tool",name="lookup_account",arguments={"account_id":"A-204"})
    out = run_agent(LOOKUP, Repeating())
    assert out["status"] == "needs_review"
    assert any(t.get("reason") == "repeated tool request" for t in out["trace"])


def test_escalation_authorized_and_executed():
    """Premium account + high-priority ticket: MockModel requests the lookup, then the
    escalation, then produces a final decision -- a real three-step tool-calling loop."""
    out = run_agent(CRITICAL_PREMIUM, MockModel())
    assert out["status"] == "accepted"
    assert out["result"]["priority"] == "high"
    assert out["result"]["needs_human"] is True
    assert any(t["event"] == "tool_executed" and t.get("name") == "create_escalation" for t in out["trace"])


def test_escalation_denied_without_premium_tier():
    """Same critical wording, but the account is standard tier -- escalation must not
    even be attempted by the mock, and the ticket still resolves to a human-reviewed
    final decision instead of silently escalating."""
    out = run_agent(CRITICAL_STANDARD, MockModel())
    assert out["status"] == "accepted"
    assert out["result"]["needs_human"] is True
    assert not any(t.get("name") == "create_escalation" for t in out["trace"])


def test_escalation_denied_for_non_premium_even_if_requested():
    """Directly test the dispatcher's own authorization, independent of what MockModel
    would ever request -- a model requesting escalation on a non-premium account must
    be denied before execution, not merely discouraged by the mock's own logic."""
    class RequestsEscalationAnyway:
        def __init__(self):
            self.step = 0
        def decide(self, ticket, observations, feedback):
            self.step += 1
            if self.step == 1:
                return Decision(kind="tool", name="lookup_account", arguments={"account_id": "A-310"})
            return Decision(kind="tool", name="create_escalation",
                             arguments={"ticket_id": "T-111", "account_id": "A-310", "reason": "forced escalation"})
    out = run_agent(CRITICAL_STANDARD, RequestsEscalationAnyway())
    assert out["status"] == "needs_review"
    assert any(t.get("reason") == "PermissionError" for t in out["trace"])


def test_duplicate_escalation_prevented():
    """The core duplicate-side-effect scenario: a model requests escalation for the same
    ticket twice, with DIFFERENT reason text each time -- exact-argument fingerprinting
    alone would miss this, since the arguments differ. Ticket-level idempotency must
    catch it anyway, and only one escalation may ever be created."""
    class EscalatesTwice:
        def __init__(self):
            self.step = 0
        def decide(self, ticket, observations, feedback):
            self.step += 1
            if self.step == 1:
                return Decision(kind="tool", name="lookup_account", arguments={"account_id": "A-417"})
            if self.step == 2:
                return Decision(kind="tool", name="create_escalation",
                                 arguments={"ticket_id": "T-110", "account_id": "A-417", "reason": "first escalation reason"})
            return Decision(kind="tool", name="create_escalation",
                             arguments={"ticket_id": "T-110", "account_id": "A-417", "reason": "a completely different second reason"})
    out = run_agent(CRITICAL_PREMIUM, EscalatesTwice(), max_steps=5)
    assert out["status"] == "needs_review"
    executed = [t for t in out["trace"] if t.get("event") == "tool_executed" and t.get("name") == "create_escalation"]
    denied = [t for t in out["trace"] if t.get("reason") == "duplicate escalation for this ticket"]
    assert len(executed) == 1, "exactly one escalation should ever be created for this ticket"
    assert len(denied) == 1, "the second, differently-worded request must still be caught"


def test_create_escalation_rejects_mismatched_ticket():
    with pytest.raises(PermissionError):
        create_escalation("T-999", "A-417", "reason", expected_ticket_id="T-110",
                           expected_account_id="A-417", priority="high", is_premium=True)


def test_create_escalation_rejects_empty_reason():
    with pytest.raises(ValueError):
        create_escalation("T-110", "A-417", "   ", expected_ticket_id="T-110",
                           expected_account_id="A-417", priority="high", is_premium=True)
