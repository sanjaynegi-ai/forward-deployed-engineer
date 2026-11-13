import argparse
import json
from pathlib import Path
from triage.core import MockModel, run_agent

def main():
    parser = argparse.ArgumentParser(description="Northstar support-ticket agent lab")
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    parser.add_argument("--ticket", default="T-104")
    parser.add_argument("--invalid-first", action="store_true", help="Inject a mock verification failure")
    parser.add_argument("--max-steps", type=int, default=4)
    args = parser.parse_args()
    tickets = json.loads((Path(__file__).parent / "data/tickets.json").read_text(encoding="utf-8"))
    ticket = next((t for t in tickets if t["ticket_id"] == args.ticket), None)
    if ticket is None:
        parser.error("unknown ticket ID")
    if args.mode == "live":
        from triage.live import LiveModel
        model = LiveModel()
    else:
        model = MockModel(inject_invalid_first=args.invalid_first)
    print(json.dumps(run_agent(ticket, model, max_steps=args.max_steps), indent=2))

if __name__ == "__main__":
    main()
