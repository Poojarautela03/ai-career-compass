"""
career_weights.py

Rule-based career-track matching engine for AI Career Compass.
"""
import streamlit as st
from google import genai

SKILL_FIELDS = [
    "dsa", "python", "java_node", "html_css_js", "react", "sql",
    "excel_powerbi", "ml", "dl", "cloud", "devops", "security",
    "mobile", "communication", "projects", "internships",
]

TRACK_WEIGHTS = {
    "AI Engineer": {"python": 3, "ml": 3, "dl": 2, "sql": 2, "dsa": 1},
    "Data Scientist": {"python": 3, "ml": 3, "sql": 2, "excel_powerbi": 1, "dsa": 1},
    "Data Analyst": {"excel_powerbi": 3, "sql": 3, "python": 2},
    "Machine Learning Engineer": {"python": 3, "ml": 3, "dl": 2, "devops": 2, "cloud": 1, "dsa": 1},
    "Backend Developer": {"java_node": 3, "python": 2, "sql": 2, "dsa": 2},
    "Frontend Developer": {"html_css_js": 3, "react": 3, "dsa": 1},
    "Full Stack Developer": {"html_css_js": 2, "react": 2, "java_node": 2, "sql": 1, "dsa": 1},
    "Cloud Engineer": {"cloud": 3, "devops": 2, "security": 2, "dsa": 1},
    "DevOps Engineer": {"devops": 3, "cloud": 2, "security": 1, "dsa": 1},
    "Cybersecurity Analyst": {"security": 3, "cloud": 1, "dsa": 1},
    "Software Engineer": {"dsa": 3, "python": 1, "java_node": 1, "sql": 1},
    "Mobile App Developer": {"mobile": 3, "dsa": 1, "java_node": 1},
}

UNIVERSAL_WEIGHTS = {"communication": 0.5, "projects": 0.3, "internships": 0.5}
UNIVERSAL_CAP = 1.5


def score_tracks(profile: dict) -> dict:
    results = {}
    for track, weights in TRACK_WEIGHTS.items():
        max_possible = sum(w * 10 for w in weights.values())
        earned = sum(profile.get(field, 0) * w for field, w in weights.items())
        comm_bonus = profile.get("communication", 0) * UNIVERSAL_WEIGHTS["communication"]
        proj_bonus = min(profile.get("projects", 0) * UNIVERSAL_WEIGHTS["projects"], UNIVERSAL_CAP)
        intern_bonus = min(profile.get("internships", 0) * UNIVERSAL_WEIGHTS["internships"], UNIVERSAL_CAP)
        bonus = comm_bonus + proj_bonus + intern_bonus
        bonus_ceiling = 10 * UNIVERSAL_WEIGHTS["communication"] + 2 * UNIVERSAL_CAP
        match_pct = min(100, round(100 * (earned + bonus) / (max_possible + bonus_ceiling), 1))
        results[track] = match_pct
    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))


def get_skill_gaps(track: str, profile: dict, threshold: int = 5) -> dict:
    weights = TRACK_WEIGHTS[track]
    has, needs = [], []
    for skill, weight in weights.items():
        if weight >= 2:
            user_value = profile.get(skill, 0)
            (has if user_value >= threshold else needs).append(skill)
    return {"has": has, "needs": needs}


@st.cache_data(show_spinner="Generating your personalized roadmap...")
def build_roadmap_ai(track: str, needs: list) -> str:
    if not needs:
        return "You're already strong across every core skill for this track!"
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    prompt = f"""You are a career mentor. A student wants to become a {track}.
They are missing these skills: {", ".join(needs)}.
Write a concise month-by-month learning roadmap (one month per missing skill,
in the order given). For each month, give: the skill focus, 2-3 specific
topics to learn, and one small project idea. Keep it practical and under
250 words total."""
    response = client.models.generate_content(model="gemini-flash-latest", contents=prompt)
    return response.text