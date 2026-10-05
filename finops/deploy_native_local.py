"""Switch the local lab to native keys/NeMo, preserving deployment rollback data."""

import argparse
import json
import subprocess
from pathlib import Path

from native_keys import private_path


def command(argv: list[str], body: dict | None = None) -> str:
    result = subprocess.run(argv, input=json.dumps(body) if body is not None else None,
                            text=True, capture_output=True, timeout=120, check=False)
    if result.returncode:
        # Secret apply errors may echo input: never print subprocess output.
        operation = next((part for part in argv if part in
                          {"get", "inspect", "network", "apply", "patch", "rollout"}), "command")
        raise RuntimeError("Local deployment command failed: " + argv[0] + " " + operation)
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kubeconfig", required=True)
    parser.add_argument("--private-keys", required=True)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--rollback-file", required=True)
    parser.add_argument("--resume", action="store_true", help="Resume without overwriting saved rollback")
    parser.add_argument("--telemetry-only", action="store_true")
    args = parser.parse_args()
    keys = json.loads(private_path(args.private_keys).read_text())
    values = dict(line.split("=", 1) for line in private_path(args.env_file).read_text().splitlines()
                  if line and not line.startswith("#"))
    rollback = private_path(args.rollback_file)
    if rollback.exists() and not args.resume:
        raise RuntimeError("Rollback file exists; review previous deployment before switching")
    kubectl = ["kubectl", "--kubeconfig", str(private_path(args.kubeconfig)),
               "--context", "docker-desktop", "-n", "insighthub-dev"]
    deployments = {}
    for name in ("insighthub-api", "insighthub-ingestion-worker"):
        deployments[name] = json.loads(command(kubectl + ["get", "deployment", name, "-o", "json"]))
    if not rollback.exists():
        with rollback.open("x", encoding="utf-8") as output:
            json.dump(deployments, output)
    for service, container, port in (
        ("insighthub-native-litellm", "insighthub-native-finops-litellm-1", 4000),
        ("insighthub-native-nemo", "insighthub-native-finops-guardrails-1", 8082),
        ("insighthub-native-accounting", "insighthub-native-finops-accounting-exporter-1", 9108),
    ):
        networks = json.loads(command(["docker", "inspect", container, "--format",
                                        '{{json .NetworkSettings.Networks}}']))
        address = networks.get("kind", {}).get("IPAddress")
        if not address:
            command(["docker", "network", "connect", "kind", container])
            address = command(["docker", "inspect", container, "--format",
                               '{{(index .NetworkSettings.Networks "kind").IPAddress}}']).strip()
        command(kubectl + ["apply", "-f", "-"], {
            "apiVersion": "v1", "kind": "Service", "metadata": {"name": service,
            "labels": {"app": service}},
            "spec": {"ports": [{"name": "http", "port": port, "targetPort": port}]},
        })
        command(kubectl + ["apply", "-f", "-"], {
            "apiVersion": "discovery.k8s.io/v1", "kind": "EndpointSlice",
            "metadata": {"name": service, "labels": {"kubernetes.io/service-name": service}},
            "addressType": "IPv4", "ports": [{"name": "http", "protocol": "TCP", "port": port}],
            "endpoints": [{"addresses": [address], "conditions": {"ready": True}}],
        })
        # The local Prometheus installation discovers legacy Endpoints. Both
        # objects point to the same real Docker address, without metric stubs.
        command(kubectl + ["apply", "-f", "-"], {
            "apiVersion": "v1", "kind": "Endpoints", "metadata": {"name": service},
            "subsets": [{"addresses": [{"ip": address}],
                         "ports": [{"name": "http", "protocol": "TCP", "port": port}]}],
        })
    command(kubectl + ["apply", "-f", "-"], {
        "apiVersion": "monitoring.coreos.com/v1", "kind": "ServiceMonitor",
        "metadata": {"name": "insighthub-native-accounting", "labels": {"release": "kube-prometheus-stack"}},
        "spec": {"selector": {"matchLabels": {"app": "insighthub-native-accounting"}},
                 "endpoints": [{"port": "http", "path": "/metrics", "interval": "15s"}]},
    })
    if args.telemetry_only:
        print(json.dumps({"native_accounting_monitor_applied": True, "workloads_restarted": False}))
        return
    command(kubectl + ["apply", "-f", "-"], {
        "apiVersion": "v1", "kind": "Secret", "metadata": {"name": "insighthub-native-security"},
        "stringData": {"OPENAI_API_KEY": keys["insighthub"], "LITELLM_API_KEY": keys["insighthub"],
                       "NEMO_GUARDRAILS_KEY": values["GUARD_API_KEY"]},
    })
    for name, image in (("insighthub-api", "insighthub-api:upstream-audit-local"),
                        ("insighthub-ingestion-worker", "insighthub-ingestion-worker:upstream-audit-local")):
        container = deployments[name]["spec"]["template"]["spec"]["containers"][0]["name"]
        env = []
        if name == "insighthub-api":
            for variable in ("OPENAI_API_KEY", "LITELLM_API_KEY", "NEMO_GUARDRAILS_KEY"):
                env.append({"name": variable, "valueFrom": {"secretKeyRef": {
                    "name": "insighthub-native-security", "key": variable}}})
            env += [{"name": "OPENAI_BASE_URL", "value": "http://insighthub-native-litellm:4000/v1"},
                    {"name": "NEMO_GUARDRAILS_URL", "value": "http://insighthub-native-nemo:8082"},
                    {"name": "LLM_STRUCTURED_OUTPUT", "value": "true"}]
        patch = {"spec": {"template": {"spec": {"containers": [
            {"name": container, "image": image, "imagePullPolicy": "Never", "env": env}]}}}}
        # This patch contains secret references only; actual values used stdin above.
        command(kubectl + ["patch", "deployment", name, "--type", "strategic",
                           "--patch", json.dumps(patch)])
        command(kubectl + ["rollout", "status", "deployment/" + name, "--timeout=100s"])
    print(json.dumps({"api_image": "insighthub-api:upstream-audit-local",
                      "worker_image": "insighthub-ingestion-worker:upstream-audit-local",
                      "native_gateway": True, "nemo_enabled": True,
                      "embedding_identity_changed": False, "rollback_saved": True}))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired):
        raise SystemExit("Native local switch failed; preserve rollback and inspect privately") from None
