"""Recommendation orchestrator.

`analyse()` is the single entry point used by the API. It runs parsing, the
ML scoring layer, gap analysis, roadmap and project generation, then produces a
narrative explanation for the top matches.
"""

from __future__ import annotations

import numpy as np

from app.data.careers import CAREERS, CAREERS_BY_ID, get_career
from app.data.companies import COMPANIES_BY_ID, companies_hiring
from app.data.skills import SKILLS_BY_ID, skill_name
from app.engine import model
from app.engine.parser import DetectedSkill, extract_skills, normalise_interests, profile_strength
from app.engine.roadmap import analyse_gap, build_roadmap, recommend_projects


def _proficiency_map(detected: list[DetectedSkill]) -> dict[str, float]:
    return {d.skill_id: d.proficiency for d in detected}


def _market_signal(career_id: str) -> float:
    career = get_career(career_id)
    if not career:
        return 0.0
    return (career.demand - 1.0) / 4.0


def _quick_readiness(career_id: str, proficiency: dict[str, float]) -> float:
    """Weighted readiness without building the full detail payload."""
    career = CAREERS_BY_ID.get(career_id)
    if not career:
        return 0.0
    total = 0.0
    earned = 0.0
    for skill_id, weight in career.required.items():
        total += weight
        earned += weight * max(0.0, min(1.0, proficiency.get(skill_id, 0.0)))
    return earned / total if total else 0.0


def _company_boost(career_id: str, company_id: str | None, proficiency: dict[str, float]) -> float:
    if not company_id:
        return 0.0
    company = COMPANIES_BY_ID.get(company_id)
    if not company or career_id not in company.hiring:
        return 0.0
    # A company preference should break ties between roles the candidate can
    # plausibly do. Without this gate a flat bonus outranks real evidence and
    # recommends a 0%-readiness role to someone who is 12% ready elsewhere.
    fit = min(1.0, _quick_readiness(career_id, proficiency) / 0.35)
    if fit <= 0:
        return 0.0
    bonus = 0.04
    for skill_id, weight in company.extra_skills.items():
        if proficiency.get(skill_id, 0.0) >= 0.5:
            bonus += weight * 0.08
    return min(0.12, bonus) * fit


def _readiness_label(score: float) -> str:
    if score >= 0.8:
        return "Ready to apply"
    if score >= 0.6:
        return "Nearly ready"
    if score >= 0.4:
        return "Buildable in 3-6 months"
    if score >= 0.2:
        return "6-12 month path"
    return "Long-term path"


def _match_explanation(
    career_id: str,
    strengths: list[dict],
    gaps: list[dict],
    content: float,
    ready: float,
) -> str:
    career = CAREERS_BY_ID[career_id]
    strongest = [s["name"] for s in strengths[:3]]
    weakest = [g["name"] for g in gaps[:3] if g["missing"] > 0.2]

    if not strengths:
        return (
            f"{career.title} is a plausible direction based on your interests, but your profile does not "
            f"yet evidence core skills. {readiness_label(ready)}."
        )

    parts = [
        f"{career.title} matches your strongest evidence: {', '.join(strongest)}.",
        f"Semantic similarity between your profile and this role is {content:.2f}, "
        f"and weighted skill readiness is {ready:.0%}.",
    ]
    if weakest:
        parts.append(f"The blocking gaps are {', '.join(weakest)}.")
    else:
        parts.append("No blocking gaps were found for this role.")
    parts.append(readiness_label(ready) + ".")
    return " ".join(parts)


def readiness_label(score: float) -> str:
    return _readiness_label(score)


def _career_payload(
    career_id: str,
    content: float,
    ready: float,
    score: float,
    strengths: list[dict],
    gaps: list[dict],
) -> dict:
    career = CAREERS_BY_ID[career_id]
    return {
        "id": career.id,
        "title": career.title,
        "category": career.category,
        "description": career.description,
        "score": round(score, 4),
        "content_similarity": round(float(content), 4),
        "readiness": round(float(ready), 4),
        "readiness_label": _readiness_label(ready),
        "demand": career.demand,
        "avg_salary_usd": career.avg_salary_usd,
        "outlook": career.outlook,
        "work_styles": list(career.work_styles),
        "responsibilities": list(career.responsibilities),
        "strengths": strengths,
        "gaps": gaps,
        "hiring_companies": [c.name for c in companies_hiring(career.id)],
        "explanation": _match_explanation(career_id, strengths, gaps, float(content), float(ready)),
    }


def _slice_rows(rows: list[tuple[str, float, float]]) -> list[dict]:
    out: list[dict] = []
    for skill_id, importance, current in rows:
        target = model.skill_target(importance)
        out.append(
            {
                "skill_id": skill_id,
                "name": skill_name(skill_id),
                "importance": round(importance, 2),
                "current": round(current, 2),
                "target": round(target, 2),
                "missing": round(max(0.0, target - current), 2),
                "category": SKILLS_BY_ID[skill_id].category if skill_id in SKILLS_BY_ID else "Other",
            }
        )
    return out


def analyse(
    resume_text: str = "",
    interests_text: str = "",
    manual_skills: list[str] | None = None,
    target_career: str | None = None,
    target_company: str | None = None,
    weekly_hours: int = 8,
    horizon_weeks: int = 16,
    top_n: int = 6,
) -> dict:
    interest_ids = normalise_interests(interests_text)
    detected = extract_skills(resume_text, manual=manual_skills)
    for skill_id in interest_ids:
        if not any(d.skill_id == skill_id for d in detected):
            skill = SKILLS_BY_ID.get(skill_id)
            if skill:
                detected.append(
                    DetectedSkill(
                        skill_id=skill.id,
                        name=skill.name,
                        category=skill.category,
                        proficiency=0.45,
                        mentions=0,
                        evidence=[],
                        sections=["interest"],
                        manual=True,
                    )
                )
    detected.sort(key=lambda d: (-d.proficiency, d.name))

    proficiency = _proficiency_map(detected)
    owned = [d.skill_id for d in detected if d.proficiency >= 0.35]

    profile_text = model.profile_document(
        [d.skill_id for d in detected],
        {d.skill_id: d.proficiency for d in detected},
    )
    content_vector = model.content_scores(profile_text)
    market_vector = model.market_prior()

    scored: list[dict] = []
    for idx, career in enumerate(CAREERS):
        content = float(content_vector[idx])
        ready, detail = model.readiness(career.id, proficiency)
        boost = 0.14 if target_career and career.id == target_career else 0.0
        score = model.final_score(
            content,
            ready,
            float(market_vector[idx]),
            target_boost=boost,
            company_boost=_company_boost(career.id, target_company, proficiency),
        )
        strengths = _slice_rows([r for r in detail if r[2] >= 0.45][:6])
        gaps = _slice_rows([r for r in detail if r[2] < 0.75][:6])
        scored.append(
            _career_payload(
                career.id,
                content,
                ready,
                score,
                strengths,
                gaps,
            )
        )

    scored.sort(key=lambda row: -row["score"])
    matches = scored[:top_n]

    # An unknown target_career must not poison the whole response: fall back to
    # the best-scoring role instead of crashing downstream on a missing id.
    if target_career and target_career not in CAREERS_BY_ID:
        target_career = None
    if target_company and target_company not in COMPANIES_BY_ID:
        target_company = None

    focus_id = target_career or (matches[0]["id"] if matches else None)
    detail_payload: dict | None = None
    if focus_id and focus_id in CAREERS_BY_ID:
        career = CAREERS_BY_ID.get(focus_id)
        ready, gaps = analyse_gap(focus_id, proficiency)
        roadmap = build_roadmap(focus_id, proficiency, gaps, weekly_hours, horizon_weeks)
        projects = recommend_projects(focus_id, gaps, proficiency)
        company_fit = None
        if target_company:
            company = COMPANIES_BY_ID[target_company]
            company_fit = {
                "id": company.id,
                "name": company.name,
                "industry": company.industry,
                "location": company.location,
                "size": company.size,
                "description": company.description,
                "culture": list(company.culture),
                "hiring": [careers_id for careers_id in company.hiring],
                "hiring_titles": [
                    CAREERS_BY_ID[c].title for c in company.hiring if c in CAREERS_BY_ID
                ],
                "extra_skills": [
                    {
                        "skill_id": sid,
                        "name": skill_name(sid),
                        "weight": weight,
                        "covered": proficiency.get(sid, 0.0) >= 0.5,
                    }
                    for sid, weight in company.extra_skills.items()
                ],
            }
        detail_payload = {
            "career_id": focus_id,
            "career_title": career.title if career else focus_id,
            "readiness": round(ready, 4),
            "readiness_label": _readiness_label(ready),
            "gaps": [
                {
                    "skill_id": g.skill_id,
                    "name": g.name,
                    "category": g.category,
                    "importance": g.importance,
                    "current": g.current,
                    "target": g.target,
                    "missing": g.missing,
                    "priority": g.priority,
                    "rationale": g.rationale,
                }
                for g in gaps
            ],
            "roadmap": roadmap,
            "projects": projects,
            "company_fit": company_fit,
        }

    similar = []
    if focus_id:
        sim = model.career_similarity()[model.CAREER_INDEX[focus_id]]
        order = np.argsort(sim)[::-1]
        for col in order:
            cid = model.CAREER_IDS[int(col)]
            if cid == focus_id or sim[col] <= 0.01:
                continue
            similar.append(
                {
                    "id": cid,
                    "title": CAREERS_BY_ID[cid].title,
                    "category": CAREERS_BY_ID[cid].category,
                    "similarity": round(float(sim[col]), 4),
                }
            )
            if len(similar) >= 4:
                break

    return {
        "profile": {
            "skills_detected": len(detected),
            "skills_proficient": len(owned),
            "input_strength": profile_strength(resume_text, detected),
            "interest_skills": interest_ids,
            "strength_signal": round(
                float(np.mean([d.proficiency for d in detected])) if detected else 0.0, 3
            ),
        },
        "skills": [
            {
                "skill_id": d.skill_id,
                "name": d.name,
                "category": d.category,
                "proficiency": round(d.proficiency, 2),
                "mentions": d.mentions,
                "sections": d.sections,
                "evidence": d.evidence,
                "self_reported": d.manual,
            }
            for d in detected
        ],
        "matches": matches,
        "focus": detail_payload,
        "adjacent_skills": model.adjacent_skills(owned),
        "similar_careers": similar,
        "model": model.model_info(),
    }