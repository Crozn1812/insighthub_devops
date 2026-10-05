import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
# The reviewed native dashboard is the single source of truth. Regeneration
# must not replace its queries with the historical scoped-adapter metrics.
destination = root / 'observability/grafana-dashboards/insighthub-day6-finops.json'
dashboard = json.loads(destination.read_text())
if dashboard.get('uid') != 'insighthub-day6-finops' or len(dashboard.get('panels', [])) < 10:
    raise ValueError('Expected reviewed native FinOps dashboard')
configmap = {'apiVersion': 'v1', 'kind': 'ConfigMap',
             'metadata': {'name': 'insighthub-day6-finops-dashboard', 'namespace': 'monitoring',
                          'labels': {'grafana_dashboard': '1'}},
             'data': {'insighthub-day6-finops.json': json.dumps(dashboard)}}
(root / 'finops/dashboard-configmap.json').write_text(json.dumps(configmap, indent=2) + '\n')
print('Ten-panel dashboard and scoped ConfigMap generated.')
