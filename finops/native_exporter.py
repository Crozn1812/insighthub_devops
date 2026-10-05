"""Read-only native accounting metrics with workload aliases, never key values."""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, urlunsplit

import psycopg


def metrics():
    url = urlsplit(os.environ["DATABASE_URL"])
    dsn = urlunsplit((url.scheme, url.netloc, url.path, "", ""))
    lines = []
    with psycopg.connect(dsn, connect_timeout=5) as connection:
        connection.read_only = True
        with connection.cursor() as cursor:
            cursor.execute('''SELECT v.key_alias,v.max_budget,v.spend,
                COALESCE(SUM(s.prompt_tokens),0),COALESCE(SUM(s.completion_tokens),0),COUNT(s.request_id)
                FROM "LiteLLM_VerificationToken" v LEFT JOIN "LiteLLM_SpendLogs" s ON s.api_key=v.token
                WHERE v.key_alias IN ('insighthub-audit-insighthub','insighthub-audit-bot','insighthub-audit-coding')
                GROUP BY v.key_alias,v.max_budget,v.spend ORDER BY v.key_alias''')
            for alias, budget, spend, inputs, outputs, requests in cursor.fetchall():
                workload = alias.removeprefix("insighthub-audit-")
                labels = '{workload="' + workload + '"}'
                for name, value in {"requests_total": requests, "input_tokens_total": inputs,
                                    "output_tokens_total": outputs, "planning_usd_total": spend,
                                    "budget_planning_usd": budget, "provider_cost_usd_total": 0}.items():
                    if value is not None:
                        lines.append("insighthub_native_" + name + labels + " " + str(value))
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        if self.path != "/metrics":
            self.send_error(404)
            return
        try:
            body = metrics().encode()
        except (psycopg.Error, ValueError, KeyError):
            self.send_error(503, "Accounting unavailable")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 9108), Handler).serve_forever()
