import argparse
from datetime import datetime, timezone

from .store import JobStore
from .engine import Engine


DB_PATH = "eventflow.db"


def build_engine():
    store = JobStore(DB_PATH)
    return store, Engine(store)


def submit_job(args):
    store, engine = build_engine()

    job_id, created = engine.submit(
        job_id=args.job_id,
        key=args.idempotency_key,
        payload=args.payload,
        priority=args.priority,
        max_attempts=args.max_attempts,
    )

    if created:
        print(f"SUBMITTED {job_id}")
    else:
        print(f"EXISTING {job_id}")


def show_status(args):
    store, _ = build_engine()

    job = store.get(args.job_id)

    if not job:
        print("NOT_FOUND")
        return

    print(f"JOB: {job.job_id}")
    print(f"STATE: {job.state.value}")
    print(f"ATTEMPTS: {job.attempts}")
    print(f"PRIORITY: {job.priority}")

    if job.worker_id:
        print(f"WORKER: {job.worker_id}")

    if job.last_error:
        print(f"ERROR: {job.last_error}")


def run_worker(args):
    store, engine = build_engine()

    def handler(job):
        return f"processed:{job.job_id}"

    result = engine.work_once(
        worker=args.worker,
        handler=handler,
        now=datetime.now(timezone.utc),
    )

    if result is None:
        print("NO_JOB")
    else:
        print(result)


def main():
    parser = argparse.ArgumentParser(
        prog="eventflow",
        description="Reliable asynchronous workflow engine",
    )

    subparsers = parser.add_subparsers(dest="command")

    submit = subparsers.add_parser(
        "submit",
        help="Submit a new job",
    )
    submit.add_argument("job_id")
    submit.add_argument("idempotency_key")
    submit.add_argument("payload")
    submit.add_argument("--priority", type=int, default=0)
    submit.add_argument("--max-attempts", type=int, default=3)
    submit.set_defaults(func=submit_job)

    status = subparsers.add_parser(
        "status",
        help="Show job status",
    )
    status.add_argument("job_id")
    status.set_defaults(func=show_status)

    run = subparsers.add_parser(
        "run",
        help="Run one worker cycle",
    )
    run.add_argument(
        "--worker",
        default="worker-1",
    )
    run.set_defaults(func=run_worker)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()