const fs = require('fs');
const yaml = require('yaml');
const core = yaml.parse(fs.readFileSync('results/redteam-core.yaml', 'utf8'));
const dataset = JSON.parse(fs.readFileSync('day6-dataset.json', 'utf8'));
if (core.tests.length !== 70 || new Set(core.tests.map(t => t.metadata.caseId)).size !== 70)
  throw new Error('Expected exact 70-case coverage');
for (const test of core.tests) {
  const source = dataset.cases.find(c => c.id === test.metadata.caseId);
  if (!source || source.input !== test.vars.prompt) throw new Error('Dataset/config mismatch');
  test.assert = test.assert.map(assertion => assertion.type.startsWith('promptfoo:redteam:') ? {
    type: 'javascript', value: 'file://scripts/agency-grade-final.cjs', metric: assertion.metric,
    config: {nativeAssertion: assertion},
  } : assertion);
}
core.description = 'ONE official final 70-case r2 execution; frozen qwen3:4b judge; evaluator limitation TRUE';
core.targets = [{id: 'file://scripts/final-target.cjs', label: 'insighthub-r2-real-chat'}];
core.defaultTest.options.provider = {id: 'ollama:chat:qwen3:4b', config: {think: false, format: 'json', num_predict: 512, num_ctx: 4096}};
fs.writeFileSync('day6-final-frozen.yaml', yaml.stringify(core));
console.log(JSON.stringify({cases: 70, datasetPromptsUnchanged: true, nativeAssertionsPreserved: true, evaluatorLimitation: true}));
