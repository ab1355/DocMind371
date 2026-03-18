import json
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
from datetime import datetime

@dataclass
class Task:
    id: str
    name: str
    required_skills: Dict[str, str]  # {"skill_id": "required_level"}
    priority: int  # 1-10 (10 = highest)
    estimated_duration_minutes: int
    deadline_hours: int

@dataclass
class Agent:
    id: str
    name: str
    skills: Dict[str, Dict]  # {"skill_id": {"level", "rating", "confidence"}}
    current_load: int
    max_capacity: int
    reliability_score: float
    avg_completion_time: float

class AgentAssignmentEngine:
    def __init__(self, agents_file: str = "agents.json"):
        self.agents = []
        if Path(agents_file).exists():
            with open(agents_file) as f:
                data = json.load(f)
                # Parse agents here in a real implementation
                pass

    def calculate_agent_fit_score(self, agent: Agent, task: Task) -> Dict:
        """
        Calculate how well an agent is suited for a task.
        Score = (skill_match × 0.4) + (capacity × 0.3) + (reliability × 0.3)
        """
        # Skill match score
        skill_match_scores = []
        for required_skill, required_level in task.required_skills.items():
            if required_skill in agent.skills:
                agent_skill = agent.skills[required_skill]
                level_match = self._level_match(agent_skill.get('level', 'novice'), required_level)
                rating = agent_skill.get('rating', 0) / 5.0  # Normalize to 0-1
                confidence = agent_skill.get('confidence', 0)
                skill_score = (level_match * 0.5 + rating * 0.3 + confidence * 0.2)
                skill_match_scores.append(skill_score)
            else:
                skill_match_scores.append(0)  # Missing required skill
                
        avg_skill_match = sum(skill_match_scores) / len(skill_match_scores) if skill_match_scores else 0
        
        # Capacity score (prefer agents with more availability)
        available_slots = agent.max_capacity - agent.current_load
        capacity_score = min(available_slots / max(agent.max_capacity, 1), 1.0)
        
        # Reliability score (prefer agents with good track record)
        reliability_score = agent.reliability_score
        
        # Composite score
        fit_score = (
            avg_skill_match * 0.4 +
            capacity_score * 0.3 +
            reliability_score * 0.3
        )
        
        # Urgency multiplier (if deadline is tight and agent is reliable)
        if task.deadline_hours < 4 and reliability_score > 0.9:
            fit_score *= 1.2
            
        return {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "fit_score": fit_score,
            "skill_match": avg_skill_match,
            "capacity_score": capacity_score,
            "reliability_score": reliability_score,
            "estimated_completion": self._estimate_completion(agent, task),
            "reasoning": self._generate_reasoning(agent, task, fit_score)
        }

    def assign_task(self, task: Task, agents: List[Agent]) -> Dict:
        """Find best agent for task"""
        if not agents:
            return {"error": "No agents available"}
            
        scores = [self.calculate_agent_fit_score(agent, task) for agent in agents]
        scores.sort(key=lambda x: x['fit_score'], reverse=True)
        
        top_3 = scores[:3]
        
        return {
            "task_id": task.id,
            "recommendations": top_3,
            "recommended_agent": top_3[0] if top_3 else None,
            "alternatives": top_3[1:] if len(top_3) > 1 else [],
            "timestamp": datetime.now().isoformat()
        }

    def _level_match(self, agent_level: str, required_level: str) -> float:
        """Map skill levels to match scores"""
        levels = {"novice": 0.5, "intermediate": 1.0, "expert": 1.5, "master": 2.0}
        agent_lvl = levels.get(agent_level, 0)
        required_lvl = levels.get(required_level, 1.0)
        
        if agent_lvl >= required_lvl:
            return 1.0
        else:
            return agent_lvl / required_lvl if required_lvl > 0 else 0

    def _estimate_completion(self, agent: Agent, task: Task) -> Dict:
        """Estimate completion time and date"""
        adjusted_time = task.estimated_duration_minutes / max(agent.avg_completion_time, 0.1)
        return {
            "minutes": adjusted_time,
            "hours": adjusted_time / 60,
            "confidence": 0.85
        }

    def _generate_reasoning(self, agent: Agent, task: Task, fit_score: float) -> str:
        """Generate human-readable explanation"""
        strengths = []
        if fit_score > 0.8:
            strengths.append("Excellent fit for this task")
            
        for skill_id, required_level in task.required_skills.items():
            if skill_id in agent.skills:
                agent_level = agent.skills[skill_id].get('level', '')
                if agent_level == "expert" or agent_level == "master":
                    strengths.append(f"Expert in {skill_id}")
                    
        available_slots = agent.max_capacity - agent.current_load
        if available_slots > 2:
            strengths.append(f"Good availability ({available_slots} slots free)")
            
        return " | ".join(strengths) if strengths else "Adequate fit"
