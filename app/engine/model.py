"""Model layer: turns the knowledge base into an actual ML model.

Three complementary signals are produced here:

1. `content_scores` - TF-IDF cosine similarity between the student's detected
   skill text and each career's document. This is what lets the system
   recommend a career the student never named explicitly.
2. `readiness` - weighted coverage of a career's required skills, using each
   skill's importance weight as the cost of being missing.
3. `latent_similarity` - TruncatedSVD of the skill-by-career matrix, used both
   for career-to-career similarity and to suggest adjacent skills that are
   predictive of skills the student already has (a collaborative-filtering
   style signal over the knowledge base).

Artifacts are built once at import time; the corpus is small enough that this is
milliseconds.
"""

from __future__ import annotations

import functools

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.careers import CAREERS
from app.data.skills import SKILLS_BY_ID, skill_name

CAREER_IDS: tuple[str, ...] = tuple(c.id for c in CAREERS)
CAREER_INDEX: dict[str, int] = {cid: i for i, cid in enumerate(CAREER_IDS)}

# Blend weights for the final match score.
W_CONTENT = 0.42
W_READINESS = 0.46
W_MARKET = 0.12

SVD_COMPONENTS = 12


def skill_target(weight: float) -> float:
    """Effective mastery bar for a weighted skill.

    Nice-to-have skills (weight < 0.6) need less than full proficiency to be
    considered covered. Kept in one place so readiness, gaps and the per-skill
    breakdown all reconcile to the same number.
    """
    return weight if weight >= 0.6 else weight * 0.7


def career_document(career_id: str) -> str:
    career = next(c for c in CAREERS if c.id == career_id)
    parts: list[str] = [career.title, career.category, career.description]
    parts.extend(career.responsibilities)
    parts.extend(career.work_styles)
    parts.extend(skill_name(s) for s in career.required)
    parts.extend(career.outlook.split())
    return " ".join(parts)


def profile_document(skill_ids: list[str], weights: dict[str, float] | None = None) -> str:
    """Render the student's profile as text for the TF-IDF space.

    A skill is repeated proportional to its proficiency so that TF-IDF term
    frequency reflects how strong the signal is, not just its presence.
    """
    weights = weights or {}
    tokens: list[str] = []
    for skill_id in skill_ids:
        skill = SKILLS_BY_ID.get(skill_id)
        if not skill:
            continue
        weight = weights.get(skill_id, 0.5)
        repeats = 1 + int(round(weight * 3))
        for _ in range(max(repeats, 1)):
            tokens.extend(skill.name.lower().split())
            tokens.extend(kw for kw in skill.keywords)
    return " ".join(tokens)


@functools.lru_cache(maxsize=1)
def _career_tfidf() -> tuple[TfidfVectorizer, np.ndarray]:
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1,
        stop_words="english",
    )
    matrix = vectorizer.fit_transform([career_document(cid) for cid in CAREER_IDS])
    return vectorizer, matrix


@functools.lru_cache(maxsize=1)
def _skill_matrix() -> tuple[tuple[str, ...], np.ndarray]:
    """Binary skill-by-carery requirement matrix, weighted by importance."""
    skill_ids = tuple(SKILLS_BY_ID.keys())
    index = {sid: i for i, sid in enumerate(skill_ids)}
    matrix = np.zeros((len(skill_ids), len(CAREER_IDS)), dtype=float)
    for career in CAREERS:
        col = CAREER_INDEX[career.id]
        for skill_id, weight in career.required.items():
            row = index.get(skill_id)
            if row is not None:
                matrix[row, col] = weight
    return skill_ids, matrix


@functools.lru_cache(maxsize=1)
def _svd() -> tuple[TruncatedSVD, np.ndarray, np.ndarray]:
    """Latent factors over careers and over skills."""
    _, skill_matrix = _skill_matrix()
    career_components = min(SVD_COMPONENTS, min(skill_matrix.shape) - 1)
    svd = TruncatedSVD(n_components=career_components, random_state=42)
    skill_factors = svd.fit_transform(skill_matrix)
    career_factors = svd.components_.T
    return svd, skill_factors, career_factors


def career_similarity() -> np.ndarray:
    """Career-to-career cosine similarity from the latent career factors."""
    _, _, career_factors = _svd()
    return cosine_similarity(career_factors)


def content_scores(profile_text: str) -> np.ndarray:
    """TF-IDF cosine similarity of the profile against every career."""
    if not profile_text.strip():
        return np.zeros(len(CAREER_IDS))
    vectorizer, matrix = _career_tfidf()
    profile_vector = vectorizer.transform([profile_text])
    return cosine_similarity(profile_vector, matrix)[0]


def market_prior() -> np.ndarray:
    """Demand-driven prior, normalised to 0..1 across the catalogue."""
    demand = np.array([c.demand for c in CAREERS], dtype=float)
    return (demand - 1.0) / 4.0


def readiness(career_id: str, proficiency: dict[str, float]) -> tuple[float, list[tuple[str, float, float]]]:
    """Weighted skill coverage for a career.

    Returns the readiness score in 0..1 and the per-skill breakdown as
    (skill_id, required_weight, student_proficiency) sorted by importance.
    """
    career = next(c for c in CAREERS if c.id == career_id)
    if not career.required:
        return 0.0, []

    total_weight = sum(career.required.values())
    achieved = 0.0
    detail: list[tuple[str, float, float]] = []
    for skill_id, weight in career.required.items():
        have = max(0.0, min(1.0, proficiency.get(skill_id, 0.0)))
        achieved += weight * have
        detail.append((skill_id, weight, have))
    detail.sort(key=lambda row: (-row[1], -row[2]))
    return achieved / total_weight, detail


def adjacent_skills(owned: list[str], limit: int = 8) -> list[dict]:
    """Skills that co-occur with what the student already has.

    Implemented as a nearest-neighbour lookup in the latent skill space, which
    is the collaborative-filtering analogue for a knowledge base.
    """
    skill_ids, _ = _skill_matrix()
    index = {sid: i for i, sid in enumerate(skill_ids)}
    owned_rows = [index[s] for s in owned if s in index]
    if not owned_rows:
        return []

    _, skill_factors, career_factors = _svd()
    owned_vec = skill_factors[owned_rows].mean(axis=0)
    if np.linalg.norm(owned_vec) == 0:
        return []

    sims = cosine_similarity(owned_vec.reshape(1, -1), career_factors)[0]
    sims = np.maximum(sims, 0.0)
    owned_set = set(owned)

    results: list[dict] = []
    order = np.argsort(sims)[::-1]
    for col in order:
        career_id = CAREER_IDS[int(col)]
        career = next(c for c in CAREERS if c.id == career_id)
        for skill_id, weight in career.required.items():
            if skill_id in owned_set or weight < 0.5:
                continue
            results.append(
                {
                    "skill_id": skill_id,
                    "name": skill_name(skill_id),
                    "affinity": round(float(sims[col]) * weight, 4),
                    "careers": [career_id],
                }
            )

    merged: dict[str, dict] = {}
    for row in results:
        entry = merged.setdefault(
            row["skill_id"],
            {"skill_id": row["skill_id"], "name": row["name"], "affinity": 0.0, "careers": []},
        )
        entry["affinity"] = max(entry["affinity"], row["affinity"])
        if row["careers"][0] not in entry["careers"]:
            entry["careers"].append(row["careers"][0])
            entry["careers"] = entry["careers"][:3]

    ranked = sorted(merged.values(), key=lambda r: -r["affinity"])[:limit]
    for row in ranked:
        row["affinity"] = round(row["affinity"], 3)
    return ranked


def final_score(
    content: float,
    ready: float,
    market: float,
    target_boost: float = 0.0,
    company_boost: float = 0.0,
) -> float:
    """Blend the three signals into a single 0..1 match score."""
    base = W_CONTENT * content + W_READINESS * ready + W_MARKET * market
    boosted = base + target_boost + company_boost
    return float(max(0.0, min(1.0, boosted)))


def blend_weights() -> dict[str, float]:
    return {
        "content_similarity": W_CONTENT,
        "skill_readiness": W_READINESS,
        "market_demand": W_MARKET,
    }


def model_info() -> dict:
    vectorizer, matrix = _career_tfidf()
    svd, skill_factors, career_factors = _svd()
    return {
        "careers": len(CAREER_IDS),
        "skills": len(SKILLS_BY_ID),
        "tfidf_features": len(vectorizer.vocabulary_),
        "tfidf_matrix_shape": list(matrix.shape),
        "latent_components": int(svd.n_components),
        "explained_variance": round(float(svd.explained_variance_ratio_.sum()), 4),
        "latent_shapes": [list(skill_factors.shape), list(career_factors.shape)],
        "weights": blend_weights(),
    }