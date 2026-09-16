import sqlite3
from datetime import datetime
from .models import Job,State

class JobStore:
    def __init__(self,path="eventflow.db"):
        self.db=sqlite3.connect(path,check_same_thread=False,isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS jobs(
          job_id TEXT PRIMARY KEY,idempotency_key TEXT UNIQUE,payload TEXT,
          priority INTEGER,max_attempts INTEGER,state TEXT,attempts INTEGER,
          available_at TEXT,lease_until TEXT,worker_id TEXT,last_error TEXT);
        CREATE INDEX IF NOT EXISTS ready_idx ON jobs(state,available_at,priority);
        CREATE TABLE IF NOT EXISTS outbox(
          event_id INTEGER PRIMARY KEY AUTOINCREMENT,job_id TEXT UNIQUE,
          event_type TEXT,payload TEXT,created_at TEXT);
        """)

    def submit(self,job_id,key,payload,priority,max_attempts,now):
        cur=self.db.execute(
            "INSERT OR IGNORE INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (job_id,key,payload,priority,max_attempts,State.QUEUED.value,0,
             now.isoformat(),None,None,None))
        if cur.rowcount: return job_id,True
        row=self.db.execute("SELECT job_id FROM jobs WHERE idempotency_key=?",(key,)).fetchone()
        return row["job_id"],False

    def get(self,job_id):
        r=self.db.execute("SELECT * FROM jobs WHERE job_id=?",(job_id,)).fetchone()
        if not r:return None
        return Job(r["job_id"],r["idempotency_key"],r["payload"],r["priority"],
                   r["max_attempts"],State(r["state"]),r["attempts"],
                   datetime.fromisoformat(r["available_at"]),
                   datetime.fromisoformat(r["lease_until"]) if r["lease_until"] else None,
                   r["worker_id"],r["last_error"])

    def claim(self,worker,now,lease_seconds=30):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            r=self.db.execute("""SELECT * FROM jobs
              WHERE state IN (?,?) AND available_at<=?
              ORDER BY priority DESC,available_at ASC,job_id ASC LIMIT 1""",
              (State.QUEUED.value,State.RETRY_WAIT.value,now.isoformat())).fetchone()
            if not r:
                self.db.execute("COMMIT"); return None
            lease=datetime.fromtimestamp(now.timestamp()+lease_seconds,now.tzinfo)
            self.db.execute("""UPDATE jobs SET state=?,attempts=attempts+1,
              lease_until=?,worker_id=? WHERE job_id=?""",
              (State.RUNNING.value,lease.isoformat(),worker,r["job_id"]))
            self.db.execute("COMMIT")
            return self.get(r["job_id"])
        except:
            self.db.execute("ROLLBACK"); raise

    def succeed(self,job_id,worker,result,now):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            r=self.db.execute("""SELECT 1 FROM jobs
              WHERE job_id=? AND state=? AND worker_id=?""",
              (job_id,State.RUNNING.value,worker)).fetchone()
            if not r:self.db.execute("ROLLBACK");return False
            self.db.execute("""UPDATE jobs SET state=?,lease_until=NULL,worker_id=NULL
              WHERE job_id=?""",(State.SUCCEEDED.value,job_id))
            self.db.execute("""INSERT OR IGNORE INTO outbox
              (job_id,event_type,payload,created_at) VALUES(?,?,?,?)""",
              (job_id,"job.succeeded",result,now.isoformat()))
            self.db.execute("COMMIT"); return True
        except:
            self.db.execute("ROLLBACK"); raise

    def fail(self,job_id,worker,error,available_at):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            r=self.db.execute("""SELECT attempts,max_attempts FROM jobs
              WHERE job_id=? AND state=? AND worker_id=?""",
              (job_id,State.RUNNING.value,worker)).fetchone()
            if not r:self.db.execute("ROLLBACK");return False
            state=State.DLQ if r["attempts"]>=r["max_attempts"] else State.RETRY_WAIT
            self.db.execute("""UPDATE jobs SET state=?,available_at=?,lease_until=NULL,
              worker_id=NULL,last_error=? WHERE job_id=?""",
              (state.value,available_at.isoformat(),error,job_id))
            self.db.execute("COMMIT"); return state is State.DLQ
        except:
            self.db.execute("ROLLBACK");raise

    def recover_expired(self,now):
        cur=self.db.execute("""UPDATE jobs SET state=?,worker_id=NULL,lease_until=NULL,
          available_at=? WHERE state=? AND lease_until IS NOT NULL AND lease_until<=?""",
          (State.RETRY_WAIT.value,now.isoformat(),State.RUNNING.value,now.isoformat()))
        return cur.rowcount

    def outbox(self):
        return self.db.execute("SELECT * FROM outbox ORDER BY event_id").fetchall()
