EventFlow

Reliable Workflow Engine built with Python and SQLite

EventFlow is a workflow/job execution engine focused on reliable background processing.

It supports concurrent workers, job scheduling, retries, idempotent execution, failure recovery, priority-based processing, and persistent job state without relying on an external message broker.

The project was built to explore how a reliable job execution system handles concurrency, worker failures, retries, and process restarts.

Why I Built This

A basic background-job system is straightforward until failures and concurrency become part of the problem.

EventFlow focuses on questions such as:

- What happens when a worker crashes while processing a job?
- How do multiple workers avoid claiming the same job?
- How should failed jobs be retried?
- How can retries be handled safely?
- How does job state survive a process restart?
- What happens when a job continues to fail?

The database acts as the persistent source of job state, while workers coordinate execution through that state.

Architecture

                         EVENTFLOW
                            │
                            ▼
                     ┌─────────────┐
                     │ Job Manager │
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ SQLite + WAL│
                     │  Job State  │
                     └──────┬──────┘
                            │
                     Atomic Claiming
                            │
                            ▼
                     ┌─────────────┐
                     │   Workers   │
                     └──────┬──────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
               Success              Failure
                  │                   │
                  ▼                   ▼
             Completed          Retry + Backoff
                                      │
                                      ▼
                                  Retry Job
                                      │
                              Max Retries?
                               │         │
                              No        Yes
                               │         │
                               └────┐    ▼
                                    │  Dead Letter
                                    │
                                    └──→ Retry

Main Flow

Job Request
     │
     ▼
Store Job
     │
     ▼
Worker Claims Job
     │
     ▼
Execute Job
     │
 ┌───┴───────────┐
 │               │
 ▼               ▼
Success        Failure
 │               │
 ▼               ▼
Completed   Retry + Backoff
                 │
                 ▼
            Retry Limit?
             │        │
            No       Yes
             │        │
             ▼        ▼
         Retry Job   Dead Letter

Reliability Features

Concurrent Workers

Multiple workers can process jobs concurrently.

Atomic job claiming is used to coordinate ownership and prevent multiple workers from processing the same job simultaneously.

Retries with Backoff

Transient failures can be retried instead of immediately becoming permanent failures.

Backoff prevents repeated failures from causing continuous immediate execution.

Idempotency

Jobs may be executed more than once because of retries or recovery.

EventFlow incorporates idempotency into the execution design so repeated execution can be handled safely.

Lease-Based Recovery

A worker can fail while processing a job.

Leases allow the system to detect work that is no longer actively being processed and make it available for recovery.

Dead-Letter Handling

Jobs that continue to fail after the allowed retry attempts are moved to a dead-letter state.

This keeps permanently failing jobs out of the normal processing flow.

Priority Scheduling

Jobs can be processed according to priority instead of treating every job equally.

Transactional Outbox

The transactional outbox pattern is used to keep database changes and outgoing events consistent.

Circuit Breaker

The circuit breaker helps prevent repeated calls to an unavailable external dependency.

SQLite WAL

SQLite Write-Ahead Logging is used to improve concurrent database access while keeping the system lightweight.

Job Lifecycle

The job state machine is based on persistent state.

Pending
   │
   ▼
Running
   │
   ├──────────────► Completed
   │
   ▼
 Failed
   │
   ▼
 Retry
   │
   ▼
 Pending

Failed
   │
   ▼
Max Retries
   │
   ▼
Dead Letter

Persistent job state allows execution and recovery decisions to survive process restarts.

Project Structure

eventflow-reliable-workflow-engine/
│
├── src/
├── tests/
├── README.md
├── requirements.txt
└── ...

The implementation is organized around job management, worker execution, persistence, and reliability handling.

Testing

The project includes tests covering core execution and reliability behaviour.

Areas include:

- Job execution
- Retry behaviour
- Concurrent worker execution
- Idempotency
- Worker failure recovery
- Job state transitions
- Failure handling

Run the test suite with:

pytest

Tech Stack

- Python — application and execution logic
- SQLite — persistent job state
- SQLite WAL — concurrent database access
- Pytest — testing
- Docker — containerized development/runtime
- GitHub Actions — CI

What I Learned

Building EventFlow gave me practical experience with the problems that appear when background processing needs to remain reliable under failure and concurrency.

Key areas included:

- Concurrency control
- Database transactions
- Worker coordination
- Retry strategies
- Idempotent execution
- Crash recovery
- State machines
- Failure isolation
- Persistent job state

Future Improvements

Possible areas for further development:

- Metrics and distributed tracing
- More detailed worker observability
- Additional persistence backends
- Horizontal worker scaling
- More advanced scheduling
- Operational tooling for inspecting and replaying failed jobs

Author

Sadia Aref

Python Developer | Backend & Software Engineering

"GitHub" (https://github.com/sadiaaref)
