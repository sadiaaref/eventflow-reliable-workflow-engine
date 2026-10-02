EventFlow

Reliable Workflow Engine built with Python and SQLite

EventFlow is a workflow/job execution engine focused on reliable background processing. It handles job scheduling, concurrent workers, retries, idempotency, failure recovery, and persistent job state without depending on an external message broker.

The project was built to explore how reliable job execution can be designed when workers can fail, jobs can be retried, and multiple workers may try to process work at the same time.

Why I built this

A basic background-job system is easy to build until failures and concurrency become part of the problem.

EventFlow focuses on questions such as:

- What happens if a worker crashes while processing a job?
- How do multiple workers avoid claiming the same job?
- How should failed jobs be retried?
- How can a job be safely retried without performing the same operation twice?
- What happens when a job keeps failing?
- How should job state survive a process restart?

The project uses the database as the persistent source of job state and builds the execution logic around that state.

EVENTFLOW

              Job / API Request
                     │
                     ▼
              ┌──────────────┐
              │  Job Manager │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ SQLite + WAL │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │    Workers   │
              └──────┬───────┘
                     │
             ┌───────┴────────┐
             ▼                ▼
        Job succeeds       Job fails
             │                │
             ▼                ▼
         Completed       Retry + Backoff
                              │
                              ▼
                           Retry job
                              │
                    Max retries reached
                              │
                              ▼
                       Dead-Letter Queue
                       
How it works

A job is created and persisted before a worker starts processing it.

Workers claim available jobs from the database and move them through their lifecycle. Job state, retry information and execution metadata are persisted so that the system can recover from worker failures instead of relying only on in-memory state.

The main flow is:

Create Job
   ↓
Persist Job
   ↓
Worker Claims Job
   ↓
Execute
   ↓
 ┌───────────────┐
 │               │
Success         Failure
 │               │
 ↓               ↓
Completed     Retry / Backoff
                 ↓
             Try Again
                 ↓
          Max Retries Reached
                 ↓
           Dead-Letter Queue

Reliability features

Concurrent worker execution

Multiple workers can process jobs concurrently while the database is used to coordinate job ownership.

Atomic claiming helps prevent two workers from processing the same job at the same time.

Retries with backoff

Temporary failures do not immediately move a job to a permanent failure state.

Failed jobs can be retried using backoff so repeated failures do not cause continuous immediate execution.

Idempotency

A retried job should not accidentally perform the same operation multiple times.

EventFlow keeps idempotency as part of the execution design so that retry behaviour can be handled safely.

Lease-based recovery

A worker may stop unexpectedly while holding a job.

The lease mechanism allows the system to identify work that is no longer being actively processed and make it available for recovery.

Dead-letter handling

Jobs that continue to fail after the allowed retry attempts are separated from normal processing and moved to a dead-letter state.

This prevents permanently failing jobs from repeatedly entering the normal worker flow.

Priority scheduling

Jobs can be processed according to priority rather than treating every job identically.

Transactional outbox

The transactional outbox pattern is used to keep database state and outgoing events consistent.

Circuit breaker

External failures can propagate quickly when a dependency is unavailable.

The circuit breaker helps prevent continuously sending requests to a failing dependency.

SQLite WAL

SQLite Write-Ahead Logging is used to improve concurrent database access while keeping the implementation lightweight.

Job lifecycle

The job state machine is built around persistent state rather than process-local memory.

Pending
   ↓
Running
   ↓
Completed

Running
   ↓
Failed
   ↓
Retry
   ↓
Pending

Failed
   ↓
Max Retries
   ↓
Dead Letter

The exact transitions are controlled by the execution and recovery logic.

Project structure

eventflow-reliable-workflow-engine/
│
├── src/
├── tests/
├── README.md
├── requirements.txt
└── ...

The implementation is intentionally split around the core responsibilities of job management, worker execution, persistence and reliability handling.

Testing

The project includes tests for the core execution and reliability behaviour.

The test suite is intended to verify cases such as:

- job execution
- retries
- concurrent worker behaviour
- idempotency
- recovery after worker failure
- job state transitions
- failure handling

Run the tests with:

pytest

Tech stack

- Python — application and execution logic
- SQLite — persistent job state
- SQLite WAL — concurrent database access
- Pytest — testing
- Docker — containerized development/runtime
- GitHub Actions — CI

What I learned

Building EventFlow helped me understand that reliable background processing is mostly about handling failure and state correctly.

The main areas I worked with were:

- concurrency control
- database transactions
- worker coordination
- retry strategies
- idempotent execution
- crash recovery
- state machines
- failure isolation
- persistent job state

Future improvements

Some areas I would explore next:

- metrics and distributed tracing
- stronger observability around worker execution
- additional persistence backends
- horizontal worker scaling
- more advanced scheduling
- operational tooling for inspecting and replaying failed jobs

Author

Sadia Aref

Python Developer | Backend & Software Engineering

"GitHub" (https://github.com/sadiaaref)
