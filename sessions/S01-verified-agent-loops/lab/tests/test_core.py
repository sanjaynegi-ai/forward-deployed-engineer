import pytest
from triage.core import MockModel, Decision, lookup_account, run_agent, verify

DIRECT = {"ticket_id":"T-101","message":"I was billed twice this month","account_id":None}
LOOKUP = {"ticket_id":"T-104","message":"Duplicate charge on account A-204","account_id":"A-204"}

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
    candidate = {"ticket_id":"T-101","category":"billing","priority":"normal","requires_human_review":False,"evidence_source":"account_lookup"}
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
