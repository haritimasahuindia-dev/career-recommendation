"""Resume / profile text parsing.

Turns free-form student text into detected skills with evidence. Detection is
deliberately transparent: every extracted skill carries the literal match that
produced it plus a section-aware proficiency estimate, so the recommendation
explained to the student can always be traced back to their own input.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.data.skills import SKILLS, SKILLS_BY_ID


@dataclass
class DetectedSkill:
    skill_id: str
    name: str
    category: str
    proficiency: float  # 0..1
    mentions: int
    evidence: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    manual: bool = False


# Strong signals bump the proficiency estimate. Ordered highest first.
_SECTION_SIGNALS: dict[str, float] = {
    "projects": 0.72,
    "experience": 0.82,
    "internship": 0.82,
    "certifications": 0.6,
    "skills": 0.55,
    "achievements": 0.68,
    "education": 0.45,
}

_SECTION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("internship", r"\b(intern(ship)?|traineeship|apprentice)\b"),
    ("experience", r"\b(experience|employment|work history|professional)\b"),
    ("projects", r"\b(projects?|portfolio|personal work|github)\b"),
    ("skills", r"\b(skills?|technolog(y|ies)|technical skills|toolkit|competencies)\b"),
    ("certifications", r"\b(certif\w*|courses?|training|licen[sc]e)\b"),
    ("achievements", r"\b(achievements?|awards?|accomplishments?|honou?rs?)\b"),
    ("education", r"\b(education|academic|university|college|school|degree|b\.?tech|b\.?sc|m\.?tech|bca|mca)\b"),
)

_KEYWORD_BUMP = 0.08
_MAX_PROFICIENCY = 0.95


def _normalise(text: str) -> str:
    text = text.lower()
    text = text.replace("’", "'").replace("`", "'")
    text = re.sub(r"[^a-z0-9+#./\s-]", " ", text)
    return re.sub(r"\s+", " ", text)


def _section_label(line: str) -> tuple[str, str] | None:
    """If a line starts with a section heading, return (name, remainder).

    The remainder matters: real resumes put the skill list on the same line as
    the heading ("SKILLS Python, SQL"). Discarding the whole line would throw
    away the only evidence the parser has.
    """
    lowered = line.strip().lower()
    for name, pattern in _SECTION_PATTERNS:
        m = re.match(pattern, lowered)
        if m:
            remainder = line.strip()[m.end() :].lstrip(" :,-—–")
            return name, remainder
    return None


def _split_sections(text: str) -> dict[str, str]:
    """Split resume text into labelled sections (best effort)."""
    sections: dict[str, list[str]] = {}
    current = "general"
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        found = _section_label(stripped)
        if found:
            current, remainder = found
            if remainder:
                sections.setdefault(current, []).append(remainder)
            else:
                sections.setdefault(current, [])
            continue

        sections.setdefault(current, []).append(stripped)
    return {k: "\n".join(v) for k, v in sections.items()}


def _evidence_context(text: str, match: str, span: int = 46) -> str:
    idx = text.find(match)
    if idx == -1:
        return match
    start = max(0, idx - span // 2)
    end = min(len(text), idx + len(match) + span)
    snippet = text[start:end].strip()
    snippet = re.sub(r"\s+", " ", snippet)
    return snippet


def _escape(pattern: str) -> str:
    return re.escape(pattern.strip())


def _surface_pattern(surface: str) -> str:
    """Match `surface` as a standalone token.

    The leading guard also rejects `.` and `-` so a short alias cannot match
    inside a longer dotted or hyphenated name: the "js" in "next.js" or the
    "node" in "node.js" are part of those tokens, not standalone mentions.
    """
    return r"(?<![a-z0-9.\-])" + _escape(surface) + r"(?![a-z0-9])"


def _claim_matches(text: str, patterns: list[str]) -> list[re.Match]:
    """Find matches for `patterns` (longest first) keeping only non-overlapping ones.

    Without this, one written mention can be counted twice because a skill's
    name and a shorter alias both match it ("Node.js" matches the name
    "node.js" and also the alias "node"). Overlapping matches are dropped so
    every occurrence is counted exactly once.
    """
    claimed = bytearray(len(text) + 1)
    kept: list[re.Match] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            start, end = match.span()
            if start == end:
                continue
            if any(claimed[start:end]):
                continue
            claimed[start:end] = b"\x01" * (end - start)
            kept.append(match)
    return kept


def extract_skills(raw_text: str, manual: list[str] | None = None) -> list[DetectedSkill]:
    """Detect canonical skills in `raw_text` and merge any manual selections."""
    text = _normalise(raw_text)
    original = re.sub(r"[ \t]+", " ", raw_text)
    sections = _split_sections(raw_text)

    # skill_id -> (best proficiency, mentions, evidence, sections seen)
    found: dict[str, tuple[float, int, list[str], set[str]]] = {}

    for skill in SKILLS:
        # Dedupe surfaces. "React" appears as a keyword, as the display name and
        # as the id, and matching the same span three times would invent three
        # mentions out of one line.
        raw_surfaces: list[str] = []
        raw_surfaces.extend(skill.keywords)
        raw_surfaces.append(skill.name.lower())
        raw_surfaces.extend(a.lower() for a in skill.aliases)
        raw_surfaces.append(skill.id.lower().replace("_", " "))

        seen_surfaces: set[str] = set()
        surfaces: list[str] = []
        for surface in raw_surfaces:
            surface = surface.strip()
            if len(surface) < 2 or surface in seen_surfaces:
                continue
            seen_surfaces.add(surface)
            surfaces.append(surface)

        # Longest first so "git & version control" wins over the bare "git".
        surfaces.sort(key=len, reverse=True)

        best = 0.0
        evidence: list[str] = []
        seen_sections: set[str] = set()

        # Distinct mention positions across the whole normalised document, so a
        # skill repeated in three sections is mentioned three times, not nine.
        mention_spans: set[tuple[int, int]] = set()
        section_best: dict[str, float] = {}
        section_spans: dict[str, set[tuple[int, int]]] = {}

        norm_sections = {name: _normalise(body) for name, body in sections.items()}

        patterns = [_surface_pattern(s) for s in surfaces]

        for match in _claim_matches(text, patterns):
            mention_spans.add(match.span())
            if len(evidence) < 3:
                snippet = _evidence_context(text, match.group(0))
                if snippet not in evidence:
                    evidence.append(snippet)

        for section_name, norm_section in norm_sections.items():
            spans = section_spans.setdefault(section_name, set())
            for match in _claim_matches(norm_section, patterns):
                spans.add(match.span())

        for section_name, spans in section_spans.items():
            if not spans:
                continue
            seen_sections.add(section_name)
            base = _SECTION_SIGNALS.get(section_name, 0.5)
            if section_name in ("experience", "internship", "projects"):
                base += 0.05
            section_best[section_name] = min(base, _MAX_PROFICIENCY)

        if mention_spans:
            # Strongest evidence sets the floor; repetition only nudges it up.
            base = max(section_best.values(), default=0.5)
            repeats = max(0, len(mention_spans) - 1)
            score = base + min(repeats, 3) * _KEYWORD_BUMP
            best = max(0.0, min(score, _MAX_PROFICIENCY))
            mentions = len(mention_spans)
            found[skill.id] = (best, mentions, evidence, seen_sections)

    results: list[DetectedSkill] = []
    for skill_id, (prof, mentions, evidence, seen) in found.items():
        skill = SKILLS_BY_ID[skill_id]
        results.append(
            DetectedSkill(
                skill_id=skill.id,
                name=skill.name,
                category=skill.category,
                proficiency=round(prof, 2),
                mentions=mentions,
                evidence=evidence,
                sections=sorted(seen),
                manual=False,
            )
        )

    existing = {r.skill_id for r in results}
    for skill_id in manual or []:
        skill = SKILLS_BY_ID.get(skill_id)
        if not skill or skill_id in existing:
            continue
        results.append(
            DetectedSkill(
                skill_id=skill.id,
                name=skill.name,
                category=skill.category,
                proficiency=0.6,
                mentions=0,
                evidence=[],
                sections=["self-reported"],
                manual=True,
            )
        )
        existing.add(skill_id)

    results.sort(key=lambda r: (-r.proficiency, -r.mentions, r.name))
    return results


def normalise_interests(raw: str) -> list[str]:
    """Pull free-text interests into canonical skill ids via alias matching."""
    text = _normalise(raw)
    if not text.strip():
        return []
    hits: list[str] = []
    for skill in SKILLS:
        surfaces = list(skill.keywords) + [skill.name.lower()] + [a.lower() for a in skill.aliases]
        for surface in surfaces:
            if not surface or len(surface) < 3:
                continue
            if re.search(r"(?<![a-z0-9])" + _escape(surface) + r"(?![a-z0-9])", text):
                if skill.id not in hits:
                    hits.append(skill.id)
                break
    return hits


def profile_strength(text: str, detected: list[DetectedSkill]) -> float:
    """How much signal the engine has: based on input length and skill breadth."""
    length_signal = min(len(text.strip()) / 1200.0, 1.0)
    breadth_signal = min(len(detected) / 10.0, 1.0)
    return round(0.55 * length_signal + 0.45 * breadth_signal, 2)