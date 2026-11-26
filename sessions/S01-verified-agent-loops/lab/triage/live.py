"""Optional live OpenAI-compatible adapter. Validate provider and tool support before use."""
import json
import os
from .core import Decision

class LiveModel:
    """Adapt an OpenAI-compatible chat model to the ``core.Model`` interface."""

    def __init__(self):
        """Load credentials and create the optional live API client."""

        try:
            from dotenv import load_dotenv
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install optional packages: uv sync --group live") from exc
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY") or not os.getenv("OPENAI_MODEL"):
            raise RuntimeError("Set OPENAI_API_KEY and OPENAI_MODEL in .env")
        self.client = OpenAI()
        self.model = os.environ["OPENAI_MODEL"]
    def decide(self, ticket, observations, feedback):
        """Ask the live model for one tool request or one final JSON candidate."""

        instructions = ("Classify support ticket into billing, technical, access, general. "
          "Return final JSON with ticket_id, category, priority (low/medium/high), "
          "needs_human (boolean), evidence_source (ticket/account_lookup). "
          "If ticket references account_id and no observations are available, request lookup_account. "
          "Never invent account information. Only cite account_lookup after successful observation. "
          "If the ticket is high priority AND a successful lookup_account observation shows a premium "
          "support_tier, you may request create_escalation once; never request it twice for the same "
          "ticket, and never claim an account is premium without a successful lookup_account observation.")
        messages = [{"role":"system","content":instructions}, {"role":"user","content":json.dumps({"ticket":ticket,"observations":observations,"verification_feedback":feedback})}]
        tools = [
            {"type":"function","function":{"name":"lookup_account","description":"Read synthetic account context for this ticket only","parameters":{"type":"object","properties":{"account_id":{"type":"string"}},"required":["account_id"],"additionalProperties":False}}},
            {"type":"function","function":{"name":"create_escalation","description":"Escalate a high-priority ticket on a premium-support account; the application re-checks authorization independently of these arguments","parameters":{"type":"object","properties":{"ticket_id":{"type":"string"},"account_id":{"type":"string"},"reason":{"type":"string"}},"required":["ticket_id","account_id","reason"],"additionalProperties":False}}},
        ]
        response = self.client.chat.completions.create(model=self.model,messages=messages,tools=tools,tool_choice="auto",temperature=0)
        message = response.choices[0].message
        if message.tool_calls:
            call = message.tool_calls[0]
            try:
                args = json.loads(call.function.arguments)
            except (ValueError,TypeError):
                args = None
            return Decision(kind="tool",name=call.function.name,arguments=args,call_id=call.id)
        try:
            candidate = json.loads(message.content or "")
        except (ValueError,TypeError):
            candidate = None
        return Decision(kind="final",candidate=candidate)
