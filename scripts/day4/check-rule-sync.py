#!/usr/bin/env python3
"""Fail when the canonical Prometheus rules and PrometheusRule CRD diverge."""
from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[2]
canonical = yaml.safe_load((root / "observability/prometheus-rules.yaml").read_text())
runtime = yaml.safe_load((root / "observability/prometheus-rule-crd.yaml").read_text())
if canonical["groups"] != runtime["spec"]["groups"]:
    raise SystemExit("PrometheusRule CRD differs from canonical prometheus-rules.yaml")
print("RULE_SYNC=PASS")
