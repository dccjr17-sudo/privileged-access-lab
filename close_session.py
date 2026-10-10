"""Close a local simulated session and record fictional credential rotation."""
import argparse
import json
import re
from datetime import datetime, timezone
from request_access import ROOT


def close(record, requester, reason, now):
    if record['status'] != 'ACTIVE' or 'session' not in record:
        raise ValueError('Only an active session can be closed')
    if requester != record['requester_id'] or requester != record['session']['requester_id']:
        raise ValueError('Requester does not match the session')
    if not reason.strip():
        raise ValueError('A closure reason is required')
    result = dict(record)
    result['session'] = dict(record['session'])
    result['session'].update(closed_at=now.isoformat(), close_reason=reason.strip())
    result.update(status='CLOSED', access_granted=False)
    result['credential_rotation'] = {
        'credential_reference': 'fictional-session-secret-' + record['session']['session_id'],
        'previous_version': 1, 'current_version': 2,
        'rotated_at': now.isoformat(),
        'scope': 'Fictional session credential metadata only; no account password changed',
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    parser.add_argument('--requester', required=True)
    parser.add_argument('--reason', required=True)
    args = parser.parse_args()
    try:
        if not re.fullmatch(r'PAM-[0-9a-f]{12}', args.request):
            raise ValueError('Invalid request ID')
        path = ROOT / 'runtime/requests' / (args.request + '.json')
        record = json.loads(path.read_text(encoding='utf-8'))
        if record['request_id'] != args.request:
            raise ValueError('Request ID does not match its record')
        result = close(record, args.requester, args.reason, datetime.now(timezone.utc))
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Closure rejected: {error}\n')
    print(f"Session: {result['session']['session_id']}")
    print('Status: CLOSED\nAccess granted: NO')
    print('Fictional session credential version: 1 -> 2')
    print('Simulation only: closure and rotation metadata saved together; no real password changed.')


if __name__ == '__main__':
    main()
