import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from concurrent.futures import ThreadPoolExecutor
import unittest
from uuid import uuid4


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        os.environ['FINOPS_DB'] = str(Path(self.directory.name) / 'ledger.sqlite')
        os.environ['FINOPS_KEYS_FILE'] = str(Path(self.directory.name) / 'keys.json')
        self.keys = {name: uuid4().hex for name in ('insighthub', 'bot', 'coding')}
        Path(os.environ['FINOPS_KEYS_FILE']).write_text(json.dumps(self.keys))
        spec = importlib.util.spec_from_file_location('budget_under_test', Path(__file__).with_name('gateway.py'))
        self.gateway = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.gateway)
        self.gateway.connection().close()

    def tearDown(self):
        self.directory.cleanup()

    def test_three_distinct_scoped_identities(self):
        for scope, key in self.keys.items():
            self.assertEqual(self.gateway.identity('Bearer ' + key), scope)
        with self.assertRaises(self.gateway.HTTPException):
            self.gateway.identity('Bearer invalid')

    def test_budget_enforced(self):
        self.assertTrue(self.gateway.reserve('bot', str(uuid4())))
        self.assertTrue(self.gateway.reserve('bot', str(uuid4())))
        self.assertFalse(self.gateway.reserve('bot', str(uuid4())))
        self.assertTrue(self.gateway.reserve('coding', str(uuid4())))

    def test_concurrent_near_threshold_atomic(self):
        self.assertTrue(self.gateway.reserve('coding', str(uuid4())))
        with ThreadPoolExecutor(max_workers=8) as executor:
            outcomes = list(executor.map(lambda _: self.gateway.reserve('coding', str(uuid4())), range(12)))
        self.assertEqual(sum(outcomes), 1)
        with self.gateway.connection() as db:
            used = db.execute("SELECT used FROM scopes WHERE workload='coding'").fetchone()['used']
        self.assertEqual(used, self.gateway.CONFIG['scopes']['coding']['max_budget_micro_usd'])

    def test_repeated_correlation_cannot_charge_twice(self):
        identifier = str(uuid4())
        self.assertTrue(self.gateway.reserve('bot', identifier))
        with self.assertRaises(sqlite3.IntegrityError):
            self.gateway.reserve('bot', identifier)
        with self.gateway.connection() as db:
            used = db.execute("SELECT used FROM scopes WHERE workload='bot'").fetchone()['used']
        self.assertEqual(used, self.gateway.CONFIG['allocation_micro_usd_per_request'])

    def test_metrics_attribution_and_arithmetic(self):
        self.gateway.reserve('insighthub', str(uuid4()))
        metrics = self.gateway.metrics().body.decode()
        self.assertIn('workload="insighthub"', metrics)
        self.assertIn('allocation_usd_used{workload="insighthub",model="qwen3:4b"} 0.01', metrics)
        self.assertIn('allocation_usd_remaining{workload="insighthub",model="qwen3:4b"} 0.09', metrics)
        self.assertIn('provider_cost_usd_total{workload="insighthub",model="qwen3:4b"} 0', metrics)

    def test_app_final_answer_contract(self):
        self.assertEqual(self.gateway.final_answer_content('{"answer":"Supported fact."}'), 'Supported fact.')
        for value in ('not JSON', '[]', '{"answer":""}', '{"answer":42}', '{"answer":"fact","analysis":"extra"}'):
            with self.assertRaises(ValueError):
                self.gateway.final_answer_content(value)


if __name__ == '__main__':
    unittest.main()
