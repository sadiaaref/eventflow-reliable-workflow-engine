import random

class RetryPolicy:
    def __init__(self,base_seconds=2,max_seconds=300,jitter=.2,seed=None):
        self.base=base_seconds; self.maximum=max_seconds
        self.jitter=jitter; self.random=random.Random(seed)
    def delay(self,attempt):
        raw=min(self.maximum,self.base*(2**max(0,attempt-1)))
        return raw*(1+self.random.uniform(-self.jitter,self.jitter))

class CircuitBreaker:
    def __init__(self,threshold=3,recovery_seconds=30):
        self.threshold=threshold; self.recovery_seconds=recovery_seconds
        self.failures=0; self.opened_at=None
    def allow(self,now):
        return self.opened_at is None or (now-self.opened_at).total_seconds()>=self.recovery_seconds
    def success(self):
        self.failures=0; self.opened_at=None
    def failure(self,now):
        self.failures+=1
        if self.failures>=self.threshold: self.opened_at=now
