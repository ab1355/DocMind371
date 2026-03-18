# AI Agent Integration Guide

This guide details how to integrate your autonomous AI agents with the 371 Minds Command Center.

## Architecture
The system uses a JSON-based "Source of Truth" file (`371-minds-project.json`) that is read and updated by both the Python API and the HTML Dashboard.

## Agent Workflow
1. **Read State:** Agents load the project state using the Python API.
2. **Get Task:** Agents call `get_next_task()` to find available work.
3. **Claim Task:** Agents call `assign_task(task_id, agent_name)` to claim work.
4. **Execute:** Agents perform the task (e.g., deploy, code, research).
5. **Report:** Agents call `complete_task(task_id, notes)` to mark work as done.
