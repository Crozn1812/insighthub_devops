"""Scoped runtime config only; unchanged API image and embedding identity."""
import json
from pathlib import Path
import subprocess

keys = json.loads((Path.home() / '.codex/day6-runtime/finops-keys.json').read_text())
base = ['kubectl', '--kubeconfig', str(Path.home() / '.codex/day6-runtime/kubeconfig-recovery-20261003.yaml'), '-n', 'insighthub-dev']
secret = {'apiVersion': 'v1', 'kind': 'Secret', 'metadata': {'name': 'insighthub-day6-finops-identity'},
          'type': 'Opaque', 'stringData': {'OPENAI_API_KEY': keys['insighthub']}}
subprocess.run(base + ['apply', '-f', '-'], input=json.dumps(secret), text=True, check=True)
patch = {'spec': {'template': {'spec': {'containers': [{'name': 'api', 'env': [
    {'name': 'OPENAI_API_KEY', 'valueFrom': {'secretKeyRef': {'name': 'insighthub-day6-finops-identity', 'key': 'OPENAI_API_KEY'}}},
    {'name': 'LLM_PROVIDER', 'value': 'openai'},
    {'name': 'OPENAI_BASE_URL', 'value': 'http://insighthub-finops-gateway:4001/v1'},
    {'name': 'OPENAI_CHAT_MODEL', 'value': 'qwen3:4b'}]}]}}}}
subprocess.run(base + ['patch', 'deployment', 'insighthub-api', '--type=strategic', '--patch', json.dumps(patch)],
               text=True, check=True)
subprocess.run(base + ['rollout', 'status', 'deployment/insighthub-api', '--timeout=180s'], check=True)
print('API routed through scoped LiteLLM gateway; secret values withheld; image unchanged.')
