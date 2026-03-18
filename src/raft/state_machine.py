from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json

class CommandType(Enum):
    ASSIGN_TASK = "ASSIGN_TASK"
    COMPLETE_TASK = "COMPLETE_TASK"
    UPDATE_TASK_STATUS = "UPDATE_TASK_STATUS"
    ADD_TASK = "ADD_TASK"

@dataclass
class Command:
    type: CommandType
    payload: Dict[str, Any]

@dataclass
class ProjectState:
    phases: List[Dict[str, Any]] = field(default_factory=list)
    
    def apply(self, command: Command):
        """
        Applies a command to the state machine.
        This method must be deterministic.
        """
        if command.type == CommandType.ASSIGN_TASK:
            self._assign_task(command.payload)
        elif command.type == CommandType.COMPLETE_TASK:
            self._complete_task(command.payload)
        # Add other command handlers...
        return self

    def _assign_task(self, payload: Dict[str, Any]):
        task_id = payload.get("task_id")
        assigned_to = payload.get("assigned_to")
        for phase in self.phases:
            for task in phase.get("tasks", []):
                if task.get("id") == task_id:
                    task["assigned_to"] = assigned_to
                    task["status"] = "In-Progress"
                    return

    def _complete_task(self, payload: Dict[str, Any]):
        task_id = payload.get("task_id")
        for phase in self.phases:
            for task in phase.get("tasks", []):
                if task.get("id") == task_id:
                    task["status"] = "Completed"
                    return

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)
