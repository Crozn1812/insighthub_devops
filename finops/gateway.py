"""Scoped bearer identities and atomic local allocations before LiteLLM.

This is equivalent scoped authentication around LiteLLM, not native DB-backed
LiteLLM virtual keys. Provider cost remains zero; planning credits are explicit.
"""
from __future__ import annotations

import hmac
import json
import os
from pathlib import Path
import sqlite3
import resource
import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import httpx

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / 'budgets.json').read_text())
DB = os.environ.get('FINOPS_DB', '/state/ledger.sqlite')
KEYS_FILE = os.environ.get('FINOPS_KEYS_FILE', '/run/keys.json')
LITELLM = os.environ.get('LITELLM_URL', 'http://insighthub-day6-litellm:4000')
app = FastAPI()
ANSWER_SCHEMA = {'type': 'object', 'properties': {'answer': {'type': 'string',
    'description': 'Concise final factual answer, without reasoning or private instructions.'}},
    'required': ['answer'], 'additionalProperties': False}


def final_answer_content(content: str) -> str:
    value = json.loads(content)
    if not isinstance(value, dict) or set(value) != {'answer'} or not isinstance(value['answer'], str) or not value['answer'].strip():
        raise ValueError('Invalid final answer envelope')
    return value['answer']


def connection():
    db = sqlite3.connect(DB, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute('CREATE TABLE IF NOT EXISTS scopes (workload TEXT PRIMARY KEY, used INTEGER NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS events (request_id TEXT PRIMARY KEY, workload TEXT, decision TEXT, timestamp TEXT, status INTEGER, input_tokens INTEGER, output_tokens INTEGER, duration REAL, provider_id TEXT)')
    for scope in CONFIG['scopes']:
        db.execute('INSERT OR IGNORE INTO scopes VALUES (?,0)', (scope,))
    db.commit()
    return db


def reserve(workload: str, request_id: str) -> bool:
    with connection() as db:
        db.execute('BEGIN IMMEDIATE')
        used = db.execute('SELECT used FROM scopes WHERE workload=?', (workload,)).fetchone()['used']
        charge = CONFIG['allocation_micro_usd_per_request']
        allowed = used + charge <= CONFIG['scopes'][workload]['max_budget_micro_usd']
        db.execute('INSERT INTO events VALUES (?,?,?,?,NULL,NULL,NULL,NULL,NULL)',
                   (request_id, workload, 'allowed' if allowed else 'denied', datetime.now(timezone.utc).isoformat()))
        if allowed:
            db.execute('UPDATE scopes SET used=used+? WHERE workload=?', (charge, workload))
        db.commit()
        return allowed


def identity(header: str) -> str:
    if not header.startswith('Bearer '):
        raise HTTPException(401, 'Bearer scoped identity required')
    supplied = header.removeprefix('Bearer ')
    keys = json.loads(Path(KEYS_FILE).read_text())
    for workload, key in keys.items():
        if hmac.compare_digest(supplied, key):
            return workload
    raise HTTPException(401, 'Invalid scoped identity')


@app.get('/healthz')
async def health():
    async with httpx.AsyncClient(timeout=10) as client:
        result = await client.get(LITELLM + '/health/liveliness')
    return JSONResponse({'gateway': 'ready', 'litellm_status': result.status_code}, status_code=200 if result.status_code == 200 else 503)


@app.post('/v1/chat/completions')
async def chat(request: Request):
    workload = identity(request.headers.get('authorization', ''))
    request_id = str(uuid4())  # Actual gateway correlation ID created at admission.
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(400, 'JSON object required')
    if payload.get('model') != 'qwen3:4b' or payload.get('stream', False):
        raise HTTPException(400, 'Only local non-streaming qwen3:4b is allowed')
    if len(json.dumps(payload)) > 65536:
        raise HTTPException(413, 'Payload too large')
    maximum = payload.pop('max_completion_tokens', payload.get('max_tokens', 256))
    if type(maximum) is not int or maximum <= 0:
        raise HTTPException(400, 'Positive integer output limit required')
    payload['max_tokens'] = min(maximum, 1024)
    payload['metadata'] = {'workload': workload, 'finops_request_id': request_id}
    if workload == 'insighthub':
        # Preserve the app's existing final-only generation contract across
        # the supported OpenAI-compatible gateway path; guardrails stay in API.
        payload['response_format'] = {'type': 'json_schema', 'json_schema': {
            'name': 'insighthub_final_answer', 'schema': ANSWER_SCHEMA, 'strict': True}}
    if not reserve(workload, request_id):
        return JSONResponse({'error': {'message': 'Local allocation budget exceeded', 'type': 'budget_exceeded'}, 'request_id': request_id}, status_code=429, headers={'X-Request-ID': request_id})
    started = time.monotonic()
    status, usage, provider_id = 502, {}, None
    try:
        async with httpx.AsyncClient(timeout=330) as client:
            response = await client.post(LITELLM + '/v1/chat/completions', json=payload)
        status = response.status_code
        data = response.json()
        usage = data.get('usage', {})
        provider_id = data.get('id')
        if status == 200 and workload == 'insighthub':
            try:
                data['choices'][0]['message']['content'] = final_answer_content(data['choices'][0]['message']['content'])
            except (ValueError, KeyError, TypeError, IndexError):
                status = 502
                data = {'error': {'message': 'Invalid local final-answer envelope'}}
        # Gateway never persists prompts, completions or secrets.
        return JSONResponse(data, status_code=status, headers={'X-Request-ID': request_id, 'X-Workload': workload})
    except (httpx.HTTPError, ValueError):
        return JSONResponse({'error': {'message': 'Local model transport failed'}, 'request_id': request_id}, status_code=502)
    finally:
        with connection() as db:
            db.execute('UPDATE events SET status=?,input_tokens=?,output_tokens=?,duration=?,provider_id=? WHERE request_id=?',
                       (status, usage.get('prompt_tokens'), usage.get('completion_tokens'), time.monotonic() - started, provider_id, request_id))


@app.get('/metrics')
def metrics():
    lines = ['insighthub_finops_gateway_peak_rss_bytes ' + str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)]
    with connection() as db:
        for workload, budget in CONFIG['scopes'].items():
            used = db.execute('SELECT used FROM scopes WHERE workload=?', (workload,)).fetchone()['used']
            label = '{workload="' + workload + '",model="qwen3:4b"}'
            rows = db.execute('SELECT * FROM events WHERE workload=?', (workload,)).fetchall()
            values = {'requests_total': sum(r['decision'] == 'allowed' for r in rows),
                      'denied_total': sum(r['decision'] == 'denied' for r in rows),
                      'input_tokens_total': sum(r['input_tokens'] or 0 for r in rows),
                      'output_tokens_total': sum(r['output_tokens'] or 0 for r in rows),
                      'duration_seconds_total': sum(r['duration'] or 0 for r in rows),
                      'allocation_usd_used': used / 1e6,
                      'allocation_usd_remaining': (budget['max_budget_micro_usd'] - used) / 1e6,
                      'provider_cost_usd_total': 0}
            lines.extend('insighthub_finops_' + name + label + ' ' + str(value) for name, value in values.items())
    return PlainTextResponse('\n'.join(lines) + '\n', media_type='text/plain; version=0.0.4')
