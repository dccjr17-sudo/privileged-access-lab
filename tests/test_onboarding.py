import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from onboard_account import prepare


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        with (ROOT / 'data/privileged-accounts.csv').open(newline='', encoding='utf-8-sig') as source:
            self.accounts = [r for r in csv.DictReader(source) if r['account_id'] != 'PA103']
        self.safes = json.loads((ROOT / 'data/safes.json').read_text())
        self.args = ['PA103','lab-server-admin-02','APP-SERVER-02','LocalAdministrator','E901','SAFE-WINDOWS-LAB']

    def test_valid_metadata(self):
        row = prepare(self.accounts,self.safes,*self.args)
        self.assertEqual(row['safe_id'],'SAFE-WINDOWS-LAB')
        self.assertEqual(row['credential_reference'],'fictional-secret-PA103')
        self.assertNotIn('access_granted',row)

    def test_duplicates(self):
        for args in [ ['PA100']+self.args[1:], ['PA103','lab-server-admin','APP-SERVER-01']+self.args[3:] ]:
            with self.assertRaises(ValueError): prepare(self.accounts,self.safes,*args)

    def test_safe_type_and_owner(self):
        for position,value in [(5,'UNKNOWN'),(3,'ServiceAccount'),(4,'E999')]:
            args=self.args.copy(); args[position]=value
            with self.assertRaises(ValueError): prepare(self.accounts,self.safes,*args)

    def test_invalid_identifiers(self):
        for position,value in [(0,'../PA103'),(1,'actual-admin'),(2,'invalid target')]:
            args=self.args.copy(); args[position]=value
            with self.assertRaises(ValueError): prepare(self.accounts,self.safes,*args)
