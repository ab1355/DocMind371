import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

class PlaybookAnalyst:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.logs_file = self.project_dir / "logs" / "outcomes.jsonl"

    def load_outcomes(self):
        """Load all logged outcomes"""
        outcomes = []
        if self.logs_file.exists():
            with open(self.logs_file) as f:
                for line in f:
                    outcomes.append(json.loads(line))
        return pd.DataFrame(outcomes)

    def analyze_template_performance(self, template_name: str):
        """Get performance stats for a template"""
        df = self.load_outcomes()
        if df.empty:
            return {}
        template_tasks = df[df.get('template', '') == template_name]
        
        if template_tasks.empty:
            return {}

        return {
            "template": template_name,
            "total_executions": len(template_tasks),
            "success_rate": (template_tasks['status'] == 'complete').mean() if 'status' in template_tasks else 0,
            "avg_quality": template_tasks['quality_score'].mean() if 'quality_score' in template_tasks else 0,
            "avg_duration_minutes": template_tasks['duration_minutes'].mean() if 'duration_minutes' in template_tasks else 0,
            "user_satisfaction": template_tasks['user_feedback'].apply(
                lambda x: x.get('rating', 0) if isinstance(x, dict) else 0
            ).mean() if 'user_feedback' in template_tasks else 0,
        }

    def rank_templates(self):
        """Rank all templates by composite score"""
        df = self.load_outcomes()
        if df.empty or 'template' not in df:
            return []
            
        templates = set(df['template'].dropna())
        rankings = []
        
        for template in templates:
            perf = self.analyze_template_performance(template)
            if not perf:
                continue
                
            # Composite score: (success × 0.4) + (quality × 0.3) + (satisfaction × 0.3)
            composite_score = (
                perf.get('success_rate', 0) * 0.4 +
                (perf.get('avg_quality', 0) / 10) * 0.3 +
                (perf.get('user_satisfaction', 0) / 5) * 0.3
            )
            rankings.append({
                **perf,
                "composite_score": composite_score
            })
            
        return sorted(rankings, key=lambda x: x['composite_score'], reverse=True)

    def detect_failures(self, threshold_hours=24):
        """Find recurring failures in last N hours"""
        df = self.load_outcomes()
        if df.empty or 'timestamp' not in df:
            return {}
            
        cutoff = datetime.now() - timedelta(hours=threshold_hours)
        recent = df[df['timestamp'] > cutoff.isoformat()]
        
        if 'status' not in recent:
            return {}
            
        failures = recent[recent['status'] != 'complete']
        if failures.empty:
            return {"recent_failures": 0}
            
        failure_patterns = failures.groupby('task_id').size().sort_values(ascending=False)
        
        return {
            "recent_failures": len(failures),
            "most_problematic_task": failure_patterns.index[0] if len(failure_patterns) > 0 else None,
            "failure_frequency": failure_patterns.to_dict()
        }

    def generate_report(self):
        """Generate comprehensive analysis report"""
        return {
            "generated_at": datetime.now().isoformat(),
            "template_rankings": self.rank_templates(),
            "failure_analysis": self.detect_failures(),
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self):
        """AI-generated recommendations based on analysis"""
        rankings = self.rank_templates()
        recommendations = []
        
        if not rankings:
            return recommendations
            
        # Recommend top performers as defaults
        if rankings[0]['composite_score'] > 0.85:
            recommendations.append({
                "type": "promote",
                "template": rankings[0]['template'],
                "reason": f"Best performer: {rankings[0]['composite_score']:.2f} score"
            })
            
        # Flag underperformers for deprecation
        if rankings[-1]['composite_score'] < 0.6:
            recommendations.append({
                "type": "deprecate",
                "template": rankings[-1]['template'],
                "reason": f"Low score: {rankings[-1]['composite_score']:.2f}"
            })
            
        return recommendations
