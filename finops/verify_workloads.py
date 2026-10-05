"""Real MCP-backed bot summaries and a bounded context/patch/test coding workflow."""

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from native_keys import post, private_path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--private-keys", required=True)
    parser.add_argument("--mcp-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    keys = json.loads(private_path(args.private_keys).read_text())
    values = dict(line.split("=", 1) for line in private_path(args.env_file).read_text().splitlines()
                  if line and not line.startswith("#"))
    mcp_root = private_path(args.mcp_root)
    os.environ.update(CHATOPS_MODEL_URL="http://127.0.0.1:14002/v1", CHATOPS_MODEL_KEY=keys["bot"],
        CHATOPS_GUARD_URL="http://127.0.0.1:18082", CHATOPS_GUARD_KEY=values["GUARD_API_KEY"],
        PROMETHEUS_MCP_COMMAND=str(mcp_root / "prometheus-mcp-0.18.0/prometheus-mcp-server.exe"),
        PROMETHEUS_MCP_ARGS=json.dumps(["--prometheus.url=http://127.0.0.1:9090", "--mcp.transport=stdio",
                                     "--mcp.tools=query", "--no-dangerous.enable-tsdb-admin-tools",
                                     "--no-docs.auto-update", "--web.listen-address=127.0.0.1:0"]),
        KUBERNETES_MCP_COMMAND="G:/node.exe", KUBERNETES_MCP_ARGS=json.dumps([
            str(mcp_root / "kubernetes-mcp-0.0.67/node_modules/kubernetes-mcp-server/bin/index.js"),
            "--config", str(mcp_root / "kubernetes/server-readonly.toml")]))
    sys.path.insert(0, str(ROOT / "chatops-bot"))
    from app.queue import ChatEvent
    from app.worker import process_event
    rows = []
    for index, question in enumerate(("InsightHub healthy?", "Ingest today?", "Pods failing?")):
        result = process_event(ChatEvent("native-audit-" + str(index), "U_SYNTHETIC_AUDIT",
                               "C_LOCAL_CAPTURE", question, "local-capture"))
        rows.append({"workload": "bot", "intent": question, "mcp_available": "UNKNOWN" not in result,
                     "model_used": "AI summary (advisory):" in result,
                     "result_sha256": hashlib.sha256(result.encode()).hexdigest(), "slack_live": False})

    # The proposed helper is derived from actual repository serialization code.
    context = (ROOT / "chatops-bot/app/queue.py").read_text()
    source = next(line.strip() for line in context.splitlines() if "payload = json.dumps(asdict(event)" in line)
    prompt = ("Propose a pure Python extraction helper named event_payload(event) for this real repository line: "
              + source + ". json and asdict are already imported. Return JSON with only code (a string containing "
              "one function definition); no imports, commands or extra functions. Preserve Unicode, separators and dataclass fields.")
    def guard(text, phase):
        request = Request("http://127.0.0.1:18082/check", data=json.dumps({"text": text, "phase": phase}).encode(),
                          headers={"X-Guard-Key": values["GUARD_API_KEY"], "Content-Type": "application/json"})
        with urlopen(request, timeout=25) as response:
            return json.load(response).get("allowed") is True
    if not guard(prompt, "input"):
        raise RuntimeError("Coding context blocked")
    response = post("/chat/completions", keys["coding"], {"model": "qwen3:4b", "max_tokens": 256,
        "response_format": {"type": "json_schema", "json_schema": {"name": "coding_patch", "strict": True,
        "schema": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"], "additionalProperties": False}}},
        "messages": [{"role": "user", "content": prompt}]})
    candidate = json.loads(response["choices"][0]["message"]["content"])["code"]
    if not isinstance(candidate, str) or len(candidate) > 3000 or not guard(candidate, "output"):
        raise RuntimeError("Coding output rejected")
    tree = ast.parse(candidate)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef) or tree.body[0].name != "event_payload":
        raise RuntimeError("Coding patch shape rejected")
    allowed_nodes = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Return, ast.Call,
                     ast.Name, ast.Load, ast.Attribute, ast.keyword, ast.Constant, ast.Tuple, ast.Expr)
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise RuntimeError("Coding patch syntax outside pure helper allowlist")
        if isinstance(node, ast.Name) and node.id not in {"event", "json", "asdict"}:
            raise RuntimeError("Coding patch identifier outside allowlist")
        if isinstance(node, ast.Attribute) and not (node.attr == "dumps" and isinstance(node.value, ast.Name) and node.value.id == "json"):
            raise RuntimeError("Coding patch attribute outside allowlist")
    test = '''import json, unittest
from dataclasses import dataclass, asdict
scope = {"json":json,"asdict":asdict,"__builtins__":{}}
exec(CANDIDATE,scope)
@dataclass
class Event:
    text:str
    attempt:int=0
class CandidateTests(unittest.TestCase):
    def test_unicode(self):
        value=scope["event_payload"](Event("Tiếng Việt"))
        self.assertIn("Tiếng Việt",value)
        self.assertEqual(json.loads(value),{"text":"Tiếng Việt","attempt":0})
    def test_quote_roundtrip(self):
        self.assertEqual(json.loads(scope["event_payload"](Event('a"b')))["text"],'a"b')
    def test_stable_compact_encoding(self):
        ev=Event("ok",2)
        self.assertEqual(scope["event_payload"](ev),json.dumps(asdict(ev),separators=(",",":"),ensure_ascii=False))
unittest.main()
'''.replace("CANDIDATE", repr(candidate))
    completed = subprocess.run(["docker", "run", "--rm", "-i", "--network", "none", "--read-only",
        "--memory", "128m", "--cpus", "1", "--tmpfs", "/tmp", "insighthub-api:upstream-audit-local", "python", "-"],
        input=test, text=True, encoding="utf-8", capture_output=True, timeout=30)
    rows.append({"workload": "coding", "source_file": "chatops-bot/app/queue.py",
                 "source_sha256": hashlib.sha256(context.encode()).hexdigest(), "proposed_helper": candidate,
                 "patch_scope": "extraction proposal tested in isolated container; not applied to production",
                 "tests_passed": completed.returncode == 0, "test_count": 3,
                 "provider_response_id": response.get("id"), "usage": response.get("usage")})
    report = {"observed_at": datetime.now(timezone.utc).isoformat(), "workloads": rows,
              "provider_cost_usd": 0, "keys_emitted": False}
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"bot_model_calls_passed": sum(r.get("model_used",False) for r in rows),
                      "coding_tests_passed": completed.returncode == 0}))


if __name__ == "__main__":
    main()
