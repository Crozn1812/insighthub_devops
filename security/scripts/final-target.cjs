const {randomUUID} = require('node:crypto');
const {execFileSync} = require('node:child_process');
function memory() {
  return Number(execFileSync('powershell.exe', ['-NoProfile', '-Command',
    '(Get-Process | Where-Object ProcessName -Like "ollama*" | Measure-Object WorkingSet64 -Sum).Sum'],
    {encoding: 'utf8', timeout: 10000}).trim());
}
class FinalTarget {
  id() {return 'insighthub-final-r2-http';}
  async callApi(prompt) {
    const requestId = randomUUID();
    const started = performance.now();
    const before = memory();
    const response = await fetch('http://127.0.0.1:18000/chat', {
      method: 'POST', headers: {'Content-Type': 'application/json', 'X-Request-ID': requestId},
      body: JSON.stringify({question: prompt, top_k: 3}), signal: AbortSignal.timeout(330000)});
    const api = await response.json();
    if (!response.ok) throw new Error('Target HTTP ' + response.status);
    const peak = Math.max(before, memory());
    return {output: api.answer, raw: JSON.stringify(api), metadata: {
      request_id: requestId, request_id_source: 'client-generated correlation UUID sent in X-Request-ID; not a provider response ID',
      http_status: response.status,
      resource_usage: {measurement_source: 'Windows Get-Process ollama* WorkingSet64 sampled before and after request; aggregate host RSS, excludes GPU memory and other requests allocation',
        duration_seconds: (performance.now() - started) / 1000, memory_peak_bytes: peak},
      target_model: api.model, target_mode: api.mode, usage: api.usage}};
  }
}
module.exports = FinalTarget;
