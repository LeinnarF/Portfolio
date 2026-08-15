"""
Usage:
    python main.py build

Site-wide copy (hero text, about section, footer links) is defined here
as plain dicts rather than Markdown files, since it isn't per-project
content that a loader needs to discover — it's the fixed shell around it.
Edit the dicts below to change the homepage copy.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.builder import build

ROOT = Path(__file__).parent

SITE = {
    "name": "Franniel Hilario",
    "logo": "FRANNIEL.",
    "tagline": "Data & UX",
    "description": (
        "Mathematics graduate specializing in Computer Science, working "
        "across data analysis, machine learning, and UI/UX design."
    ),
    "resume_url": "/resume.pdf",
    "footer_links": [
        {"label": "GitHub", "url": "https://github.com/LeinnarF"},
        {"label": "LinkedIn", "url": "https://linkedin.com/in/leinnarf"},
        {"label": "Email", "url": "mailto:hilariofranniel@gmail.com"},
    ],
}

HOME = {
    "eyebrow": "MATHEMATICS • DATA • UX",
    "headline": "Turning data into useful experiences.",
    "description": (
        "Mathematics graduate specializing in Computer Science, with "
        "experience in data analysis, machine learning, and UI/UX design."
    ),
    "actions": [
        {"label": "View Data Work", "url": "#data", "style": "primary"},
        {"label": "View UI/UX Work", "url": "#uiux", "style": "secondary"},
    ],
    "visual_top": "DATA → UX",
    "visual_bottom": "insight → experience",
}

WORK = {
    "eyebrow": "SELECTED WORK",
    "title": "Things I've built.",
    "description": "A combination of analytical projects and user-centered design work.",
}

INTERSECTION = {
    "eyebrow": "THE INTERSECTION",
    "lines": [
        {"text": "Data gives us", "highlight": "insight."},
        {"text": "Design turns it into", "highlight": "action."},
    ],
    "description": (
        "I'm interested in the space between quantitative analysis and "
        "human-centered design — using data to understand problems and "
        "design to make those insights useful."
    ),
}

ABOUT = {
    "eyebrow": "ABOUT",
    "title": "A little about me.",
    "paragraphs": [
        "I'm a Mathematics graduate specializing in Computer Science, "
        "interested in data, technology, and human-centered design.",
        "My work spans data analysis, machine learning, visualization, "
        "UI/UX design, and software development.",
    ],
    "skills": [
        {"name": "Data", "skills_list": ["Python", "SQL", "Pandas", "NumPy", "Scikit-learn", "Visualization"]},
        {"name": "UX / UI", "skills_list": ["User Research", "Wireframing", "UI Design", "Prototyping"]},
        {"name": "Development", "skills_list": ["HTML", "CSS", "C/C++", "Python", "Git", "Linux"]},
        {"name": "Tools", "skills_list": ["Figma", "Jupyter", "VS Code", "GitHub", "Streamlit", "Power BI"]},
    ],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the portfolio static site.")
    parser.add_argument("command", choices=["build"], help="Command to run")
    args = parser.parse_args()

    if args.command == "build":
        build(
            content_dir=ROOT / "content",
            templates_dir=ROOT / "templates",
            assets_dir=ROOT / "assets",
            output_dir=ROOT / "static",
            site=SITE,
            home=HOME,
            work=WORK,
            intersection=INTERSECTION,
            about=ABOUT,
        )


if __name__ == "__main__":
    main()
