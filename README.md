# EventFlow — Reliable Workflow Engine

A durable asynchronous job engine focused on failure handling.

## Reliability mechanisms

- idempotency keys
- SQLite WAL persistence
- atomic worker claiming with transactions
- worker leases and expired-lease recovery
- deterministic priority scheduling
- exponential retry with injectable jitter
- dead-letter queue after max attempts
- transactional outbox for completion events
- circuit breaker
- explicit job state machine

## Architecture

Client -> idempotent submit -> durable queue -> atomic lease -> worker
                                      |                     |
                                      +-> retry/backoff <---+
                                      |
                                      +-> DLQ
                                      |
                                      +-> outbox on success

This is intentionally complementary to the SRE project: it executes work reliably rather than diagnosing production incidents.
