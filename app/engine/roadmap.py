"""Skill-gap analysis and personalised learning roadmap generation."""

from __future__ import annotations

from dataclasses import dataclass

from app.data.careers import CAREERS_BY_ID, get_career
from app.data.resources import projects_for, resources_for
from app.data.skills import SKILLS_BY_ID, skill_name
from app.engine.model import skill_target


@dataclass
class SkillGap:
    skill_id: str
    name: str
    category: str
    importance: float
    current: float
    target: float
    missing: float
    priority: str  # critical | high | medium
    rationale: str


def _priority(importance: float, missing: float) -> str:
    impact = importance * missing
    if importance >= 0.8 and missing >= 0.35:
        return "critical"
    if impact >= 0.25:
        return "high"
    return "medium"


def analyse_gap(career_id: str, proficiency: dict[str, float]) -> tuple[float, list[SkillGap]]:
    """Compare a student's proficiency against one career's requirements."""
    career = get_career(career_id)
    if not career:
        return 0.0, []

    total_weight = sum(career.required.values()) or 1.0
    achieved = 0.0
    gaps: list[SkillGap] = []

    for skill_id, importance in career.required.items():
        current = max(0.0, min(1.0, proficiency.get(skill_id, 0.0)))
        target = skill_target(importance)
        achieved += importance * current

        missing = max(0.0, target - current)
        skill = SKILLS_BY_ID.get(skill_id)
        gaps.append(
            SkillGap(
                skill_id=skill_id,
                name=skill.name if skill else skill_name(skill_id),
                category=skill.category if skill else "Other",
                importance=importance,
                current=round(current, 2),
                target=round(target, 2),
                missing=round(missing, 2),
                priority=_priority(importance, missing),
                rationale=_rationale(career.title, skill_name(skill_id), importance, missing),
            )
        )

    readiness = achieved / total_weight
    gaps.sort(key=lambda g: (-g.importance * g.missing, g.skill_id))
    return round(readiness, 4), gaps


def _rationale(career_title: str, skill_name: str, importance: float, missing: float) -> str:
    if missing <= 0.05:
        return f"You already cover {skill_name}, which {career_title} roles rely on."
    if importance >= 0.9:
        return f"{skill_name} is a core requirement for {career_title}; recruiters screen for it first."
    if importance >= 0.6:
        return f"{career_title} work regularly uses {skill_name}, so partial knowledge still helps."
    if missing > 0.4:
        return f"{skill_name} is a differentiator for {career_title} roles, though not a hard requirement."
    return f"A bonus rather than a blocker for {career_title} roles."


def _weeks_needed(importance: float, hours_available: float) -> int:
    base = 40 / max(importance, 0.25)
    adjusted = base * (12.0 / max(hours_available, 1.0))
    return int(max(2, min(20, round(adjusted))))


def build_roadmap(
    career_id: str,
    proficiency: dict[str, float],
    gaps: list[SkillGap],
    weekly_hours: int = 8,
    horizon_weeks: int = 16,
) -> dict:
    """Produce a week-by-week learning roadmap for one career."""
    career = CAREERS_BY_ID.get(career_id)
    actionable = [g for g in gaps if g.missing > 0.12]
    actionable.sort(key=lambda g: (-(g.importance * g.missing), g.skill_id))

    phases: list[dict] = []
    bucket = actionable[:6]
    if bucket:
        phase_size = max(2, (len(bucket) + 2) // 3)
        names = ("Foundation", "Core Practice", "Job-Ready Signals")
        chunks = [bucket[i : i + phase_size] for i in range(0, len(bucket), phase_size)]

        # Raw effort per phase, then scaled down so the phases exactly fill the
        # requested horizon. A roadmap that promises 29 weeks on a 16-week
        # horizon is worse than useless to a student.
        raw = []
        for chunk in chunks:
            hours = sum(
                (resources_for(g.skill_id)[0].hours if resources_for(g.skill_id) else 12) for g in chunk
            )
            raw.append((_weeks_needed(1.0, hours / max(len(chunk), 1)), hours))

        total_raw = sum(w for w, _ in raw) or 1
        scale = min(1.0, horizon_weeks / total_raw)
        allocated = [max(1, int(round(w * scale))) for w, _ in raw]

        # A short horizon can have fewer weeks than phases. Drop the smallest
        # phase (and its chunk, keeping both lists in sync) until the
        # remainder is non-negative, then push it onto the first phase. This
        # guarantees sum(allocated) == horizon_weeks.
        while len(allocated) > 1 and horizon_weeks - sum(allocated) < 0:
            smallest = min(range(len(allocated)), key=lambda i: allocated[i])
            allocated.pop(smallest)
            chunks.pop(smallest)
            names = names[: len(chunks)]
            raw.pop(smallest)
        if not allocated:
            allocated = [horizon_weeks]
            chunks = chunks[:1] or [[]]

        drift = horizon_weeks - sum(allocated)
        if drift > 0:
            allocated[0] += drift
        elif drift < 0:
            i = 0
            while drift < 0 and allocated[i] > 1:
                take = min(-drift, allocated[i] - 1)
                allocated[i] -= take
                drift += take
                i += 1

        for phase_index, chunk in enumerate(chunks):
            hours = raw[phase_index][1]
            phases.append(
                {
                    "name": names[phase_index] if phase_index < len(names) else f"Phase {phase_index + 1}",
                    "weeks": allocated[phase_index],
                    "skills": [
                        {
                            "skill_id": g.skill_id,
                            "name": g.name,
                            "importance": g.importance,
                            "current": g.current,
                            "priority": g.priority,
                        }
                        for g in chunk
                    ],
                    "estimated_hours": hours,
                    "milestone": _milestone(chunk, career.title if career else "the role"),
                }
            )

    weeks: list[dict] = []
    cursor = 1
    for phase in phases:
        for offset in range(phase["weeks"]):
            week_no = cursor + offset
            if week_no > horizon_weeks:
                break
            weeks.append(
                {
                    "week": week_no,
                    "phase": phase["name"],
                    "focus": phase["skills"][offset % len(phase["skills"])]["name"],
                    "skill_id": phase["skills"][offset % len(phase["skills"])]["skill_id"],
                    "hours": weekly_hours,
                }
            )
        cursor += phase["weeks"]

    return {
        "career_id": career_id,
        "career_title": career.title if career else career_id,
        "weekly_hours": weekly_hours,
        "horizon_weeks": horizon_weeks,
        "total_weeks": len(weeks),
        "estimated_total_hours": len(weeks) * weekly_hours,
        "phases": phases,
        "weeks": weeks[:horizon_weeks],
        "resources": _resources_for_gaps(actionable[:8]),
    }


def _milestone(chunk: list[SkillGap], career_title: str) -> str:
    names = [g.name for g in chunk]
    if len(names) == 1:
        return f"Build one demonstrable {names[0]} project relevant to {career_title} roles."
    return f"Combine {names[0]} and {names[1]} into a single portfolio project."


def _resources_for_gaps(gaps: list[SkillGap]) -> list[dict]:
    out: list[dict] = []
    for gap in gaps:
        for resource in resources_for(gap.skill_id)[:2]:
            out.append(
                {
                    "skill_id": gap.skill_id,
                    "skill_name": gap.name,
                    "priority": gap.priority,
                    "title": resource.title,
                    "kind": resource.kind,
                    "provider": resource.provider,
                    "url": resource.url,
                    "hours": resource.hours,
                }
            )
    return out


def recommend_projects(
    career_id: str,
    gaps: list[SkillGap],
    proficiency: dict[str, float],
    limit: int = 4,
) -> list[dict]:
    """Pick projects that close the largest gaps for the target career."""
    career = get_career(career_id)
    if not career:
        return []

    gap_weight = {g.skill_id: g.importance * g.missing for g in gaps}
    scored: list[tuple[float, dict]] = []
    seen: set[str] = set()

    for skill_id, weight in gap_weight.items():
        for idea in projects_for(skill_id):
            if idea.id in seen:
                continue
            overlap = sum(gap_weight.get(s, 0.0) for s in idea.skills)
            career_bonus = sum(1.0 for s in idea.skills if s in career.required)
            value = overlap * 1.4 + career_bonus * 0.25 + idea.hours / 400.0
            scored.append(
                (
                    value,
                    {
                        "id": idea.id,
                        "title": idea.title,
                        "summary": idea.summary,
                        "difficulty": idea.difficulty,
                        "estimated_hours": idea.hours,
                        "skills": [skill_name(s) for s in idea.skills],
                        "skill_ids": list(idea.skills),
                        "closes": [
                            {"skill_id": s, "name": skill_name(s)}
                            for s in idea.skills
                            if s in gap_weight and gap_weight[s] > 0.15
                        ],
                    },
                )
            )
            seen.add(idea.id)

    scored.sort(key=lambda row: -row[0])
    return [payload for _, payload in scored[:limit]]
