"""Timed fictional emergency activity, closure, and post-use review."""
import argparse
import csv
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from request_access import ROOT
from emergency_access import create_request
from close_session import close


def transition(record, accounts, policy, command, actor, target, action, reason, now):
    if record['workflow'] != 'EMERGENCY':
        raise ValueError('An emergency record is required')
    result = dict(record)
    if command == 'followup':
        if record['status'] != 'CLOSED' or record['post_use_review_status'] != 'PENDING':
            raise ValueError('A closed session with pending post-use review is required')
        if actor != policy['approver_id'] or actor == record['requester_id']:
            raise ValueError('Post-use review requires the independent emergency reviewer')
        if not reason.strip():
            raise ValueError('Post-use findings are required')
        result.update(post_use_review_status='COMPLETED',
                      post_use_review={'reviewer_id': actor, 'findings': reason.strip(), 'at': now.isoformat()})
        return result
    if actor != record['requester_id']:
        raise ValueError('Requester does not match the emergency request')
    if command == 'close':
        return close(record, actor, reason, now)
    create_request(accounts, policy, actor, record['account_id'], record['target'],
                   record['duration_minutes'], record['incident_reference'], record['reason'])
    if target != record['target']:
        raise ValueError('Target does not match the emergency request')
    if command == 'start':
        approval = record.get('approval', {})
        if record['status'] != 'APPROVED' or 'session' in record:
            raise ValueError('An unused approved emergency request is required')
        if approval.get('decision') != 'approve' or approval.get('reviewer_id') != policy['approver_id']:
            raise ValueError('Valid emergency approval is required')
        result.update(status='ACTIVE', access_granted=True, post_use_review_status='PENDING',
                      session={'session_id': 'BGS-' + uuid.uuid4().hex[:12],
                               'requester_id': actor, 'target': target, 'started_at': now.isoformat(),
                               'expires_at': (now + timedelta(minutes=record['duration_minutes'])).isoformat()})
        return result
    if command != 'action':
        raise ValueError('Unknown emergency command')
    if record['status'] != 'ACTIVE' or not record['access_granted']:
        raise ValueError('An active emergency session is required')
    session = record['session']
    if actor != session['requester_id'] or target != session['target']:
        raise ValueError('Actor or target does not match the emergency session')
    if not datetime.fromisoformat(session['started_at']) <= now < datetime.fromisoformat(session['expires_at']):
        raise ValueError('Emergency session is expired or has not started')
    if action not in policy['allowed_actions']:
        raise ValueError('Action is outside the emergency recovery policy')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['start', 'action', 'close', 'followup'])
    parser.add_argument('--request', required=True)
    parser.add_argument('--actor', required=True)
    parser.add_argument('--target', default='')
    parser.add_argument('--action', default='')
    parser.add_argument('--reason', default='')
    args = parser.parse_args()
    try:
        if not re.fullmatch(r'BG-[0-9a-f]{12}', args.request):
            raise ValueError('Invalid emergency request ID')
        path = ROOT / 'runtime/emergency' / (args.request + '.json')
        record = json.loads(path.read_text(encoding='utf-8'))
        if record['request_id'] != args.request:
            raise ValueError('Request ID does not match its record')
        policy = json.loads((ROOT / 'data/emergency-policy.json').read_text(encoding='utf-8'))
        with (ROOT / 'data/privileged-accounts.csv').open(newline='', encoding='utf-8-sig') as source:
            accounts = {row['account_id']: row for row in csv.DictReader(source)}
        now = datetime.now(timezone.utc)
        rejection = None
        try:
            result = transition(record, accounts, policy, args.command, args.actor,
                                args.target, args.action, args.reason, now)
        except ValueError as error:
            rejection = str(error)
            result = dict(record)
        result['audit'] = list(record.get('audit', [])) + [{
            'at': now.isoformat(), 'command': args.command, 'actor_id': args.actor,
            'target': args.target, 'action': args.action,
            'outcome': 'DENIED' if rejection else 'ALLOWED',
            'detail': rejection or 'Simulated transition recorded',
        }]
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
        if rejection:
            parser.exit(1, f'Emergency operation rejected: {rejection}\nAttempt recorded in emergency audit history.\n')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Emergency operation rejected: {error}\n')
    print(f"Emergency request: {result['request_id']} | Incident: {result['incident_reference']}")
    print(f"Status: {result['status']}")
    print(f"Access granted: {'YES (simulated)' if result['access_granted'] else 'NO'}")
    if args.command == 'start':
        print(f"Expires at (UTC): {result['session']['expires_at']}")
    if args.command == 'action':
        print(f'Action: {args.action} | Outcome: ALLOWED (simulated)')
    if args.command == 'close':
        print('Fictional session credential version: 1 -> 2')
    print(f"Post-use review: {result['post_use_review_status']}")
    print('Simulation only: local metadata and audit updated; no real access or commands issued.')


if __name__ == '__main__':
    main()
