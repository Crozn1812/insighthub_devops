"""Validate captured runtime artifacts; no manufactured usage or verdicts."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def artifact(local_path: str) -> Path:
    """Use historical local originals or the tracked submission projection."""
    local = ROOT / local_path
    return local if local.exists() else ROOT / 'docs/evidence' / local.name


class RuntimeArtifactTests(unittest.TestCase):
    def setUp(self):
        self.final = json.loads(artifact('security/results/day6-final-results.json').read_text())
        self.cost = json.loads(artifact('evidence/day6-cost-final.json').read_text())
        self.workloads = json.loads(artifact('evidence/day6-finops-workloads.json').read_text())
        self.app = json.loads(artifact('evidence/day6-finops-insighthub.json').read_text())

    def test_exact_cost_request_coverage(self):
        expected = {r['request_id'] for r in self.final['results']}
        actual = [r['request_id'] for r in self.cost['entries']]
        self.assertEqual(len(expected), 70)
        self.assertEqual(len(actual), 70)
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(set(actual)), len(actual))

    def test_token_accounting_matches_actual_target(self):
        by_id = {r['request_id']: r for r in self.final['results']}
        for row in self.cost['entries']:
            for key in ('input_tokens', 'output_tokens'):
                self.assertIs(type(row[key]), int)
                self.assertGreaterEqual(row[key], 0)
                self.assertEqual(row[key], by_id[row['request_id']][key])

    def test_cost_schema_and_arithmetic(self):
        self.assertEqual(self.cost['currency'], 'USD')
        self.assertEqual(self.cost['mode'], 'real')
        self.assertGreater(self.cost['budget_usd'], 0)
        for row in self.cost['entries']:
            self.assertEqual(row['cost_usd'], (row['input_tokens'] * row['input_usd_per_million'] + row['output_tokens'] * row['output_usd_per_million']) / 1e6)
        self.assertEqual(self.cost['total_usd'], sum(r['cost_usd'] for r in self.cost['entries']))
        self.assertLessEqual(self.cost['total_usd'], self.cost['budget_usd'])

    def test_zero_cost_actual_resource_fields(self):
        for row in self.cost['entries']:
            usage = row['resource_usage']
            self.assertGreater(usage['duration_seconds'], 0)
            self.assertGreater(usage['memory_peak_bytes'], 0)
            self.assertIn('Windows Get-Process', usage['measurement_source'])

    def test_three_workloads_have_real_model_usage(self):
        rows = [self.app] + [r for r in self.workloads if r['http_status'] == 200]
        self.assertEqual({r['workload'] for r in rows}, {'insighthub', 'bot', 'coding'})
        for row in rows:
            self.assertTrue(row['request_id'])
            self.assertTrue(row['provider_response_id'])
            usage = row['usage']
            self.assertGreater(usage.get('prompt_tokens', usage.get('input_tokens')), 0)
            self.assertGreater(usage.get('completion_tokens', usage.get('output_tokens')), 0)
            self.assertEqual(row['provider_cost_usd'], 0)

    def test_real_budget_and_concurrent_results(self):
        bot = [r['http_status'] for r in self.workloads if r['workload'] == 'bot']
        self.assertEqual(bot, [200, 200, 429])
        concurrent = [r['http_status'] for r in self.workloads if r['label'] == 'concurrent-near-threshold']
        self.assertEqual(sorted(concurrent), [200, 429])
        ledger = json.loads(artifact('evidence/day6-finops-ledger.json').read_text())
        config = json.loads((ROOT / 'finops/budgets.json').read_text())
        for scope in ledger['scopes']:
            self.assertLessEqual(scope['used'], config['scopes'][scope['workload']]['max_budget_micro_usd'])


if __name__ == '__main__':
    unittest.main()
