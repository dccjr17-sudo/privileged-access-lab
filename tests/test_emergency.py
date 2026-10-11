import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from emergency_access import create_request, review_request


class EmergencyTests(unittest.TestCase):
    def setUp(self):
        self.policy = dict(account_id='PA100',target='APP-SERVER-01',safe_id='SAFE-WINDOWS-LAB',
                           requester_id='E101',approver_id='E999',max_duration_minutes=5)
        self.accounts = {'PA100': dict(target='APP-SERVER-01',safe_id='SAFE-WINDOWS-LAB')}
        self.args = ['E101','PA100','APP-SERVER-01',5,'INC-1001','Service outage; normal owner unavailable']

    def test_pending_no_access(self):
        result=create_request(self.accounts,self.policy,*self.args)
        self.assertEqual(result['status'],'PENDING')
        self.assertFalse(result['access_granted'])
        self.assertTrue(result['request_id'].startswith('BG-'))

    def test_invalid_scope_and_incident(self):
        for position,value in [(0,'E900'),(1,'PA103'),(2,'DB-SERVER-01'),(3,6),(3,0),(4,''),(4,'INC-abc'),(5,' ')]:
            args=self.args.copy(); args[position]=value
            with self.subTest(position=position,value=value):
                with self.assertRaises(ValueError): create_request(self.accounts,self.policy,*args)

    def test_safe_and_independent_approver(self):
        with self.assertRaises(ValueError): create_request({'PA100':dict(target='APP-SERVER-01',safe_id='OTHER')},self.policy,*self.args)
        with self.assertRaises(ValueError): create_request(self.accounts,dict(self.policy,approver_id='E101'),*self.args)

    def test_emergency_review_controls(self):
        record=create_request(self.accounts,self.policy,*self.args)
        approved=review_request(record,self.policy,'E999','approve','Incident verified')
        self.assertEqual(approved['status'],'APPROVED')
        self.assertFalse(approved['access_granted'])
        self.assertEqual(review_request(record,self.policy,'E999','deny','Not needed')['status'],'DENIED')
        for rec,user,reason in [(record,'E101','test'),(record,'E901','test'),(approved,'E999','test'),(record,'E999',' ')]:
            with self.assertRaises(ValueError): review_request(rec,self.policy,user,'approve',reason)
