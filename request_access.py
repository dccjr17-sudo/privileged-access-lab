"""Create a policy-checked fictional request without granting access."""
import argparse
import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def validate_request(accounts, policies, account_id, requester, target, minutes, purpose):
    if account_id not in accounts or account_id not in policies:
        raise ValueError("Account has no configured access policy")
    account, policy = accounts[account_id], policies[account_id]
    if policy["target"] != account["target"] or policy["approver_id"] != account["owner_id"]:
        raise ValueError("Policy does not match account inventory")
    if requester not in policy["allowed_requesters"]:
        raise ValueError("Requester is not allowed by this policy")
    if target != policy["target"]:
        raise ValueError("Target is not allowed by this policy")
    if not 1 <= minutes <= policy["max_duration_minutes"]:
        raise ValueError(f"Duration must be 1 to {policy['max_duration_minutes']} minutes")
    if purpose != policy["allowed_purpose"]:
        raise ValueError("Purpose must match the configured maintenance purpose")
    return policy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account", required=True)
    parser.add_argument("--requester", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--minutes", type=int, required=True)
    parser.add_argument("--purpose", required=True)
    args = parser.parse_args()
    with (ROOT / "data/privileged-accounts.csv").open(newline="", encoding="utf-8-sig") as source:
        accounts = {row["account_id"]: row for row in csv.DictReader(source)}
    policies = json.loads((ROOT / "data/access-policies.json").read_text(encoding="utf-8"))
    try:
        policy = validate_request(accounts, policies, args.account, args.requester, args.target, args.minutes, args.purpose)
    except ValueError as error:
        parser.exit(1, f"Request rejected: {error}\n")
    record = {
        "request_id": "PAM-" + uuid.uuid4().hex[:12],
        "account_id": args.account, "requester_id": args.requester,
        "target": args.target, "duration_minutes": args.minutes,
        "purpose": args.purpose, "approver_id": policy["approver_id"],
        "status": "PENDING", "access_granted": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    folder = ROOT / "runtime/requests"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / (record["request_id"] + ".json")).open("x", encoding="utf-8") as output:
        json.dump(record, output, indent=2)
        output.write("\n")
    print(f"Request: {record['request_id']}")
    print(f"Requester: {args.requester} | Jamie")
    print(f"Account: {args.account} | Target: {args.target}")
    print(f"Requested duration: {args.minutes} minutes")
    print(f"Approver: {policy['approver_id']} | Riley")
    print("Status: PENDING\nAccess granted: NO")
    print("Simulation only: request saved locally; no administrator access or credentials provided.")


if __name__ == "__main__":
    main()
