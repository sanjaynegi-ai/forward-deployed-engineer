"""Course example: application owns tool authorization, execution, and verification."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Protocol

CATEGORIES = {"billing", "technical", "access", "general"}
CRITICAL_KEYWORDS = ("critical", "urgent", "down", "immediately")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@dataclass
class Decision:
    kind: str  # 'tool' or 'final'
    name: str | None = None
    arguments: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    call_id: str | None = None

class Model(Protocol):
    def decide(self, ticket: dict, observations: list[dict], feedback: list[str]) -> Decision: ...

def lookup_account(account_id: str, *, expected_account_id: str | None) -> dict:
    """Read-only, scoped synthetic lookup; never accept arbitrary file paths."""
    if not expected_account_id or account_id != expected_account_id:
        raise PermissionError("account lookup is outside ticket scope")
    records = json.loads((DATA_DIR / "accounts.json").read_text(encoding="utf-8"))
    if account_id not in records:
        return {"account_id": account_id, "found": False}
    return {"account_id": account_id, "found": True, **records[account_id]}

def create_escalation(
    ticket_id: str,
    account_id: str,
    reason: str,
    *,
    expected_ticket_id: str,
    expected_account_id: str | None,
    priority: str,
    is_premium: bool,
) -> dict:
    """A *write*, side-effecting tool -- unlike ``lookup_account``, calling this twice
    is not free. ``expected_ticket_id``, ``expected_account_id``, ``priority``, and
    ``is_premium`` are supplied by the application from trusted state (the current
    ticket and an already-authorized account lookup), never taken from the model's own
    tool-call arguments -- the same defense-in-depth pattern ``lookup_account`` uses for
    ``expected_account_id``. A model *claiming* an account is premium is not evidence;
    only a prior, authorized ``lookup_account`` observation is.
    """
    if ticket_id != expected_ticket_id:
        raise PermissionError("escalation ticket_id does not match the ticket being processed")
    if not expected_account_id or account_id != expected_account_id:
        raise PermissionError("escalation account_id is outside ticket scope")
    if not reason or not reason.strip():
        raise ValueError("escalation reason must be a non-empty string")
    if priority != "high":
        raise PermissionError("escalation requires a high-priority ticket")
    if not is_premium:
        raise PermissionError("escalation requires a premium-support account")
    return {"escalation_created": True, "ticket_id": ticket_id, "account_id": account_id, "reason": reason}


def verify(candidate: Any, ticket: dict, observations: list[dict]) -> list[str]:
    if not isinstance(candidate, dict):
        return ["candidate must be a JSON object"]
    errors = []
    if candidate.get("ticket_id") != ticket["ticket_id"]:
        errors.append("ticket_id must match input")
    if candidate.get("category") not in CATEGORIES:
        errors.append("category must be billing, technical, access, or general")
    if candidate.get("priority") not in {"low", "medium", "high"}:
        errors.append("priority must be low, medium, or high")
    if type(candidate.get("needs_human")) is not bool:
        errors.append("needs_human must be boolean")
    if candidate.get("evidence_source") not in {"ticket", "account_lookup"}:
        errors.append("evidence_source must be ticket or account_lookup")
    if candidate.get("evidence_source") == "account_lookup":
        if not any(o.get("found") and o.get("account_id") == ticket.get("account_id") for o in observations):
            errors.append("account_lookup evidence requires a successful authorized observation")
    return errors

class MockModel:
    """Deterministic teaching stand-in; not a real LLM."""
    def __init__(self, inject_invalid_first: bool = False):
        self.inject_invalid_first = inject_invalid_first
        self.calls = 0
    def decide(self, ticket: dict, observations: list[dict], feedback: list[str]) -> Decision:
        self.calls += 1
        if self.inject_invalid_first and not feedback and not observations:
            return Decision(kind="final", candidate={"ticket_id": ticket["ticket_id"], "category": "refunds"})
        if ticket.get("account_id") and not observations:
            return Decision(kind="tool", name="lookup_account", arguments={"account_id": ticket["account_id"]}, call_id=f"mock-{self.calls}")
        msg = ticket["message"].lower()
        category = "billing" if any(w in msg for w in ("billed", "charge", "invoice")) else "technical" if any(w in msg for w in ("crash", "error", "app")) else "general"
        priority = "high" if any(w in msg for w in CRITICAL_KEYWORDS) else "medium"
        account_obs = next((o for o in observations if o.get("found")), None)
        is_premium = bool(account_obs and account_obs.get("support_tier") == "premium")
        already_escalated = any(o.get("escalation_created") for o in observations)
        if priority == "high" and is_premium and not already_escalated:
            return Decision(
                kind="tool", name="create_escalation",
                arguments={"ticket_id": ticket["ticket_id"], "account_id": ticket["account_id"],
                           "reason": f"High-priority issue on a premium account: {ticket['message'][:60]}"},
                call_id=f"mock-{self.calls}",
            )
        return Decision(kind="final", candidate={
            "ticket_id": ticket["ticket_id"], "category": category, "priority": priority,
            "needs_human": priority == "high",
            "evidence_source": "account_lookup" if observations else "ticket",
        })

#: Tools authorized for this harness. Nothing the model requests outside this set is
#: ever executed -- a model-visible tool schema is a hint, not a security boundary.
TOOL_ALLOWLIST = {"lookup_account", "create_escalation"}

def run_agent(ticket: dict, model: Model, *, max_steps: int = 4) -> dict:
    observations: list[dict] = []
    feedback: list[str] = []
    trace: list[dict] = []
    seen_calls: set[str] = set()
    escalated_tickets: set[str] = set()  # ticket-level idempotency, independent of argument text
    for step in range(1, max_steps + 1):
        try:
            decision = model.decide(ticket, observations, feedback)
        except Exception as exc:
            trace.append({"step": step, "event": "model_error", "error": type(exc).__name__})
            break
        trace.append({"step": step, "event": "model_decision", "kind": decision.kind})
        if decision.kind == "tool":
            # A tool request is untrusted input, even when produced by a model.
            args = decision.arguments
            if decision.name not in TOOL_ALLOWLIST or not isinstance(args, dict):
                trace.append({"step": step, "event": "tool_denied", "reason": "unknown tool"})
                break

            if decision.name == "lookup_account":
                if set(args) != {"account_id"} or not isinstance(args["account_id"], str):
                    trace.append({"step": step, "event": "tool_denied", "reason": "invalid arguments"})
                    break
                fingerprint = f"lookup_account:{args['account_id']}"
                if fingerprint in seen_calls:
                    trace.append({"step": step, "event": "tool_denied", "reason": "repeated tool request"})
                    break
                seen_calls.add(fingerprint)
                try:
                    result = lookup_account(args["account_id"], expected_account_id=ticket.get("account_id"))
                except (PermissionError, OSError, ValueError) as exc:
                    trace.append({"step": step, "event": "tool_denied", "reason": type(exc).__name__})
                    break
                observations.append(result)
                trace.append({"step": step, "event": "tool_executed", "name": decision.name, "found": result.get("found")})
                continue

            # create_escalation: a side-effecting tool. Exact-argument fingerprinting
            # (above) is not enough here -- a second request for the SAME ticket with
            # DIFFERENT reason text would pass that check and still duplicate the side
            # effect. Idempotency must be keyed on the business entity (the ticket),
            # not on the literal tool call.
            if set(args) != {"ticket_id", "account_id", "reason"} or not all(
                isinstance(args[k], str) for k in ("ticket_id", "account_id", "reason")
            ):
                trace.append({"step": step, "event": "tool_denied", "reason": "invalid arguments"})
                break
            if args["ticket_id"] in escalated_tickets:
                trace.append({"step": step, "event": "tool_denied", "reason": "duplicate escalation for this ticket"})
                break
            account_obs = next((o for o in observations if o.get("found")), None)
            is_premium = bool(account_obs and account_obs.get("support_tier") == "premium")
            # Teaching simplification: this synthetic fixture has no stored severity
            # field, so the dispatcher derives "priority" the same way a real system's
            # trusted SLA/ticketing data would -- never from the model's own claim. In
            # a production system this would read a stored field, not re-run a keyword
            # heuristic; the point stands either way: authorization must come from the
            # application's trusted state, never from the model-supplied arguments.
            msg = ticket["message"].lower()
            priority = "high" if any(w in msg for w in CRITICAL_KEYWORDS) else "medium"
            try:
                result = create_escalation(
                    args["ticket_id"], args["account_id"], args["reason"],
                    expected_ticket_id=ticket["ticket_id"], expected_account_id=ticket.get("account_id"),
                    priority=priority, is_premium=is_premium,
                )
            except (PermissionError, ValueError) as exc:
                trace.append({"step": step, "event": "tool_denied", "reason": type(exc).__name__})
                break
            escalated_tickets.add(args["ticket_id"])
            observations.append(result)
            trace.append({"step": step, "event": "tool_executed", "name": decision.name})
            continue
        if decision.kind != "final":
            trace.append({"step": step, "event": "invalid_decision"})
            break
        errors = verify(decision.candidate, ticket, observations)
        if not errors:
            trace.append({"step": step, "event": "verification_passed"})
            return {"status": "accepted", "result": decision.candidate, "trace": trace}
        feedback = errors
        trace.append({"step": step, "event": "verification_failed", "errors": errors})
    return {"status": "needs_review", "reason": "no verified result within limits", "trace": trace}
