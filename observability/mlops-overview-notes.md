# Day 4 MLOps overview

## Model Registry

The registry is the source of truth for immutable model artifacts, their version, training-data lineage, evaluation results, and deployment status. A deployment references an approved model version rather than an unpinned name.

## Approval Gate

An approval gate checks reproducible quality, safety, latency, and cost evidence before promotion. Automation may gather evidence and enforce policy, but an accountable owner approves production promotion when the policy requires human review.

## Drift

Data drift means the distribution of model inputs has changed. Concept drift means the relationship between inputs and the desired output has changed, so an unchanged input pattern may require a different answer. They need different tests and neither can be inferred from infrastructure health alone.

## Rollback

Rollback switches traffic to a previously approved model and compatible configuration, then verifies service and model-quality signals. Artifacts, prompts, embedding identity, and schema compatibility must be versioned together so rollback is deterministic.

## Ownership boundary

DevOps owns reliable deployment, telemetry, alert routing, capacity, access controls, and rollback mechanics. ML Engineers own data/model evaluation, drift interpretation, and candidate model quality. They jointly define SLOs and promotion policy. DevOps does **not** autonomously retrain the model; retraining requires the governed ML workflow and its approval gates.
