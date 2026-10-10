"""Review a fictional PAM request; reviewer IDs are lab inputs, not logins."""
import argparse
import csv
import json
import re
from datetime import datetime, timezone

from request_access import ROOT, validate_request


def review(record, accounts, policies, reviewer, decision, reason):
    if record['status'] != 'PENDING':
        raise ValueError('Only pending requests can be reviewed')
    if reviewer == record['requester_id']:
        raise ValueError('Self approval is not allowed')
    policy = validate_request(accounts, policies, record['account_id'], record['requester_id'],
                              record['target'], record['duration_minutes'], record['purpose'])
    if reviewer != policy['approver_id'] or reviewer != record['approver_id']:
        raise ValueError('Reviewer is not the assigned approver')
    if decision not in ('approve', 'deny') or not reason.strip():
        raise ValueError('A valid decision and nonempty reason are required')
    result = dict(record)
    result.update(status='APPROVED' if decision == 'approve' else 'DENIED',
                  access_granted=False,
                  review={'reviewer_id': reviewer, 'decision': decision, 'reason': reason.strip(),
                          'reviewed_at': datetime.now(timezone.utc).isoformat()})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    parser.add_argument('--reviewer', required=True)
    parser.add_argument('--decision', choices=['approve', 'deny'], required=True)
    parser.add_argument('--reason', required=True)
    args = parser.parse_args()
    try:
        if not re.fullmatch(r'PAM-[0-9a-f]{12}', args.request):
            raise ValueError('Invalid request ID')
        path = ROOT / 'runtime/requests' / (args.request + '.json')
        record = json.loads(path.read_text(encoding='utf-8'))
        if record['request_id'] != args.request:
            raise ValueError('Request ID does not match its record')
        with (ROOT / 'data/privileged-accounts.csv').open(newline='', encoding='utf-8-sig') as source:
            accounts = {row['account_id']: row for row in csv.DictReader(source)}
        policies = json.loads((ROOT / 'data/access-policies.json').read_text(encoding='utf-8'))
        result = review(record, accounts, policies, args.reviewer, args.decision, args.reason)
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Review rejected: {error}\n')
    print(f"Request: {result['request_id']}")
    print(f"Reviewer: {args.reviewer} | Riley")
    print(f"Status: {result['status']}")
    print('Access granted: NO')
    print('Simulation only: decision saved locally; an approved request requires a separate session start.')


if __name__ == '__main__':
    main()
