"""Native LiteLLM key attribution and zero-cap enforcement proof (no key output)."""

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from native_keys import CAPS, post, private_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--private-keys", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    values = dict(line.split("=", 1) for line in private_path(args.env_file).read_text().splitlines()
                  if line and not line.startswith("#"))
    keys = json.loads(private_path(args.private_keys).read_text())
    master = values["LITELLM_MASTER_KEY"]
    rows = []
    for alias, key in keys.items():
        response = post("/chat/completions", key, {
            "model": "qwen3:4b", "max_tokens": 32,
            "messages": [{"role": "user", "content": "Reply with one short sentence explaining Redis queues."}],
        })
        row = {"workload": alias, "allowed": bool(response.get("choices")),
               "response_id": response.get("id"), "usage": response.get("usage"),
               "max_budget": CAPS[alias], "denied": 0}
        # This is a real native zero-cap check at zero local provider cost. It is
        # not evidence that positive dollar spend has exhausted the usual cap.
        try:
            updated = post("/key/update", master, {"key": key, "max_budget": 0})
            row["native_update_zero_cap"] = updated.get("max_budget") == 0
            time.sleep(12)
            row["denial_http_statuses"] = []
            def denied(_):
                try:
                    post("/chat/completions", key, {"model": "qwen3:4b", "max_tokens": 8,
                         "messages": [{"role": "user", "content": "Say hello."}]})
                    return False
                except RuntimeError as error:
                    status = str(error).rsplit("HTTP ", 1)[-1]
                    row["denial_http_statuses"].append(status)
                    return status in {"400", "403", "429"}
            with ThreadPoolExecutor(max_workers=2) as executor:
                row["denied"] = sum(executor.map(denied, range(2)))
        finally:
            post("/key/update", master, {"key": key, "max_budget": CAPS[alias]})
        rows.append(row)
    report = {"observed_at": datetime.now(timezone.utc).isoformat(),
              "engine": "native-litellm-1.98.0", "workloads": rows,
              "provider_cost_usd": 0, "native_accounting_scope": "planning allocation, not provider billing",
              "planning_input_rate": 0.000001, "planning_output_rate": 0.000002,
              "denial_scope": "temporary native max_budget=0",
              "positive_budget_exhaustion_verified": False,
              "keys_emitted": False}
    with open(args.output, "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
    print(json.dumps({"allowed": sum(row["allowed"] for row in rows),
                      "denied": sum(row["denied"] for row in rows)}))


if __name__ == "__main__":
    main()
