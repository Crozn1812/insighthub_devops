"""Create secrets only in the existing user-local runtime directory."""
import json
from pathlib import Path
import secrets

destination = Path.home() / '.codex/day6-runtime/finops-keys.json'
if destination.exists():
    values = json.loads(destination.read_text())
    assert set(values) == {'insighthub', 'bot', 'coding'}
else:
    destination.write_text(json.dumps({name: secrets.token_urlsafe(48) for name in ('insighthub', 'bot', 'coding')}), encoding='utf-8')
print('Three scoped keys available in user-local runtime; values withheld.')
