import json
import os
from datetime import datetime
from src.raft.node import RaftNode
from src.raft.state_machine import Command, CommandType

class Project:
    def __init__(self, node_id="node1", peers=[]):
        self.raft_node = RaftNode(node_id, peers)

    def load(self):
        if os.path.exists(self.project_file):
            with open(self.project_file, 'r') as f:
                return json.load(f)
        return {"phases": [], "tasks": []}

    def save(self):
        with open(self.project_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_next_task(self):
        for phase in self.data.get("phases", []):
            for task in phase.get("tasks", []):
                if task["status"] == "To-Do":
                    return task
        return None

    def assign_task(self, task_id, agent_name):
        command = Command(
            type=CommandType.ASSIGN_TASK,
            payload={"task_id": task_id, "assigned_to": agent_name}
        )
        self.raft_node.submit_command(command)
        return True

    def update_task_status(self, task_id, status):
        for phase in self.data.get("phases", []):
            for task in phase.get("tasks", []):
                if task["id"] == task_id:
                    task["status"] = status
                    self.save()
                    return True
        return False

    def complete_task(self, task_id, notes=""):
        command = Command(
            type=CommandType.COMPLETE_TASK,
            payload={"task_id": task_id}
        )
        self.raft_node.submit_command(command)
        return True

    def block_task(self, task_id, reason=""):
        for phase in self.data.get("phases", []):
            for task in phase.get("tasks", []):
                if task["id"] == task_id:
                    task["status"] = "Blocked"
                    task["blocker_reason"] = reason
                    self.save()
                    return True
        return False

    def get_status_summary(self):
        total = 0
        completed = 0
        for phase in self.data.get("phases", []):
            for task in phase.get("tasks", []):
                total += 1
                if task["status"] == "Complete":
                    completed += 1
        
        percentage = (completed / total * 100) if total > 0 else 0
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_percentage": round(percentage, 2)
        }

    def get_agent_status(self, agent_name):
        assigned_tasks = []
        for phase in self.data.get("phases", []):
            for task in phase.get("tasks", []):
                if task.get("assigned_to") == agent_name:
                    assigned_tasks.append(task)
        return assigned_tasks
