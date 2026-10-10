"""Start a time-limited fictional session; no connection or OS access is made."""
import argparse
import csv
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from request_access import ROOT, validate_request


def start(record, accounts, policies, requester, target, now):
    if record['status'] != 'APPROVED' or 'session' in record:
        raise ValueError('An unused approved request is required')
    if requester != record['requester_id'] or target != record['target']:
        raise ValueError('Requester or target does not match the approved request')
    policy = validate_request(accounts, policies, record['account_id'], requester,
                              target, record['duration_minutes'], record['purpose'])
    approval = record.get('review', {})
    if (approval.get('decision') != 'approve' or
            approval.get('reviewer_id') != policy['approver_id'] or
            approval.get('reviewer_id') == requester):
        raise ValueError('A valid independent approval is required')
    result = dict(record)
    result.update(status='ACTIVE', access_granted=True,
                  session={'session_id': 'SES-' + uuid.uuid4().hex[:12],
                           'requester_id': requester, 'target': target,
                           'started_at': now.isoformat(),
                           'expires_at': (now + timedelta(minutes=record['duration_minutes'])).isoformat()})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    parser.add_argument('--requester', required=True)
    parser.add_argument('--target', required=True)
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
        result = start(record, accounts, policies, args.requester, args.target, datetime.now(timezone.utc))
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Session rejected: {error}\n')
    print(f"Request: {result['request_id']}")
    print(f"Session: {result['session']['session_id']}")
    print(f"Requester: {args.requester} | Target: {args.target}")
    print('Status: ACTIVE\nAccess granted: YES (simulated)')
    print(f"Expires at (UTC): {result['session']['expires_at']}")
    print('Simulation only: timed authorization saved locally; no server connection or real credentials.')


if __name__ == '__main__':
    main()
