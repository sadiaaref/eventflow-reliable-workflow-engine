from datetime import datetime,timezone,timedelta
from eventflow.store import JobStore
from eventflow.engine import Engine
from eventflow.models import State
from eventflow.policy import RetryPolicy

NOW=datetime(2026,1,1,tzinfo=timezone.utc)

def test_idempotency():
    e=Engine(JobStore(":memory:"))
    assert e.submit("1","same","x",now=NOW)==("1",True)
    assert e.submit("2","same","x",now=NOW)==("1",False)

def test_priority():
    s=JobStore(":memory:"); e=Engine(s)
    e.submit("low","l","x",priority=1,now=NOW)
    e.submit("high","h","x",priority=10,now=NOW)
    assert s.claim("w",NOW).job_id=="high"

def test_success_and_outbox():
    s=JobStore(":memory:"); e=Engine(s); e.submit("1","k","x",now=NOW)
    assert e.work_once("w",lambda j:"ok",NOW)=="SUCCEEDED"
    assert s.get("1").state is State.SUCCEEDED
    assert len(s.outbox())==1

def test_retry_then_dlq():
    s=JobStore(":memory:"); e=Engine(s,RetryPolicy(1,jitter=0))
    e.submit("1","k","x",max_attempts=2,now=NOW)
    bad=lambda j: (_ for _ in ()).throw(RuntimeError("boom"))
    assert e.work_once("w",bad,NOW)=="RETRY"
    assert e.work_once("w",bad,NOW+timedelta(seconds=3))=="DLQ"
    assert s.get("1").state is State.DLQ

def test_lease_recovery():
    s=JobStore(":memory:"); e=Engine(s); e.submit("1","k","x",now=NOW)
    assert s.claim("dead",NOW,lease_seconds=1).state is State.RUNNING
    assert s.recover_expired(NOW+timedelta(seconds=2))==1
    assert s.get("1").state is State.RETRY_WAIT

def test_circuit_breaker():
    s=JobStore(":memory:"); e=Engine(s); e.breaker.threshold=1
    e.submit("1","k","x",now=NOW)
    bad=lambda j: (_ for _ in ()).throw(RuntimeError("boom"))
    assert e.work_once("w",bad,NOW)=="RETRY"
    assert e.work_once("w",lambda j:"ok",NOW) is None
