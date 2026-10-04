import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
queries = [
    ('Admitted requests by workload', 'sum by (workload) (insighthub_finops_requests_total)'),
    ('Input tokens by workload', 'sum by (workload) (insighthub_finops_input_tokens_total)'),
    ('Output tokens by workload', 'sum by (workload) (insighthub_finops_output_tokens_total)'),
    ('Local planning allocation used (USD credits; not billing)', 'insighthub_finops_allocation_usd_used'),
    ('Local planning allocation remaining (USD credits)', 'insighthub_finops_allocation_usd_remaining'),
    ('Denied requests by workload', 'sum by (workload) (insighthub_finops_denied_total)'),
    ('Real model usage', 'sum by (model) (insighthub_finops_requests_total)'),
    ('Model request duration total (seconds)', 'sum by (workload) (insighthub_finops_duration_seconds_total)'),
    ('Local Ollama provider cost USD (zero; excludes electricity)', 'insighthub_finops_provider_cost_usd_total'),
    ('Budget gateway sampled process peak RSS bytes (excludes model/GPU)', 'insighthub_finops_gateway_peak_rss_bytes'),
]
dashboard = {'uid': 'insighthub-day6-finops', 'title': 'InsightHub Day 6 - Local LLM Cost and Usage',
             'tags': ['insighthub', 'day6', 'local-only'], 'schemaVersion': 39, 'version': 1,
             'refresh': '15s', 'timezone': 'browser', 'time': {'from': 'now-1h', 'to': 'now'},
             'panels': [{'id': i + 1, 'title': title, 'type': 'timeseries',
                         'gridPos': {'h': 8, 'w': 12, 'x': (i % 2) * 12, 'y': (i // 2) * 8},
                         'targets': [{'refId': 'A', 'expr': expression}]} for i, (title, expression) in enumerate(queries)]}
destination = root / 'observability/grafana-dashboards/insighthub-day6-finops.json'
destination.write_text(json.dumps(dashboard, indent=2) + '\n')
configmap = {'apiVersion': 'v1', 'kind': 'ConfigMap',
             'metadata': {'name': 'insighthub-day6-finops-dashboard', 'namespace': 'monitoring',
                          'labels': {'grafana_dashboard': '1'}},
             'data': {'insighthub-day6-finops.json': json.dumps(dashboard)}}
(root / 'finops/dashboard-configmap.json').write_text(json.dumps(configmap, indent=2) + '\n')
print('Ten-panel dashboard and scoped ConfigMap generated.')
