# Day 1 independent review

The API persists a bounded upload in the shared payload volume before it returns
202, while the separately built ARQ worker receives only the document ID and
uses the existing `process_document` transaction. The worker image runs as UID
1001 and Compose invokes its packaged entry point. A lost enqueue reply returns
503 and preserves the payload; its conditional failure marker cannot overwrite
a locked or ready row. Manual retry accepts only failed rows, verifies retained
payload hash and pipeline identity, and uses the stable job ID without retaining
old ARQ results. Integration tests cover first-attempt provider failure followed
by a successful retry using the same document ID, plus missing/changed payload,
pipeline mismatch and enqueue timeout. Runtime fixture verification measured a
fresh 202 upload, ready state, chat source and correlated worker JSON event.
The remaining limitation is no outbox/reconciler for a process crash after the
database commit and before enqueue; this is documented rather than hidden.
