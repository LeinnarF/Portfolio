"""
Walks content/<type>/*.md, parses each file, and normalizes the result
into Project objects.

Layout expected:

    content/
      data/
        app-rating-prediction.md
        sugar-price-forecasting.md
      uiux/
        internship-project.md

The folder name under content/ becomes Project.type, which is what the
templates group by (see categories in main.py / builder.py). Adding a
new category later is just a new folder — no code change needed here.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from .models import Project
from .parser import ParseError, parse_markdown_file


def load_projects(content_dir: str | Path) -> list[Project]:
    content_dir = Path(content_dir)
    projects: list[Project] = []

    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory not found: {content_dir}")

    for type_dir in sorted(p for p in content_dir.iterdir() if p.is_dir()):
        project_type = type_dir.name

        for md_file in sorted(type_dir.glob("*.md")):
            try:
                metadata, html = parse_markdown_file(md_file)
            except ParseError as exc:
                print(f"[loader] skipping {md_file}: {exc}")
                continue

            metadata.setdefault("slug", md_file.stem)
            metadata["type"] = project_type
            metadata["content"] = html

            try:
                project = Project(**metadata)
            except ValidationError as exc:
                print(f"[loader] skipping {md_file}, invalid front matter:\n{exc}")
                continue

            if project.draft:
                continue

            projects.append(project)

    # featured first, then explicit order, then title — stable and predictable
    projects.sort(key=lambda p: (not p.featured, p.order, p.title.lower()))
    return projects


def group_by_category(projects: list[Project]) -> list[dict]:
    """
    Turn a flat project list into the `categories` structure index.html
    expects, preserving the order categories first appear in.
    """
    from .models import CATEGORY_LABELS

    order: list[str] = []
    for p in projects:
        if p.type not in order:
            order.append(p.type)

    return [
        {
            "id": category_type,
            "label": CATEGORY_LABELS.get(category_type, category_type.upper()),
            "projects": [p for p in projects if p.type == category_type],
        }
        for category_type in order
    ]
