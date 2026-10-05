import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { parse } from 'yaml';

const root = path.resolve(import.meta.dirname, '..');
const config = parse(fs.readFileSync(path.join(root, 'promptfooconfig.yaml'), 'utf8'));
const generated = parse(fs.readFileSync(path.join(root, 'results', 'redteam-generated.yaml'), 'utf8'));
const core = parse(fs.readFileSync(path.join(root, 'results', 'redteam-core.yaml'), 'utf8'));
const corpus = JSON.parse(fs.readFileSync(path.join(root, 'day6-generated-corpus.json'), 'utf8'));
const dataset = JSON.parse(fs.readFileSync(path.join(root, 'day6-dataset.json'), 'utf8'));

assert.equal(config.redteam.provider.id, 'ollama:chat:qwen3:4b');
assert.equal(config.redteam.provider.config.think, false);
assert.equal(config.defaultTest.options.provider.id, 'ollama:chat:qwen3:1.7b');
assert.equal(config.defaultTest.options.provider.config.think, false);
assert.equal(config.defaultTest.options.provider.config.format, 'json');
assert.equal(config.defaultTest.options.provider.config.num_predict, 128);
assert.ok(generated.tests.length >= 50, 'at least 50 Promptfoo-native attacks are required');
assert.ok(generated.tests.every((test) => test.metadata?.pluginId), 'every attack must retain Promptfoo plugin provenance');

const cases = dataset.cases;
const ids = new Set(cases.map((item) => item.id));
const attackCount = cases.filter((item) => item.source === 'promptfoo-native').length;
const benignCount = cases.filter((item) => item.category === 'benign').length;
const categoryCounts = Object.fromEntries(
  ['injection', 'pii', 'excessive_agency', 'benign'].map((category) => [
    category,
    cases.filter((item) => item.category === category).length,
  ]),
);
assert.equal(ids.size, cases.length, 'dataset IDs must be unique');
assert.equal(generated.tests.length, 262, 'generated attack corpus must remain complete');
assert.equal(corpus.cases.filter((item) => item.source === 'promptfoo-native').length, 262);
assert.equal(corpus.cases.filter((item) => item.category === 'benign').length, 10);
assert.equal(attackCount, 60, 'core dataset must contain 60 attacks');
assert.equal(benignCount, 10, 'core dataset must contain 10 benign cases');
assert.equal(cases.length, 70, 'core dataset must contain 70 cases');
assert.deepEqual(categoryCounts, { injection: 20, pii: 30, excessive_agency: 10, benign: 10 });
assert.equal(core.tests.length, 70, 'Promptfoo core config must execute all core cases');
assert.equal(core.defaultTest.options.provider.config.think, false);
assert.equal(core.defaultTest.options.provider.id, 'ollama:chat:qwen3:1.7b');
assert.equal(core.defaultTest.options.provider.config.format, 'json');
assert.equal(core.defaultTest.options.provider.config.num_predict, 128);
assert.equal(new Set(core.tests.map((test) => test.metadata?.caseId)).size, 70);
assert.ok(cases.some((item) => item.category === 'injection'), 'injection category is required');
assert.ok(cases.some((item) => item.category === 'benign'), 'benign category is required');
assert.ok(cases.every((item) => item.input?.trim() && item.expected?.trim()), 'inputs and expectations must be non-placeholder');

console.log(JSON.stringify({ generatedAttacks: generated.tests.length, coreAttacks: attackCount, benignCases: benignCount, total: cases.length, categoryCounts, uniqueIds: ids.size }));
