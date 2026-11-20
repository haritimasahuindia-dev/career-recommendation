"""Regression suite. Run with:  .venv\\Scripts\\python -m tests.test_regression

Covers the things that silently broke before:
  * every skill name and alias still detected
  * overlapping alias/name matches are not double counted
  * proficiency stays inside the documented 0..0.95 range
  * roadmap phase weeks always sum to the requested horizon
  * the full page + API surface answers 200
"""

import json
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.careers import CAREERS  # noqa: E402
from app.data.companies import COMPANIES  # noqa: E402
from app.data.skills import SKILLS, SKILLS_BY_ID  # noqa: E402
from app.engine.parser import extract_skills  # noqa: E402
from app.engine.roadmap import analyse_gap, build_roadmap  # noqa: E402

BASE_URL = "http://127.0.0.1:8000"


def get(path):
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def post(path, payload):
    req = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8", "replace") or "{}")

BASE = "SKILLS: "


def skills_in(text):
    return {s.skill_id: s for s in extract_skills(text)}


class SkillDetection(unittest.TestCase):
    def test_every_name_and_alias_detected(self):
        bad = []
        for skill in SKILLS:
            surfaces = {skill.name.lower(), skill.id.lower().replace("_", " ")}
            surfaces |= {k.lower() for k in skill.keywords}
            surfaces |= {a.lower() for a in skill.aliases}
            for surface in surfaces:
                surface = surface.strip()
                if len(surface) < 2:
                    continue
                if skill.id not in skills_in(BASE + surface):
                    bad.append((skill.id, surface))
        self.assertEqual(bad, [], f"undetected surfaces: {bad[:20]}")

    def test_name_and_alias_do_not_double_count(self):
        # "Node.js" is both the name and (via alias "node") a prefix match.
        got = skills_in(BASE + "Node.js")["nodejs"].mentions
        self.assertEqual(got, 1, "a single written mention must count once")

    def test_dotted_suffix_is_not_a_skill(self):
        # the "js" inside "next.js" is part of that token, not JavaScript
        self.assertNotIn("javascript", skills_in(BASE + "Next.js"))

    def test_genuine_repeats_still_count(self):
        self.assertEqual(skills_in(BASE + "python python")["python"].mentions, 2)
        self.assertEqual(
            skills_in(BASE + "node.js and node.js")["nodejs"].mentions, 2
        )

    def test_proficiency_stays_in_documented_range(self):
        text = "INTERNSHIP: " + " ".join(["Python React SQL"] * 12)
        for skill in extract_skills(text):
            self.assertGreaterEqual(skill.proficiency, 0.0)
            self.assertLessEqual(skill.proficiency, 0.95)

    def test_documented_base_scores(self):
        expected = {
            "INTERNSHIP: built a billing service with Python": 0.87,
            "PROJECTS: built a recipe app with Java": 0.77,
            "ACHIEVEMENTS: cut cloud spend with Docker": 0.68,
            "SKILLS: Python": 0.55,
            "EDUCATION: coursework in statistics": 0.45,
        }
        skill_id = {
            "INTERNSHIP: built a billing service with Python": "python",
            "PROJECTS: built a recipe app with Java": "java",
            "ACHIEVEMENTS: cut cloud spend with Docker": "docker",
            "SKILLS: Python": "python",
            "EDUCATION: coursework in statistics": "statistics",
        }
        for text, want in expected.items():
            got = skills_in(text)[skill_id[text]].proficiency
            self.assertAlmostEqual(got, want, places=2, msg=text)

    def test_empty_and_odd_input_is_safe(self):
        for text in ["", "   ", "\n\t", "?", "-", "0" * 5000]:
            self.assertIsInstance(extract_skills(text), list)


class Roadmap(unittest.TestCase):
    def test_phase_weeks_sum_to_horizon(self):
        for career in CAREERS:
            _, gaps = analyse_gap(career.id, {})
            for horizon in (4, 8, 16, 26, 52):
                phases = build_roadmap(career.id, {}, gaps, 8, horizon)["phases"]
                total = sum(p["weeks"] for p in phases)
                self.assertEqual(
                    total, horizon, f"{career.id} @ {horizon}w summed to {total}"
                )

    def test_phase_weeks_sum_with_partial_skills(self):
        _, gaps = analyse_gap("frontend-developer", {"html": 0.9, "css": 0.7, "javascript": 0.4})
        for horizon in (4, 12, 30):
            phases = build_roadmap(
                "frontend-developer", {}, gaps, 12, horizon
            )["phases"]
            self.assertEqual(sum(p["weeks"] for p in phases), horizon)

    def test_every_referenced_skill_exists(self):
        for career in CAREERS:
            for sid in career.required:
                self.assertIn(sid, SKILLS_BY_ID, f"{career.id} -> {sid}")
        for company in COMPANIES:
            for sid in company.extra_skills:
                self.assertIn(sid, SKILLS_BY_ID, f"{company.id} -> {sid}")


class Routes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        status, _ = get("/healthz")
        if status != 200:
            raise unittest.SkipTest(
                f"server not running on {BASE_URL} - start it first"
            )

    def test_pages(self):
        paths = ["/", "/analyse", "/careers", "/skills", "/roadmap",
                 "/projects", "/resources", "/companies", "/about", "/healthz"]
        paths += [f"/careers/{c.id}" for c in CAREERS]
        paths += [f"/companies/{c.id}" for c in COMPANIES]
        for p in paths:
            with self.subTest(path=p):
                self.assertEqual(get(p)[0], 200)

    def test_apis(self):
        for p in ["/api/meta", "/api/stats", "/api/careers", "/api/skills",
                  "/api/projects", "/api/resources", "/api/companies"]:
            with self.subTest(path=p):
                self.assertEqual(get(p)[0], 200)

    def test_unknown_page_is_404(self):
        for p in ["/nope", "/careers/nope", "/companies/nope", "/static/nope.css"]:
            with self.subTest(path=p):
                self.assertEqual(get(p)[0], 404)

    def test_no_salary_in_rendered_html(self):
        # A bare "$" is legitimate (the JS uses $("id")), so only look for
        # compensation shapes: the field name and currency amounts.
        banned = ["avg_salary", "avg_salary_usd", "salary band", "$88", "$120"]
        for p in ["/", "/careers", "/companies", "/roadmap", "/about",
                  "/careers/frontend-developer", "/companies/flipkart"]:
            body = get(p)[1]
            for needle in banned:
                self.assertNotIn(needle, body, f"{p} contains {needle!r}")

    def test_no_mojibake_in_rendered_html(self):
        for p in ["/", "/careers", "/skills", "/careers/frontend-developer"]:
            body = get(p)[1]
            for bad in ("\ufffd", "\u00e2\u2020", "\u00c2"):
                self.assertNotIn(bad, body, f"{p} contains {bad!r}")

    def test_roadmap_post(self):
        for horizon in (4, 16, 52):
            status, data = post("/api/roadmap", {
                "career_id": "frontend-developer",
                "weekly_hours": 8,
                "horizon_weeks": horizon,
            })
            self.assertEqual(status, 200)
            self.assertEqual(
                sum(p["weeks"] for p in data["roadmap"]["phases"]), horizon
            )

    def test_analyse_rejects_bad_target_gracefully(self):
        status, data = post("/api/analyse", {
            "resume_text": "SKILLS Python SQL React",
            "target_career": "does-not-exist",
            "target_company": "does-not-exist",
        })
        self.assertEqual(status, 200)
        self.assertGreater(len(data["matches"]), 0)

    def test_validation_bounds(self):
        for payload in (
            {"career_id": "frontend-developer", "weekly_hours": 0},
            {"career_id": "frontend-developer", "weekly_hours": 41},
            {"career_id": "frontend-developer", "horizon_weeks": 3},
            {"career_id": "frontend-developer", "horizon_weeks": 53},
        ):
            with self.subTest(payload=payload):
                self.assertEqual(post("/api/roadmap", payload)[0], 422)


if __name__ == "__main__":
    unittest.main(verbosity=2)
