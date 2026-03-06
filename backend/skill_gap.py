"""
Skill Gap Analysis Module — EduShield AI
Compares student skill profiles against target job role requirements
and generates personalized learning roadmaps.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Job Role Skill Requirements (Extensible)
# ─────────────────────────────────────────────
ROLE_REQUIREMENTS = {
    "backend_engineer": {
        "title": "Backend Engineer",
        "skills": {
            "dsa": 80,
            "java": 70,
            "system_design": 70,
            "database": 60,
            "api_design": 65,
            "python": 60
        }
    },
    "data_scientist": {
        "title": "Data Scientist",
        "skills": {
            "python": 80,
            "ml": 75,
            "statistics": 70,
            "sql": 60,
            "data_visualization": 55,
            "deep_learning": 65
        }
    },
    "frontend_developer": {
        "title": "Frontend Developer",
        "skills": {
            "html_css": 80,
            "javascript": 85,
            "react": 75,
            "ui_ux": 60,
            "typescript": 55,
            "testing": 50
        }
    },
    "devops_engineer": {
        "title": "DevOps Engineer",
        "skills": {
            "linux": 75,
            "docker": 70,
            "ci_cd": 70,
            "cloud": 65,
            "scripting": 60,
            "monitoring": 55
        }
    },
    "ml_engineer": {
        "title": "ML Engineer",
        "skills": {
            "python": 85,
            "ml": 80,
            "deep_learning": 75,
            "mlops": 65,
            "system_design": 60,
            "data_engineering": 55
        }
    }
}


def _get_priority(gap: float) -> str:
    """Determine priority based on gap magnitude"""
    if gap >= 40:
        return "high"
    elif gap >= 20:
        return "medium"
    else:
        return "low"


def _get_priority_order(priority: str) -> int:
    """Numeric sort key for priorities"""
    return {"high": 0, "medium": 1, "low": 2}.get(priority, 3)


def analyze_skill_gap(student_skills: Dict[str, float], 
                       target_role: str) -> Dict[str, Any]:
    """
    Compare student skills against a target role's requirements.
    
    Args:
        student_skills: e.g. {"dsa": 40, "java": 50, "system_design": 10}
        target_role: Key from ROLE_REQUIREMENTS
    
    Returns:
        Skill gap analysis with per-skill gaps, priorities, and roadmap
    """
    if target_role not in ROLE_REQUIREMENTS:
        available = list(ROLE_REQUIREMENTS.keys())
        return {"error": f"Unknown role: {target_role}. Available: {available}"}
    
    role = ROLE_REQUIREMENTS[target_role]
    required_skills = role["skills"]
    
    gaps = {}
    total_gap = 0
    skills_met = 0
    
    for skill, required_level in required_skills.items():
        student_level = student_skills.get(skill, 0)
        student_level = max(0, min(100, student_level))  # clamp 0-100
        
        gap = max(0, required_level - student_level)
        priority = _get_priority(gap)
        
        gaps[skill] = {
            "required": required_level,
            "current": student_level,
            "gap": gap,
            "priority": priority,
            "met": gap == 0
        }
        
        total_gap += gap
        if gap == 0:
            skills_met += 1
    
    # Overall readiness percentage
    max_possible_gap = sum(required_skills.values())
    readiness_pct = round((1 - total_gap / max_possible_gap) * 100, 1) if max_possible_gap > 0 else 100
    
    # Generate learning roadmap
    roadmap = generate_roadmap(gaps)
    
    result = {
        "target_role": role["title"],
        "role_key": target_role,
        "skill_gaps": gaps,
        "readiness_percentage": readiness_pct,
        "skills_met": skills_met,
        "total_skills": len(required_skills),
        "roadmap": roadmap
    }
    
    logger.info(f"Skill gap analysis for {target_role}: readiness={readiness_pct}%, "
                f"skills met={skills_met}/{len(required_skills)}")
    
    return result


def generate_roadmap(gaps: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """
    Generate a week-by-week learning roadmap prioritizing the biggest gaps.
    
    Args:
        gaps: Output from analyze_skill_gap's per-skill analysis
    
    Returns:
        List of weekly study plan entries
    """
    # Sort skills by gap (descending), then by priority
    sorted_skills = sorted(
        [(skill, info) for skill, info in gaps.items() if info["gap"] > 0],
        key=lambda x: (-x[1]["gap"], _get_priority_order(x[1]["priority"]))
    )
    
    if not sorted_skills:
        return [{"week": "—", "focus": "All skills met!", "action": "Practice interview questions", "hours_per_week": 5}]
    
    roadmap = []
    week = 1
    
    for skill, info in sorted_skills:
        gap = info["gap"]
        skill_label = skill.replace("_", " ").title()
        
        # Estimate weeks needed based on gap size
        if gap >= 40:
            num_weeks = 2
            hours = 15
            action = f"Intensive study: {skill_label} fundamentals + practice problems"
        elif gap >= 20:
            num_weeks = 1
            hours = 10
            action = f"Focused review: {skill_label} concepts + hands-on exercises"
        else:
            num_weeks = 1
            hours = 5
            action = f"Quick refresher: {skill_label} key topics + mock tests"
        
        end_week = week + num_weeks - 1
        week_label = f"Week {week}" if num_weeks == 1 else f"Week {week}–{end_week}"
        
        roadmap.append({
            "week": week_label,
            "focus": skill_label,
            "gap": gap,
            "priority": info["priority"],
            "action": action,
            "hours_per_week": hours
        })
        
        week = end_week + 1
    
    return roadmap


def get_available_roles() -> List[Dict[str, Any]]:
    """Return list of available roles for the UI selector"""
    return [
        {
            "key": key,
            "title": role["title"],
            "skills": list(role["skills"].keys()),
            "skill_count": len(role["skills"])
        }
        for key, role in ROLE_REQUIREMENTS.items()
    ]
