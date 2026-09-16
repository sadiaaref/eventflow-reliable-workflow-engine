from datetime import datetime,timezone,timedelta
from .policy import RetryPolicy,CircuitBreaker

class Engine:
    def __init__(self,store,retry=None,breaker=None):
        self.store=store; self.retry=retry or RetryPolicy()
        self.breaker=breaker or CircuitBreaker()

    def submit(self,job_id,key,payload,priority=0,max_attempts=3,now=None):
        now=now or datetime.now(timezone.utc)
        return self.store.submit(job_id,key,payload,priority,max_attempts,now)

    def work_once(self,worker,handler,now=None):
        now=now or datetime.now(timezone.utc)
        self.store.recover_expired(now)
        if not self.breaker.allow(now): return None
        job=self.store.claim(worker,now)
        if not job:return None
        try:
            result=handler(job)
            self.store.succeed(job.job_id,worker,result,now)
            self.breaker.success()
            return "SUCCEEDED"
        except Exception as exc:
            self.breaker.failure(now)
            delay=self.retry.delay(job.attempts)
            terminal=self.store.fail(job.job_id,worker,str(exc),now+timedelta(seconds=delay))
            return "DLQ" if terminal else "RETRY"
