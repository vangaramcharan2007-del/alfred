import enum
import json
import logging
import uuid
import time
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from jarvisx.tools.operational_db import OperationalDatabase

logger = logging.getLogger(__name__)


class WorkflowState(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"


@dataclass
class WorkflowStep:
    name: str
    action: Callable[[Dict[str, Any]], Dict[str, Any]]
    retries: int = 3
    timeout: int = 60


@dataclass
class Workflow:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = "Unnamed Workflow"
    state: WorkflowState = WorkflowState.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)
    current_step_index: int = 0
    error: Optional[str] = None


class WorkflowEngine:
    def __init__(self, db: OperationalDatabase, max_workers: int = 4):
        self.db = db
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="WorkflowEngine")
        self._init_db()

    def _init_db(self) -> None:
        with closing(self.db._get_connection()) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    state TEXT,
                    context TEXT,
                    current_step_index INTEGER,
                    error TEXT,
                    updated_at REAL
                )
            ''')
            conn.commit()

    def persist_workflow(self, workflow: Workflow) -> None:
        with closing(self.db._get_connection()) as conn:
            conn.execute('''
                INSERT INTO workflows (id, name, state, context, current_step_index, error, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    state=excluded.state,
                    context=excluded.context,
                    current_step_index=excluded.current_step_index,
                    error=excluded.error,
                    updated_at=excluded.updated_at
            ''', (
                workflow.id,
                workflow.name,
                workflow.state.value,
                json.dumps(workflow.context),
                workflow.current_step_index,
                workflow.error,
                time.time()
            ))
            conn.commit()
            
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        with closing(self.db._get_connection()) as conn:
            row = conn.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)).fetchone()
            if row:
                return Workflow(
                    id=row[0],
                    name=row[1],
                    state=WorkflowState(row[2]),
                    context=json.loads(row[3]),
                    current_step_index=row[4],
                    error=row[5]
                )
        return None

    def start(self, workflow: Workflow) -> str:
        """Starts a workflow asynchronously and returns its ID."""
        self.persist_workflow(workflow)
        self.executor.submit(self._run, workflow)
        return workflow.id

    def _run(self, workflow: Workflow) -> None:
        workflow.state = WorkflowState.RUNNING
        self.persist_workflow(workflow)

        while workflow.current_step_index < len(workflow.steps):
            step = workflow.steps[workflow.current_step_index]
            logger.info(f"Workflow {workflow.id} running step: {step.name}")
            
            success = False
            for attempt in range(step.retries):
                try:
                    result = step.action(workflow.context)
                    workflow.context.update(result)
                    success = True
                    break
                except Exception as e:
                    logger.warning(f"Workflow {workflow.id} step {step.name} failed attempt {attempt + 1}: {e}")
                    workflow.state = WorkflowState.RETRYING
                    self.persist_workflow(workflow)
                    time.sleep(1) # simple backoff
                    
            if not success:
                workflow.state = WorkflowState.FAILED
                workflow.error = f"Step {step.name} failed after {step.retries} attempts."
                self.persist_workflow(workflow)
                logger.error(workflow.error)
                return

            workflow.current_step_index += 1
            workflow.state = WorkflowState.RUNNING
            self.persist_workflow(workflow)

        workflow.state = WorkflowState.COMPLETED
        self.persist_workflow(workflow)
        logger.info(f"Workflow {workflow.id} completed successfully.")
