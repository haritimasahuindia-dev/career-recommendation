"""FastAPI application for the AI-based student career & skill recommender.

Server-rendered multi-page frontend plus a JSON API used by the analysis tool.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from app import __version__
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.data.careers import CAREERS, CAREERS_BY_ID, get_career
from app.data.companies import COMPANIES, COMPANIES_BY_ID, all_industries, get_company
from app.data.resources import PROJECT_IDEAS, RESOURCES
from app.data.skills import SKILLS, SKILLS_BY_ID
from app.engine import model
from app.engine.parser import extract_skills
from app.engine.recommend import analyse, readiness_label
from app.engine.roadmap import analyse_gap, build_roadmap, recommend_projects

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="Student Recommendation — AI Career & Skill Recommendation",
    description=(
        "Personalised career matches, weighted skill-gap analysis, learning roadmaps "
        "and portfolio projects for students."
    ),
    version=__version__,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# --------------------------------------------------------------------------
# view helpers
# --------------------------------------------------------------------------
def _career_proficiency(career_id: str) -> dict[str, float]:
    """Per-skill importance, used for the 'full coverage' plan preview."""
    career = get_career(career_id)
    if not career:
        return {}
    return {sid: 0.0 for sid in career.required}


def _career_detail(career) -> dict:
    skills = [
        {
            "id": sid,
            "name": SKILLS_BY_ID[sid].name if sid in SKILLS_BY_ID else sid,
            "category": SKILLS_BY_ID[sid].category if sid in SKILLS_BY_ID else "Other",
            "weight": weight,
        }
        for sid, weight in sorted(career.required.items(), key=lambda kv: -kv[1])
    ]
    projects = []
    seen: set[str] = set()
    for sid in career.required:
        for idea in PROJECT_IDEAS.get(sid, ()):
            if idea.id in seen:
                continue
            seen.add(idea.id)
            projects.append(
                {
                    "id": idea.id,
                    "title": idea.title,
                    "summary": idea.summary,
                    "difficulty": idea.difficulty,
                    "hours": idea.hours,
                    "skill_ids": list(idea.skills),
                }
            )
    projects.sort(key=lambda p: p["hours"])
    companies = [c for c in COMPANIES if career.id in c.hiring]

    related = [
        SKILLS_BY_ID[s]
        for s in sorted(career.required, key=lambda k: -career.required[k])
        if s in SKILLS_BY_ID
    ][:12]

    top = sorted(career.required, key=lambda k: -career.required[k])[:3]
    return {
        "id": career.id,
        "title": career.title,
        "category": career.category,
        "description": career.description,
        "demand": career.demand,
        "avg_salary_usd": career.avg_salary_usd,
        "outlook": career.outlook,
        "work_styles": list(career.work_styles),
        "styles": list(career.work_styles),
        "responsibilities": list(career.responsibilities),
        "skills": skills,
        "projects": projects[:4],
        "companies": companies,
        "related": related,
        "readiness_hint": f"top: {', '.join(SKILLS_BY_ID[s].name for s in top if s in SKILLS_BY_ID)}",
    }


def _career_cards() -> list[dict]:
    out = []
    for c in CAREERS:
        out.append(
            {
                "id": c.id,
                "title": c.title,
                "category": c.category,
                "description": c.description,
                "demand": c.demand,
                "avg_salary_usd": c.avg_salary_usd,
                "skills": [
                    {
                        "id": sid,
                        "name": SKILLS_BY_ID[sid].name if sid in SKILLS_BY_ID else sid,
                    }
                    for sid in sorted(c.required, key=lambda k: -c.required[k])
                ],
                "readiness_hint": ", ".join(
                    SKILLS_BY_ID[s].name
                    for s in sorted(c.required, key=lambda k: -c.required[k])[:2]
                    if s in SKILLS_BY_ID
                ),
            }
        )
    return out


def _skill_cards() -> list[dict]:
    usage: dict[str, list[dict]] = {}
    for career in CAREERS:
        for sid, weight in career.required.items():
            if weight < 0.5:
                continue
            usage.setdefault(sid, []).append({"id": career.id, "title": career.title, "weight": weight})

    out = []
    for s in SKILLS:
        users = sorted(usage.get(s.id, []), key=lambda u: -u["weight"])
        out.append(
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "aliases": list(s.aliases),
                "keywords": list(s.keywords),
                "demand": len(users),
                "careers": users,
            }
        )
    return sorted(out, key=lambda r: (-r["demand"], r["name"]))


def _project_cards() -> list[dict]:
    seen: set[str] = set()
    out = []
    for ideas in PROJECT_IDEAS.values():
        for idea in ideas:
            if idea.id in seen:
                continue
            seen.add(idea.id)
            out.append(
                {
                    "id": idea.id,
                    "title": idea.title,
                    "summary": idea.summary,
                    "difficulty": idea.difficulty,
                    "hours": idea.hours,
                    "skill_ids": list(idea.skills),
                    "skill_names": [
                        SKILLS_BY_ID[s].name if s in SKILLS_BY_ID else s for s in idea.skills
                    ],
                }
            )
    return sorted(out, key=lambda p: (p["difficulty"], p["hours"]))


def _resource_cards() -> list[dict]:
    out = []
    for skill_id, items in RESOURCES.items():
        skill = SKILLS_BY_ID.get(skill_id)
        name = skill.name if skill else skill_id
        for r in items:
            out.append(
                {
                    "skill_id": skill_id,
                    "skill_name": name,
                    "title": r.title,
                    "kind": r.kind,
                    "provider": r.provider,
                    "url": r.url,
                    "hours": r.hours,
                }
            )
    return sorted(out, key=lambda r: (r["kind"], r["skill_name"]))


def _skill_detail(skill_id: str) -> dict | None:
    skill = SKILLS_BY_ID.get(skill_id)
    if not skill:
        return None
    users = [
        {"id": c.id, "title": c.title, "weight": c.required[skill_id]}
        for c in CAREERS
        if skill_id in c.required
    ]
    users.sort(key=lambda u: -u["weight"])
    projects = [
        {
            "id": idea.id,
            "title": idea.title,
            "summary": idea.summary,
            "difficulty": idea.difficulty,
            "hours": idea.hours,
        }
        for idea in PROJECT_IDEAS.get(skill_id, ())
    ]
    resources = [
        {
            "title": r.title,
            "kind": r.kind,
            "provider": r.provider,
            "url": r.url,
            "hours": r.hours,
        }
        for r in RESOURCES.get(skill_id, ())
    ]
    return {
        "id": skill.id,
        "name": skill.name,
        "category": skill.category,
        "aliases": list(skill.aliases),
        "keywords": list(skill.keywords),
        "careers": users,
        "projects": projects,
        "resources": resources,
    }


def _project_detail(project_id: str) -> dict | None:
    for ideas in PROJECT_IDEAS.values():
        for idea in ideas:
            if idea.id == project_id:
                return {
                    "id": idea.id,
                    "title": idea.title,
                    "summary": idea.summary,
                    "difficulty": idea.difficulty,
                    "hours": idea.hours,
                    "skills": [
                        {"id": sid, "name": SKILLS_BY_ID[sid].name if sid in SKILLS_BY_ID else sid}
                        for sid in idea.skills
                    ],
                }
    return None


def _site_stats() -> dict:
    info = model.model_info()
    return {
        "careers": len(CAREERS),
        "skills": len(SKILLS),
        "companies": len(COMPANIES),
        "projects": len(_project_cards()),
        "resources": len(_resource_cards()),
        "features": info["tfidf_features"],
        "components": info["latent_components"],
        "explained": info["explained_variance"],
        "weights": info["weights"],
    }


def _page(name: str, request: Request, *, status_code: int = 200, **ctx):
    ctx.setdefault("stats", _site_stats())
    ctx.setdefault("career_titles", {c.id: c.title for c in CAREERS})
    ctx.setdefault("skill_names", {s.id: s.name for s in SKILLS})
    return templates.TemplateResponse(
        request=request, name=name, context=ctx, status_code=status_code
    )


# --------------------------------------------------------------------------
# PAGES
# --------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_home(request: Request):
    top = sorted(CAREERS, key=lambda c: (-c.demand, -c.avg_salary_usd))[:3]
    return _page("index.html", request, top_careers=[_career_detail(c) for c in top])


@app.get("/analyse", response_class=HTMLResponse, include_in_schema=False)
def page_analyse(request: Request):
    return _page("analyse.html", request)


@app.get("/careers", response_class=HTMLResponse, include_in_schema=False)
def page_careers(request: Request):
    cats: list[str] = []
    for c in CAREERS:
        if c.category not in cats:
            cats.append(c.category)
    return _page("careers.html", request, careers=_career_cards(), categories=sorted(cats))


@app.get("/careers/{career_id}", response_class=HTMLResponse, include_in_schema=False)
def page_career_detail(request: Request, career_id: str):
    career = get_career(career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Unknown career id")
    return _page("career_detail.html", request, career=_career_detail(career))


@app.get("/skills", response_class=HTMLResponse, include_in_schema=False)
def page_skills(request: Request):
    cards = _skill_cards()
    cats = sorted({c["category"] for c in cards})
    return _page("skills.html", request, skills=cards, categories=cats)


@app.get("/skills/{skill_id}", response_class=HTMLResponse, include_in_schema=False)
def page_skill_detail(request: Request, skill_id: str):
    detail = _skill_detail(skill_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Unknown skill id")
    return _page("skill_detail.html", request, skill=detail)


@app.get("/roadmap", response_class=HTMLResponse, include_in_schema=False)
def page_roadmap(request: Request):
    cards = _career_cards()
    return _page("roadmap.html", request, careers=cards)


@app.get("/projects", response_class=HTMLResponse, include_in_schema=False)
def page_projects(request: Request):
    cards = _project_cards()
    diffs = [d for d in ("beginner", "intermediate", "advanced") if any(c["difficulty"] == d for c in cards)]
    return _page("projects.html", request, projects=cards, difficulties=diffs)


@app.get("/projects/{project_id}", response_class=HTMLResponse, include_in_schema=False)
def page_project_detail(request: Request, project_id: str):
    detail = _project_detail(project_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Unknown project id")
    return _page("project_detail.html", request, project=detail)


@app.get("/resources", response_class=HTMLResponse, include_in_schema=False)
def page_resources(request: Request):
    cards = _resource_cards()
    kinds: list[str] = []
    for r in cards:
        if r["kind"] not in kinds:
            kinds.append(r["kind"])
    return _page(
        "resources.html",
        request,
        resources=cards,
        kinds=sorted(kinds),
        skill_count=len({r["skill_id"] for r in cards}),
    )


@app.get("/companies", response_class=HTMLResponse, include_in_schema=False)
def page_companies(request: Request):
    companies = []
    for c in COMPANIES:
        companies.append(
            {
                "id": c.id,
                "name": c.name,
                "industry": c.industry,
                "location": c.location,
                "size": c.size,
                "description": c.description,
                "hiring": list(c.hiring),
                "culture": list(c.culture),
                "extra_skills": [
                    {
                        "skill_id": sid,
                        "name": SKILLS_BY_ID[sid].name if sid in SKILLS_BY_ID else sid,
                        "weight": weight,
                    }
                    for sid, weight in c.extra_skills.items()
                ],
            }
        )
    return _page("companies.html", request, companies=companies, industries=all_industries())


@app.get("/companies/{company_id}", response_class=HTMLResponse, include_in_schema=False)
def page_company_detail(request: Request, company_id: str):
    company = COMPANIES_BY_ID.get(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    roles = []
    for cid in company.hiring:
        career = CAREERS_BY_ID.get(cid)
        if career is None:
            continue
        detail = _career_detail(career)
        roles.append(
            {
                "id": detail["id"],
                "title": detail["title"],
                "category": detail["category"],
                "demand": detail["demand"],
                "avg_salary_usd": detail["avg_salary_usd"],
                "readiness_hint": detail["readiness_hint"],
                "skills": detail["skills"][:6],
                "outlook": detail["outlook"],
            }
        )

    extra = [
        {
            "skill_id": sid,
            "name": SKILLS_BY_ID[sid].name if sid in SKILLS_BY_ID else sid,
            "weight": weight,
        }
        for sid, weight in company.extra_skills.items()
    ]

    return _page(
        "company_detail.html",
        request,
        company={
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "location": company.location,
            "size": company.size,
            "description": company.description,
            "culture": list(company.culture),
        },
        roles=roles,
        extra_skills=extra,
    )


@app.get("/about", response_class=HTMLResponse, include_in_schema=False)
def page_about(request: Request):
    return _page("about.html", request)


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok", "careers": len(CAREERS), "skills": len(SKILLS)}


@app.exception_handler(404)
async def not_found(request: Request, exc):
    path = request.url.path
    if path.startswith("/api"):
        return JSONResponse({"detail": "Not found"}, status_code=404)
    if path.startswith("/static"):
        # Missing asset: never answer a stylesheet/script request with HTML.
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return _page("404.html", request, status_code=404)


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------
class AnalyseRequest(BaseModel):
    resume_text: str = Field(default="", max_length=40000)
    interests_text: str = Field(default="", max_length=8000)
    manual_skills: list[str] = Field(default_factory=list)
    target_career: str | None = None
    target_company: str | None = None
    weekly_hours: int = Field(default=8, ge=1, le=40)
    horizon_weeks: int = Field(default=16, ge=4, le=52)
    top_n: int = Field(default=6, ge=1, le=12)


class RoadmapRequest(BaseModel):
    career_id: str
    weekly_hours: int = Field(default=8, ge=1, le=40)
    horizon_weeks: int = Field(default=16, ge=4, le=52)


class ReadinessRequest(BaseModel):
    career_id: str
    proficiency: dict[str, float] = Field(default_factory=dict)


class CompanyFitRequest(BaseModel):
    resume_text: str = Field(default="", max_length=40000)
    proficiency: dict[str, float] = Field(default_factory=dict)


@app.get("/api/health")
def api_health() -> dict:
    return {"status": "ok", "careers": len(CAREERS), "skills": len(SKILLS), "version": app.version}


@app.get("/api/stats")
def api_stats() -> dict:
    return _site_stats()


@app.get("/api/meta")
def api_meta() -> dict:
    return {
        "skills": [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "aliases": list(s.aliases),
                "keywords": list(s.keywords),
            }
            for s in SKILLS
        ],
        "skill_categories": sorted({s.category for s in SKILLS}),
        "careers": [
            {
                "id": c.id,
                "title": c.title,
                "category": c.category,
                "demand": c.demand,
                "avg_salary_usd": c.avg_salary_usd,
                "top_skills": sorted(c.required, key=c.required.get, reverse=True)[:6],
            }
            for c in CAREERS
        ],
        "companies": [
            {
                "id": co.id,
                "name": co.name,
                "industry": co.industry,
                "location": co.location,
                "size": co.size,
                "hiring": list(co.hiring),
            }
            for co in COMPANIES
        ],
        "model": model.model_info(),
    }


@app.get("/api/careers")
def api_careers() -> dict:
    return {"count": len(CAREERS), "careers": _career_cards()}


@app.get("/api/careers/{career_id}")
def api_career(career_id: str) -> dict:
    career = get_career(career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Unknown career id")
    detail = _career_detail(career)
    detail["required"] = [
        {"skill_id": sid, "weight": weight}
        for sid, weight in sorted(career.required.items(), key=lambda kv: -kv[1])
    ]
    detail["companies"] = [{"id": c.id, "name": c.name, "industry": c.industry} for c in detail["companies"]]
    return detail


@app.get("/api/skills")
def api_skills() -> dict:
    cards = _skill_cards()
    return {"count": len(cards), "skills": cards}


@app.get("/api/skills/{skill_id}")
def api_skill(skill_id: str) -> dict:
    detail = _skill_detail(skill_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Unknown skill id")
    return detail


@app.get("/api/projects")
def api_projects() -> dict:
    cards = _project_cards()
    return {"count": len(cards), "projects": cards}


@app.get("/api/projects/{project_id}")
def api_project(project_id: str) -> dict:
    detail = _project_detail(project_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Unknown project id")
    return detail


@app.get("/api/resources")
def api_resources() -> dict:
    cards = _resource_cards()
    return {"count": len(cards), "resources": cards}


@app.get("/api/companies")
def api_companies() -> dict:
    return {
        "count": len(COMPANIES),
        "companies": [
            {
                "id": c.id,
                "name": c.name,
                "industry": c.industry,
                "location": c.location,
                "size": c.size,
                "description": c.description,
                "culture": list(c.culture),
                "hiring": list(c.hiring),
                "extra_skills": [
                    {"skill_id": k, "weight": v} for k, v in c.extra_skills.items()
                ],
            }
            for c in COMPANIES
        ],
    }


@app.get("/api/companies/{company_id}")
def api_company(company_id: str) -> dict:
    company = get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Unknown company id")
    return {
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "location": company.location,
        "size": company.size,
        "description": company.description,
        "culture": list(company.culture),
        "hiring": [
            {"career_id": cid, "title": CAREERS_BY_ID[cid].title if cid in CAREERS_BY_ID else cid}
            for cid in company.hiring
        ],
        "extra_skills": [
            {
                "skill_id": sid,
                "name": SKILLS_BY_ID[sid].name if sid in SKILLS_BY_ID else sid,
                "weight": weight,
            }
            for sid, weight in company.extra_skills.items()
        ],
    }


@app.post("/api/companies/{company_id}/fit")
def api_company_fit(company_id: str, payload: CompanyFitRequest) -> dict:
    company = get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Unknown company id")

    prof = {k: max(0.0, min(1.0, v)) for k, v in payload.proficiency.items()}
    if payload.resume_text.strip():
        for detected in extract_skills(payload.resume_text):
            prof.setdefault(detected.skill_id, detected.proficiency)

    extra = []
    for sid, weight in company.extra_skills.items():
        current = prof.get(sid, 0.0)
        extra.append(
            {
                "skill_id": sid,
                "name": SKILLS_BY_ID[sid].name if sid in SKILLS_BY_ID else sid,
                "weight": weight,
                "current": round(current, 2),
                "covered": current >= 0.5,
            }
        )

    roles = []
    for cid in company.hiring:
        career = CAREERS_BY_ID.get(cid)
        if not career:
            continue
        ready, gaps = analyse_gap(cid, prof)
        roles.append(
            {
                "career_id": cid,
                "title": career.title,
                "readiness": ready,
                "readiness_label": readiness_label(ready),
                "top_gaps": [
                    {"skill_id": g.skill_id, "name": g.name, "missing": g.missing}
                    for g in gaps[:3]
                ],
            }
        )
    roles.sort(key=lambda r: -r["readiness"])

    extra_total = sum(e["weight"] for e in extra)
    extra_covered = sum(e["weight"] for e in extra if e["covered"])
    differentiator_score = extra_covered / extra_total if extra_total else 0.0
    best_role = roles[0]["readiness"] if roles else 0.0
    overall = round(0.75 * best_role + 0.25 * differentiator_score, 4)

    return {
        "company": {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "location": company.location,
        },
        "overall_fit": overall,
        "fit_label": readiness_label(overall),
        "differentiator_score": round(differentiator_score, 4),
        "best_role": roles[0]["title"] if roles else None,
        "extra_skills": extra,
        "roles": roles,
    }


@app.post("/api/analyse")
def api_analyse(payload: AnalyseRequest) -> dict:
    if not payload.resume_text.strip() and not payload.interests_text.strip() and not payload.manual_skills:
        raise HTTPException(
            status_code=400,
            detail="Provide resume text, interests, or at least one skill.",
        )
    return analyse(
        resume_text=payload.resume_text,
        interests_text=payload.interests_text,
        manual_skills=payload.manual_skills,
        target_career=payload.target_career,
        target_company=payload.target_company,
        weekly_hours=payload.weekly_hours,
        horizon_weeks=payload.horizon_weeks,
        top_n=payload.top_n,
    )


@app.post("/api/roadmap")
def api_roadmap(payload: RoadmapRequest) -> dict:
    career = get_career(payload.career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Unknown career id")
    proficiency = _career_proficiency(payload.career_id)
    _, gaps = analyse_gap(payload.career_id, proficiency)
    roadmap = build_roadmap(
        payload.career_id, proficiency, gaps, payload.weekly_hours, payload.horizon_weeks
    )
    return {
        "career": {
            "id": career.id,
            "title": career.title,
            "category": career.category,
            "description": career.description,
        },
        "assumed_from": "zero (no existing skills)",
        "roadmap": roadmap,
        "projects": recommend_projects(payload.career_id, gaps, proficiency),
    }


@app.post("/api/readiness")
def api_readiness(payload: ReadinessRequest) -> dict:
    career = get_career(payload.career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Unknown career id")
    clean = {k: max(0.0, min(1.0, v)) for k, v in payload.proficiency.items()}
    ready, gaps = analyse_gap(payload.career_id, clean)
    return {
        "career_id": career.id,
        "career_title": career.title,
        "readiness": round(ready, 4),
        "gaps": [
            {
                "skill_id": g.skill_id,
                "name": g.name,
                "importance": g.importance,
                "current": g.current,
                "target": g.target,
                "missing": g.missing,
                "priority": g.priority,
                "rationale": g.rationale,
            }
            for g in gaps
        ],
    }
