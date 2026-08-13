"""
Renders templates/*.html with the loaded content and writes static/.

Registers two Jinja globals the templates rely on:
  - url_for('index' | 'project', project=...)  -> site-relative URL
  - asset_url(path)                              -> site-relative asset URL

Both are deliberately simple path builders, not a real routing system —
this is a static site, there's no server deciding URLs at request time.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .loader import group_by_category, load_projects
from .models import Project


def _url_for(name: str, project: Project | None = None) -> str:
    if name == "project":
        if project is None:
            raise ValueError("url_for('project', ...) requires a project argument")
        return f"/{project.slug}/"
    return "/"


def _asset_url(path: str) -> str:
    return f"/assets/{path.lstrip('/')}"


def build(
    *,
    content_dir: str | Path,
    templates_dir: str | Path,
    assets_dir: str | Path,
    output_dir: str | Path,
    site: dict[str, Any],
    home: dict[str, Any],
    work: dict[str, Any],
    intersection: dict[str, Any],
    about: dict[str, Any],
) -> list[Project]:
    output_dir = Path(output_dir)
    assets_dir = Path(assets_dir)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    if assets_dir.exists():
        shutil.copytree(assets_dir, output_dir / "assets")

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["url_for"] = _url_for
    env.globals["asset_url"] = _asset_url

    projects = load_projects(content_dir)
    categories = group_by_category(projects)

    index_html = env.get_template("index.html").render(
        site=site,
        home=home,
        work=work,
        categories=categories,
        intersection=intersection,
        about=about,
    )
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")

    project_template = env.get_template("project.html")
    for project in projects:
        project_dir = output_dir / project.slug
        project_dir.mkdir(parents=True, exist_ok=True)
        html = project_template.render(site=site, project=project)
        (project_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"Built {len(projects)} project(s) across {len(categories)} categor{'y' if len(categories) == 1 else 'ies'} -> {output_dir}")
    return projects
