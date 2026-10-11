"""Onboard fictional metadata into the CSV inventory; never create real accounts."""
import argparse
import csv
import io
import json
import re
from request_access import ROOT


def prepare(accounts, safes, account_id, name, target, account_type, owner, safe):
    if not re.fullmatch(r'PA[0-9]{3}', account_id):
        raise ValueError('Account ID must be PA followed by three digits')
    if not re.fullmatch(r'lab-[a-z0-9-]+', name):
        raise ValueError('Use a fictional account name beginning with lab-')
    if not re.fullmatch(r'[A-Z][A-Z0-9-]{1,63}', target):
        raise ValueError('Use a fictional target in uppercase letters, numbers, and hyphens')
    if safe not in safes:
        raise ValueError('Safe does not exist')
    policy = safes[safe]
    if account_type != policy['allowed_account_type']:
        raise ValueError('Account type is not allowed in this safe')
    if owner not in policy['allowed_owners']:
        raise ValueError('Owner is not allowed for this safe')
    if any(row['account_id'] == account_id for row in accounts):
        raise ValueError('Account ID already exists')
    if any((row['account_name'].casefold(), row['target'].casefold()) ==
           (name.casefold(), target.casefold()) for row in accounts):
        raise ValueError('Account name and target pair already exists')
    return dict(account_id=account_id, account_name=name, target=target,
                account_type=account_type, owner_id=owner,
                credential_reference='fictional-secret-' + account_id, safe_id=safe)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('account', 'name', 'target', 'type', 'owner', 'safe'):
        parser.add_argument('--' + field, required=True)
    args = parser.parse_args()
    try:
        safes = json.loads((ROOT / 'data/safes.json').read_text(encoding='utf-8'))
        path = ROOT / 'data/privileged-accounts.csv'
        with path.open(newline='', encoding='utf-8-sig') as source:
            accounts = list(csv.DictReader(source))
        record = prepare(accounts, safes, args.account, args.name, args.target, args.type, args.owner, args.safe)
        for row in accounts:
            if not row.get('safe_id'):
                matches = [safe for safe, policy in safes.items() if row['account_id'] in policy['seed_accounts']]
                if len(matches) != 1:
                    raise ValueError('Existing account needs an unambiguous safe assignment')
                row['safe_id'] = matches[0]
        buffer = io.StringIO(newline='')
        writer = csv.DictWriter(buffer, fieldnames=list(record))
        writer.writeheader()
        writer.writerows(accounts + [record])
        temporary = path.with_suffix('.tmp')
        temporary.write_text(buffer.getvalue(), encoding='utf-8', newline='')
        temporary.replace(path)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Onboarding rejected: {error}\n')
    print(f'Account: {args.account} | {args.name}')
    print(f'Target: {args.target} | Type: {args.type}')
    print(f'Safe: {args.safe} | Owner: {args.owner}')
    print('Status: ONBOARDED (metadata only)\nAccess granted: NO')
    print('Simulation only: CSV inventory updated; no real account or password created. A separate access policy is required.')


if __name__ == '__main__':
    main()
