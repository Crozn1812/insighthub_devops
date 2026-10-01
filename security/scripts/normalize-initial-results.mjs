import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const raw = JSON.parse(fs.readFileSync(path.join(root, 'results', 'day6-initial-promptfoo.json'), 'utf8'));
const results = raw.results.results.map((row) => ({
  case_id: row.testCase.metadata.caseId,
  category: row.testCase.metadata.category,
  passed: row.success,
  severity: row.testCase.metadata.severity ?? null,
  provider: 'ollama',
  model: 'qwen3:4b',
  judge_model: 'qwen3:1.7b',
  request_id: row.id,
  input_tokens: row.response?.metadata?.input_tokens ?? null,
  output_tokens: row.response?.metadata?.output_tokens ?? null,
  latency_ms: row.latencyMs,
  reason: row.gradingResult.reason,
  source_commit: '936da06fae93a25fca88cd71dfd7fa5a2aedff0f',
}));
fs.writeFileSync(path.join(root, 'results', 'day6-initial-results.json'), `${JSON.stringify({ eval_id: raw.evalId, results }, null, 2)}\n`);
console.log(JSON.stringify({ evalId: raw.evalId, total: results.length, pass: results.filter((r) => r.passed).length, fail: results.filter((r) => !r.passed).length }));
