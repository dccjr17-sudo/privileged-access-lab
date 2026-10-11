import sys
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from emergency_access import create_request,review_request
from emergency_session import transition


class EmergencySessionTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,11,12,tzinfo=timezone.utc)
        self.policy=dict(account_id='PA100',target='APP-SERVER-01',safe_id='SAFE-WINDOWS-LAB',requester_id='E101',approver_id='E999',max_duration_minutes=5,allowed_actions=['restart_service'])
        self.accounts={'PA100':dict(target='APP-SERVER-01',safe_id='SAFE-WINDOWS-LAB')}
        self.pending=create_request(self.accounts,self.policy,'E101','PA100','APP-SERVER-01',5,'INC-1001','Outage')
        self.approved=review_request(self.pending,self.policy,'E999','approve','Verified')

    def run_transition(self,record,command,actor='E101',target='APP-SERVER-01',action='',reason='Exercise complete',now=None):
        return transition(record,self.accounts,self.policy,command,actor,target,action,reason,now or self.now)

    def test_session_approval_and_single_use(self):
        active=self.run_transition(self.approved,'start')
        for record in (self.pending,active):
            with self.assertRaises(ValueError): self.run_transition(record,'start')
        self.assertEqual(active['post_use_review_status'],'PENDING')

    def test_activity_scope_and_exact_expiry(self):
        active=self.run_transition(self.approved,'start')
        self.run_transition(active,'action',action='restart_service')
        for actor,target,action,now in [('E999','APP-SERVER-01','restart_service',self.now),('E101','DB-SERVER-01','restart_service',self.now),('E101','APP-SERVER-01','delete_logs',self.now),('E101','APP-SERVER-01','restart_service',self.now+timedelta(minutes=5)),('E101','APP-SERVER-01','restart_service',self.now-timedelta(seconds=1))]:
            with self.assertRaises(ValueError): self.run_transition(active,'action',actor,target,action,now=now)

    def test_closure_and_post_use_review(self):
        active=self.run_transition(self.approved,'start')
        closed=self.run_transition(active,'close')
        self.assertFalse(closed['access_granted'])
        self.assertEqual(closed['credential_rotation']['current_version'],2)
        self.assertEqual(closed['post_use_review_status'],'PENDING')
        completed=self.run_transition(closed,'followup','E999')
        self.assertEqual(completed['post_use_review_status'],'COMPLETED')
        self.assertEqual(completed['status'],'CLOSED')
        with self.assertRaises(ValueError): self.run_transition(closed,'action',action='restart_service')
        with self.assertRaises(ValueError): self.run_transition(completed,'followup','E999')

    def test_review_authority_and_timing(self):
        active=self.run_transition(self.approved,'start'); closed=self.run_transition(active,'close')
        for record,actor,reason in [(active,'E999','findings'),(closed,'E101','findings'),(closed,'E901','findings'),(closed,'E999',' ')]:
            with self.assertRaises(ValueError): self.run_transition(record,'followup',actor,reason=reason)

    def test_revalidation_and_cleanup(self):
        active=self.run_transition(self.approved,'start')
        self.accounts['PA100']['safe_id']='OTHER'
        with self.assertRaises(ValueError): self.run_transition(active,'action',action='restart_service')
        closed=self.run_transition(active,'close')
        self.assertFalse(closed['access_granted'])
