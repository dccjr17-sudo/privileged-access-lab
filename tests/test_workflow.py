"""Deterministic checks of local simulation controls; no personal state modified."""
import copy
import csv
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from request_access import validate_request
from review_access import review
from start_session import start
from session_action import authorize
from close_session import close


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        with (ROOT / 'data/privileged-accounts.csv').open(newline='', encoding='utf-8-sig') as source:
            self.accounts = {r['account_id']: r for r in csv.DictReader(source)}
        self.policies = json.loads((ROOT / 'data/access-policies.json').read_text())
        self.now = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
        self.record = dict(request_id='PAM-000000000001', account_id='PA100', requester_id='E101',
                           target='APP-SERVER-01', duration_minutes=30, purpose='approved patch maintenance',
                           approver_id='E901', status='PENDING', access_granted=False)

    def approved(self):
        return review(self.record, self.accounts, self.policies, 'E901', 'approve', 'Approved maintenance')

    def active(self):
        return start(self.approved(), self.accounts, self.policies, 'E101', 'APP-SERVER-01', self.now)

    def check_action(self, record, user='E101', target='APP-SERVER-01', action='check_patch_status', now=None):
        return authorize(record, self.accounts, self.policies, user, target, action, now or self.now)

    def test_request_policy_boundaries(self):
        for duration in (1, 30):
            validate_request(self.accounts, self.policies, 'PA100', 'E101', 'APP-SERVER-01', duration, self.record['purpose'])
        for account,user,target,duration,purpose in [('PA999','E101','APP-SERVER-01',30,self.record['purpose']),
                ('PA100','E900','APP-SERVER-01',30,self.record['purpose']),
                ('PA100','E101','DB-SERVER-01',30,self.record['purpose']),
                ('PA100','E101','APP-SERVER-01',0,self.record['purpose']),
                ('PA100','E101','APP-SERVER-01',60,self.record['purpose']),
                ('PA100','E101','APP-SERVER-01',30,'other')]:
            with self.subTest(account=account,user=user,target=target,duration=duration,purpose=purpose):
                with self.assertRaises(ValueError):
                    validate_request(self.accounts,self.policies,account,user,target,duration,purpose)

    def test_independent_approval_and_denial(self):
        self.assertEqual(self.approved()['status'], 'APPROVED')
        self.assertFalse(self.approved()['access_granted'])
        denied = review(self.record,self.accounts,self.policies,'E901','deny','Not needed')
        self.assertEqual(denied['status'],'DENIED')
        for reviewer in ('E101','E900'):
            with self.assertRaises(ValueError):
                review(self.record,self.accounts,self.policies,reviewer,'approve','test')

    def test_repeat_review_and_blank_reason(self):
        for record,reason in [(self.approved(),'repeat'),(self.record,' ')]:
            with self.assertRaises(ValueError):
                review(record,self.accounts,self.policies,'E901','approve',reason)

    def test_session_requires_approval(self):
        for record in (self.record,dict(self.approved(),review={})):
            with self.assertRaises(ValueError):
                start(record,self.accounts,self.policies,'E101','APP-SERVER-01',self.now)

    def test_session_scope_and_repeat_start(self):
        for record,user,target in [(self.approved(),'E900','APP-SERVER-01'),
                                  (self.approved(),'E101','DB-SERVER-01'),
                                  (self.active(),'E101','APP-SERVER-01')]:
            with self.assertRaises(ValueError):
                start(record,self.accounts,self.policies,user,target,self.now)

    def test_timing_and_exact_expiration(self):
        active = self.active()
        self.assertEqual(datetime.fromisoformat(active['session']['expires_at']),self.now+timedelta(minutes=30))
        self.check_action(active)
        self.check_action(active,now=self.now+timedelta(minutes=30,microseconds=-1))
        for moment in (self.now-timedelta(microseconds=1),self.now+timedelta(minutes=30)):
            with self.assertRaises(ValueError):
                self.check_action(active,now=moment)

    def test_action_scope(self):
        for user,target,action in [('E900','APP-SERVER-01','check_patch_status'),
                                  ('E101','DB-SERVER-01','check_patch_status'),
                                  ('E101','APP-SERVER-01','delete_logs')]:
            with self.assertRaises(ValueError):
                self.check_action(self.active(),user,target,action)

    def test_closure_rotation_and_activity_block(self):
        closed=close(self.active(),'E101','Done',self.now)
        self.assertEqual(closed['status'],'CLOSED')
        self.assertFalse(closed['access_granted'])
        self.assertEqual(closed['credential_rotation']['current_version'],2)
        with self.assertRaises(ValueError): self.check_action(closed)
        with self.assertRaises(ValueError): close(closed,'E101','Repeat',self.now)

    def test_closure_authority_and_reason(self):
        for user,reason in [('E900','Done'),('E101',' ')]:
            with self.assertRaises(ValueError): close(self.active(),user,reason,self.now)

    def test_functions_preserve_input(self):
        original=copy.deepcopy(self.record)
        self.active()
        self.assertEqual(self.record,original)
        active=self.active(); original=copy.deepcopy(active)
        close(active,'E101','Done',self.now)
        self.assertEqual(active,original)


if __name__ == '__main__':
    unittest.main()
