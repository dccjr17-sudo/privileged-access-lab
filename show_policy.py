"""Display fictional PAM inventory and policy; no system access is changed."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    with (ROOT / "data/privileged-accounts.csv").open(newline="", encoding="utf-8-sig") as source:
        accounts = {row["account_id"]: row for row in csv.DictReader(source)}
    policies = json.loads((ROOT / "data/access-policies.json").read_text(encoding="utf-8"))
    account = accounts["PA100"]
    policy = policies["PA100"]
    if policy["target"] != account["target"] or policy["approver_id"] != account["owner_id"]:
        raise ValueError("Policy target or approver does not match the inventory")
    print(f"Account: PA100 | {account['account_name']}")
    print(f"Type: {account['account_type']}")
    print(f"Target: {policy['target']}")
    print(f"Allowed requester: {', '.join(policy['allowed_requesters'])} (Jamie)")
    print(f"Approver: {policy['approver_id']} (Riley)")
    print(f"Maximum duration: {policy['max_duration_minutes']} minutes")
    print(f"Approval required: {'YES' if policy['approval_required'] else 'NO'}")
    print(f"Self approval allowed: {'YES' if policy['self_approval_allowed'] else 'NO'}")
    print(f"Purpose: {policy['allowed_purpose']}")
    print(f"Rotate after use: {'YES' if policy['rotate_after_use'] else 'NO'}")
    print("Simulation only: policy configuration displayed; enforcement is built in later steps.")


if __name__ == "__main__":
    main()
