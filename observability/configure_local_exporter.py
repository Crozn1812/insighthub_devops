"""Repair only the local non-TLS PostgreSQL exporter DSN; never print credentials."""

import argparse
import base64
import json
import subprocess
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kubeconfig", required=True)
    args = parser.parse_args()
    command = ["kubectl", "--kubeconfig", args.kubeconfig, "--context", "docker-desktop",
               "-n", "insighthub-dev"]
    def run(argv, body=None):
        result = subprocess.run(command + argv, input=body, text=True, capture_output=True,
                                timeout=60, check=False)
        if result.returncode:
            raise RuntimeError("Local exporter configuration failed")
        return result.stdout
    data = json.loads(run(["get", "secret", "insighthub-runtime", "-o", "json"]))
    url = urlsplit(base64.b64decode(data["data"]["DATABASE_URL"]).decode())
    if url.hostname != "insighthub-postgres":
        raise RuntimeError("Refuse to alter TLS for any non-local database")
    query = dict(parse_qsl(url.query))
    query["sslmode"] = "disable"
    dsn = urlunsplit((url.scheme, url.netloc, url.path, urlencode(query), ""))
    run(["apply", "-f", "-"], json.dumps({"apiVersion": "v1", "kind": "Secret",
        "metadata": {"name": "insighthub-postgres-exporter-local"},
        "stringData": {"DATA_SOURCE_NAME": dsn}}))
    patch = {"spec": {"template": {"spec": {"containers": [{"name": "postgres-exporter",
        "env": [{"name": "DATA_SOURCE_NAME", "valueFrom": {"secretKeyRef": {
            "name": "insighthub-postgres-exporter-local", "key": "DATA_SOURCE_NAME"}}}]}]}}}}
    run(["patch", "deployment", "insighthub-postgres-exporter", "--type=strategic", "--patch", json.dumps(patch)])
    run(["rollout", "status", "deployment/insighthub-postgres-exporter", "--timeout=60s"])
    print(json.dumps({"exporter_reconfigured": True, "scope": "existing local PostgreSQL without TLS",
                      "application_database_changed": False, "credentials_emitted": False}))


if __name__ == "__main__":
    main()
