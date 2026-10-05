"""Provision real LiteLLM DB-backed keys; secret values stay outside this repo."""

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:14002"
CAPS = {"insighthub": 1.0, "bot": 0.5, "coding": 1.0}


def private_path(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if path.is_relative_to(ROOT):
        raise ValueError("Private credential path must be outside repository")
    return path


def post(endpoint: str, identity: str, body: dict) -> dict:
    request = Request(BASE + endpoint, data=json.dumps(body).encode(),
                      headers={"Authorization": "Bearer " + identity,
                               "Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=120) as response:
            result = json.load(response)
    except HTTPError as error:
        # Native admin errors can contain identities: never print response bodies.
        raise RuntimeError(f"Native endpoint failed: HTTP {error.code}") from None
    except URLError:
        raise RuntimeError("Native endpoint unavailable") from None
    if not isinstance(result, dict):
        raise RuntimeError("Invalid native response")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--private-keys", required=True)
    args = parser.parse_args()
    env_file = private_path(args.env_file)
    destination = private_path(args.private_keys)
    if destination.exists():
        raise ValueError("Refuse to overwrite existing keys")
    values = dict(line.split("=", 1) for line in env_file.read_text().splitlines()
                  if line and not line.startswith("#"))
    master = values["LITELLM_MASTER_KEY"]
    keys, metadata = {}, []
    for alias, budget in CAPS.items():
        result = post("/key/generate", master, {
            "key_alias": "insighthub-audit-" + alias,
            "models": ["qwen3:4b"], "max_budget": budget,
            "duration": "7d", "metadata": {"workload": alias, "provider_cost_scope": "local"},
        })
        key = result.get("key")
        if not isinstance(key, str) or not key.startswith("sk-"):
            raise RuntimeError("Native key generation did not return a virtual key")
        # Save each successful provision immediately: a later error cannot lose keys.
        keys[alias] = key
        if not destination.exists():
            with destination.open("x", encoding="utf-8") as output:
                os.chmod(destination, 0o600)
                json.dump(keys, output)
        else:
            destination.write_text(json.dumps(keys), encoding="utf-8")
        metadata.append({"workload": alias, "key_alias": result.get("key_alias"),
                         "max_budget": result.get("max_budget"),
                         "budget_duration": result.get("budget_duration"),
                         "native_generation": True})
    print(json.dumps({"native_keys": metadata, "secret_values_emitted": False}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, RuntimeError) as error:
        # Only our fixed error text is safe; OS exceptions may reveal private paths.
        if isinstance(error, RuntimeError):
            raise SystemExit(str(error)) from None
        raise SystemExit("Native provisioning failed; inspect local prerequisites privately") from None
