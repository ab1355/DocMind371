import json
from datetime import datetime
from pathlib import Path

class OutcomeLogger:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.logs_dir = Path(f"logs/{project_name}")
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def log_task_completion(self, task_id: str, agent_id: str,
                            duration_minutes: int, quality_score: float,
                            user_feedback: dict = None, blockers: list = None):
        """Log a completed task with outcome metrics"""
        outcome = {
            "task_id": task_id,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "quality_score": quality_score,
            "user_feedback": user_feedback or {},
            "blockers": blockers or [],
        }
        with open(self.logs_dir / "outcomes.jsonl", "a") as f:
            f.write(json.dumps(outcome) + "\n")

    def log_workflow_execution(self, workflow_name: str, steps_completed: int,
                               total_steps: int, success: bool, duration_minutes: int):
        """Log workflow execution"""
        workflow_log = {
            "workflow_name": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "steps_completed": steps_completed,
            "total_steps": total_steps,
            "success": success,
            "duration_minutes": duration_minutes,
        }
        with open(self.logs_dir / "workflows.jsonl", "a") as f:
            f.write(json.dumps(workflow_log) + "\n")
