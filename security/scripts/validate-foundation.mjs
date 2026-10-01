import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { parse } from 'yaml';

const root = path.resolve(import.meta.dirname, '..');
const config = parse(fs.readFileSync(path.join(root, 'promptfooconfig.yaml'), 'utf8'));
const generated = parse(fs.readFileSync(path.join(root, 'results', 'redteam-generated.yaml'), 'utf8'));
const dataset = JSON.parse(fs.readFileSync(path.join(root, 'day6-dataset.json'), 'utf8'));

assert.equal(config.redteam.provider.id, 'ollama:chat:qwen3:4b');
assert.equal(config.redteam.provider.config.think, false);
assert.equal(config.defaultTest.options.provider.id, 'ollama:chat:qwen3:4b');
assert.ok(generated.tests.length >= 50, 'at least 50 Promptfoo-native attacks are required');
assert.ok(generated.tests.every((test) => test.metadata?.pluginId), 'every attack must retain Promptfoo plugin provenance');

const cases = dataset.cases;
const ids = new Set(cases.map((item) => item.id));
const attackCount = cases.filter((item) => item.source === 'promptfoo-native').length;
const benignCount = cases.filter((item) => item.category === 'benign').length;
assert.equal(ids.size, cases.length, 'dataset IDs must be unique');
assert.equal(attackCount, generated.tests.length, 'dataset must trace every generated attack');
assert.ok(benignCount >= 10, 'at least 10 benign cases are required');
assert.ok(cases.some((item) => item.category === 'injection'), 'injection category is required');
assert.ok(cases.some((item) => item.category === 'benign'), 'benign category is required');
assert.ok(cases.every((item) => item.input?.trim() && item.expected?.trim()), 'inputs and expectations must be non-placeholder');

console.log(JSON.stringify({ generatedAttacks: generated.tests.length, benignCases: benignCount, total: cases.length, uniqueIds: ids.size }));
