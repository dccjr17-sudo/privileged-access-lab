"""Record fictional maintenance actions; never execute operating-system commands."""
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from request_access import ROOT, validate_request


def authorize(record, accounts, policies, requester, target, action, now):
    session = record.get('session', {})
    if record['status'] != 'ACTIVE' or not record.get('access_granted'):
        raise ValueError('An active session is required')
    if requester != record['requester_id'] or requester != session.get('requester_id'):
        raise ValueError('Requester does not match the session')
    if target != record['target'] or target != session.get('target'):
        raise ValueError('Target does not match the session')
    policy = validate_request(accounts, policies, record['account_id'], requester,
                              target, record['duration_minutes'], record['purpose'])
    started = datetime.fromisoformat(session['started_at'])
    expires = datetime.fromisoformat(session['expires_at'])
    if not started <= now < expires:
        raise ValueError('Session is expired or has not started')
    if action not in policy.get('allowed_actions', []):
        raise ValueError('Action is not allowed by the maintenance policy')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    parser.add_argument('--requester', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--action', required=True)
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
        now = datetime.now(timezone.utc)
        rejection = None
        try:
            authorize(record, accounts, policies, args.requester, args.target, args.action, now)
        except ValueError as error:
            rejection = str(error)
        record.setdefault('activity', []).append({
            'at': now.isoformat(), 'requester_id': args.requester, 'target': args.target,
            'action': args.action, 'outcome': 'DENIED' if rejection else 'ALLOWED',
            'detail': rejection or 'Fictional maintenance action recorded; no command executed',
        })
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Activity rejected: {error}\n')
    if rejection:
        parser.exit(1, f'Activity rejected: {rejection}\nAttempt recorded in local audit history.\n')
    print(f"Session: {record['session']['session_id']}")
    print(f'Requester: {args.requester} | Target: {args.target}')
    print(f'Action: {args.action}\nOutcome: ALLOWED (simulated)')
    print('Activity saved in local audit history. No command executed or server changed.')


if __name__ == '__main__':
    main()
