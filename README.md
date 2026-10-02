EventFlow — Reliable Workflow Engine

EventFlow is a Python-based workflow/job execution engine designed to handle reliable background work with retries, recovery, idempotency, prioritization, and failure isolation.

Why EventFlow?

Background jobs can fail because of temporary service errors, worker crashes, duplicate requests, or unavailable dependencies.

EventFlow explores how a reliable workflow engine can continue processing work while preventing duplicate execution and recovering jobs after failures.

Key Features

- Idempotency — prevents duplicate job execution using idempotency keys.
- Priority scheduling — higher-priority jobs can be processed before lower-priority jobs.
- Retries & exponential backoff — transient failures are retried automatically.
- Lease-based recovery — abandoned jobs can be recovered after a worker failure.
- Dead-letter queue — permanently failed jobs are isolated for later inspection.
- Transactional outbox — supports reliable event publication alongside database updates.
- Circuit breaker — prevents repeated calls to an unhealthy dependency.
- SQLite WAL mode — improves concurrent database access.
- Atomic worker claiming — prevents multiple workers from claiming the same job.
- Job state machine — keeps job transitions explicit and controlled.

Architecture

                    ┌──────────────────┐
                    │   Client / API   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Job Manager    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ SQLite / WAL DB  │
                    └────────┬─────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │ Worker Pool  │      │ Outbox/Event │
          └──────┬───────┘      └──────────────┘
                 │
        ┌────────┼─────────┐
        ▼        ▼         ▼
     Success   Retry    Permanent
                         Failure
                           │
                           ▼
                    Dead-Letter Queue

Job Lifecycle

A job moves through explicit states:

PENDING
   │
   ▼
RUNNING
 ┌─┴───────────────┐
 │                 │
 ▼                 ▼
SUCCESS           FAILED
                     │
              retry available?
                 /       \
               yes        no
                │          │
                ▼          ▼
              RETRY       DLQ

This makes job execution and failure handling easier to reason about and test.

Reliability Mechanisms

Idempotency

Each job can use an idempotency key so that repeated requests do not result in unintended duplicate work.

Retries

Transient failures can be retried using exponential backoff rather than immediately failing the job.

Lease-Based Recovery

Workers acquire a lease while processing a job. If a worker crashes and the lease expires, the job can become eligible for recovery.

Dead-Letter Queue

Jobs that exceed their retry policy are moved to a dead-letter queue instead of being retried indefinitely.

Transactional Outbox

Database changes and outgoing events can be coordinated through an outbox mechanism, reducing the risk of updating state successfully while losing the corresponding event.

Circuit Breaker

Repeated failures from an external dependency can cause the circuit to open temporarily, preventing unnecessary calls while the dependency is unhealthy.

Tech Stack

- Python
- SQLite
- SQLite WAL
- Pytest
- Docker
- GitHub Actions

Project Structure

eventflow/
├── ...
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md

«Update this section to match the actual directory structure of the repository.»

Getting Started

Clone

git clone https://github.com/sadiaaref/eventflow-reliable-workflow-engine.git
cd eventflow-reliable-workflow-engine

Install dependencies

python -m venv .venv

Activate the virtual environment and install the project's dependencies according to the repository configuration.

Run

Use the project's documented entry point to start EventFlow.

Run tests

pytest

Testing

The project includes tests for reliability and workflow behavior, including failure handling and recovery scenarios.

Run:

pytest

For the most useful test cases, focus on:

- duplicate job submission
- concurrent worker claiming
- retry behavior
- lease expiration
- worker recovery
- dead-letter handling
- state transitions

Engineering Concepts Demonstrated

EventFlow was built to explore practical backend and distributed-systems concepts:

- concurrency
- atomic operations
- failure recovery
- idempotency
- retry strategies
- state machines
- database transactions
- event reliability
- fault isolation

Future Improvements

Potential improvements include:

- PostgreSQL support
- Redis-based distributed coordination
- metrics and observability
- structured logging
- web dashboard
- distributed workers
- additional integration tests

Author

Sadia Aref

Python | Backend Development | Software Engineering

GitHub: https://github.com/sadiaaref
