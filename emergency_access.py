"""Separate fictional emergency requests; no real emergency access is issued."""
import argparse
import csv
import json
import re
import uuid
from datetime import datetime, timezone
from request_access import ROOT


def create_request(accounts, policy, requester, account, target, minutes, incident, reason):
    if requester != policy['requester_id']:
        raise ValueError('Requester is not designated for emergency access')
    if account != policy['account_id'] or target != policy['target']:
        raise ValueError('Account or target is outside the emergency policy')
    row = accounts.get(account)
    if not row or row['target'] != target or row.get('safe_id') != policy['safe_id']:
        raise ValueError('Emergency account does not match the safe inventory')
    if not 1 <= minutes <= policy['max_duration_minutes']:
        raise ValueError('Emergency duration must be 1 to 5 minutes')
    if not re.fullmatch(r'INC-[0-9]{4,12}', incident):
        raise ValueError('Incident reference must be INC- followed by 4 to 12 digits')
    if not reason.strip():
        raise ValueError('An outage reason is required')
    if requester == policy['approver_id']:
        raise ValueError('Emergency approver must be independent')
    return {
        'request_id': 'BG-' + uuid.uuid4().hex[:12], 'workflow': 'EMERGENCY',
        'requester_id': requester, 'account_id': account, 'target': target,
        'safe_id': policy['safe_id'], 'duration_minutes': minutes,
        'incident_reference': incident, 'reason': reason.strip(),
        'approver_id': policy['approver_id'], 'status': 'PENDING',
        'access_granted': False, 'post_use_review_status': 'NOT_DUE',
        'created_at': datetime.now(timezone.utc).isoformat(),
    }


def review_request(record, policy, reviewer, decision, reason):
    if record['workflow'] != 'EMERGENCY' or record['status'] != 'PENDING':
        raise ValueError('Only pending emergency requests can be reviewed')
    if reviewer == record['requester_id']:
        raise ValueError('Emergency self approval is not allowed')
    if reviewer != policy['approver_id'] or reviewer != record['approver_id']:
        raise ValueError('Reviewer is not the designated emergency approver')
    if decision not in ('approve', 'deny') or not reason.strip():
        raise ValueError('A valid decision and review reason are required')
    result = dict(record)
    result.update(status='APPROVED' if decision == 'approve' else 'DENIED', access_granted=False,
                  approval={'reviewer_id': reviewer, 'decision': decision, 'reason': reason.strip(),
                            'at': datetime.now(timezone.utc).isoformat()})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    request = commands.add_parser('request')
    for field in ('requester', 'account', 'target', 'incident', 'reason'):
        request.add_argument('--' + field, required=True)
    request.add_argument('--minutes', required=True, type=int)
    review = commands.add_parser('review')
    for field in ('request', 'reviewer', 'reason'):
        review.add_argument('--' + field, required=True)
    review.add_argument('--decision', choices=['approve', 'deny'], required=True)
    args = parser.parse_args()
    try:
        policy = json.loads((ROOT / 'data/emergency-policy.json').read_text(encoding='utf-8'))
        if args.command == 'review':
            if not re.fullmatch(r'BG-[0-9a-f]{12}', args.request):
                raise ValueError('Invalid emergency request ID')
            path = ROOT / 'runtime/emergency' / (args.request + '.json')
            record = json.loads(path.read_text(encoding='utf-8'))
            if record['request_id'] != args.request:
                raise ValueError('Request ID does not match its record')
            result = review_request(record, policy, args.reviewer, args.decision, args.reason)
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
            temporary.replace(path)
            print(f"Emergency request: {result['request_id']}")
            print(f"Reviewer: {args.reviewer} | Status: {result['status']}")
            print('Access granted: NO\nSimulation only: emergency decision recorded; session start is a separate step.')
            return
        with (ROOT / 'data/privileged-accounts.csv').open(newline='', encoding='utf-8-sig') as source:
            accounts = {row['account_id']: row for row in csv.DictReader(source)}
        record = create_request(accounts, policy, args.requester, args.account, args.target,
                                args.minutes, args.incident, args.reason)
        folder = ROOT / 'runtime/emergency'
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / (record['request_id'] + '.json')).open('x', encoding='utf-8') as output:
            json.dump(record, output, indent=2)
            output.write('\n')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Emergency request rejected: {error}\n')
    print(f"Emergency request: {record['request_id']}")
    print(f"Incident: {args.incident}")
    print(f"Requester: {args.requester} | Account: {args.account} | Target: {args.target}")
    print(f"Duration: {args.minutes} minutes | Emergency approver: {record['approver_id']} (Jordan)")
    print('Status: PENDING\nAccess granted: NO')
    print('Simulation only: separate emergency request saved; incident reference and identities are lab inputs.')


if __name__ == '__main__':
    main()
