# Native NeMo guardrails

Adapted from authoritative upstream `congdinh2008/insighthub` at
`4923fed6ef650aeea69eb179ff2a12415cf0fc90`, `security/guardrails/`.
Dependencies are the upstream hash-locked NeMo 0.24.1 set. The service actually
uses `Guardrails(..., require_iorails=True)` and `check_async`, rather than
renaming the application's deterministic detector as NeMo.

Default configuration has `models: []`: native input/output regex rails execute
locally, with no classifier/provider bill. Semantic self-checks are **disabled**
unless explicitly configured and independently verified. Regex rails are bounded
defense layers, not proof of general injection resistance.

The API additionally retains its deterministic input, retrieved-context and
protected-output controls. Set `NEMO_GUARDRAILS_URL` and the private
`NEMO_GUARDRAILS_KEY` to enable native checks on input, retained retrieval chunks
and generated output. An unavailable/malformed rail response returns 503.
Fixture environments may leave the URL empty; that does not demonstrate MH6.

`finops/native-compose.yaml` starts the isolated local service. Supply
`NATIVE_ENV_FILE` outside the repository. Never publish keys or service request
bodies. Runtime allowed/blocked proof is still required before marking MH6 PASS.

Current final native probe: **4 PASS / 1 FAIL**. Input/context checks and
HTTP-failure handling behaved as expected; an output behavior-override sentence
was allowed. Output regexes cover PII/key markers, not general output injection.
See [actual result](../../docs/evidence/upstream/nemo-final-runtime.json).
