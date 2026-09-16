from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class State(str,Enum):
    QUEUED="QUEUED"; RUNNING="RUNNING"; SUCCEEDED="SUCCEEDED"
    RETRY_WAIT="RETRY_WAIT"; DLQ="DLQ"

@dataclass(frozen=True)
class Job:
    job_id:str
    idempotency_key:str
    payload:str
    priority:int
    max_attempts:int
    state:State
    attempts:int
    available_at:datetime
    lease_until:datetime|None
    worker_id:str|None
    last_error:str|None
