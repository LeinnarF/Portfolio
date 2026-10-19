"""
Renders templates/*.html with the loaded content and writes static/.

Registers two Jinja globals the templates rely on:
  - url_for('index' | 'project', project=...)  -> site-relative URL with base_url
  - asset_url(path)                              -> site-relative asset URL with base_url
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .images import sync_assets
from .loader import (
    build_project_models,
    collect_content_and_images,
    group_by_category,
    load_site_config,
)
from .models import Project
from .utils import asset_url as _asset_url
from .utils import url_for as _url_for


def _write_if_changed(path: Path, content: str) -> bool:
    """Write text file only if content has changed or file doesn't exist."""
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == content:
                return False
        except OSError:
            pass
    path.write_text(content, encoding="utf-8")
    return True


def _generate_sitemap_xml(
    projects: list[Project],
    site: dict[str, Any],
    base_url: str = "",
) -> str:
    """Generate XML sitemap for search engines."""
    domain = site.get("url", "").rstrip("/")
    today = datetime.date.today().isoformat()
    clean_base = base_url.rstrip("/") if base_url else ""

    urls = [f"{domain}{clean_base}/"]
    for p in projects:
        urls.append(f"{domain}{clean_base}/{p.slug}/")

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{url}</loc>")
        xml_lines.append(f"    <lastmod>{today}</lastmod>")
        xml_lines.append("    <changefreq>monthly</changefreq>")
        xml_lines.append("  </url>")
    xml_lines.append("</urlset>")
    return "\n".join(xml_lines)


def build(
    *,
    content_dir: str | Path,
    templates_dir: str | Path,
    assets_dir: str | Path,
    output_dir: str | Path,
    site_data: dict[str, Any] | None = None,
    base_url: str | None = None,
    strict: bool = False,
    # Backward compatibility kwargs
    site: dict[str, Any] | None = None,
    home: dict[str, Any] | None = None,
    work: dict[str, Any] | None = None,
    intersection: dict[str, Any] | None = None,
    about: dict[str, Any] | None = None,
) -> list[Project]:
    content_dir = Path(content_dir)
    templates_dir = Path(templates_dir)
    assets_dir = Path(assets_dir)
    output_dir = Path(output_dir)

    # 1. Load site configuration and global copy
    if site_data is None:
        site_data = load_site_config(content_dir)

    # Merge backward-compatibility overrides if passed
    current_site = dict(site_data.get("site", {}))
    if site is not None:
        current_site.update(site)

    current_home = dict(site_data.get("home", {}))
    if home is not None:
        current_home.update(home)

    current_work = dict(site_data.get("work", {}))
    if work is not None:
        current_work.update(work)

    current_intersection = dict(site_data.get("intersection", {}))
    if intersection is not None:
        current_intersection.update(intersection)

    current_about = dict(site_data.get("about", {}))
    if about is not None:
        current_about.update(about)

    if base_url is None:
        base_url = site_data.get("base_url", "")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Collect content files and extract referenced images
    raw_projects, referenced_images = collect_content_and_images(content_dir, strict=strict)

    # 3. Incrementally optimize and sync assets (only referenced images + non-images)
    image_map = sync_assets(
        assets_dir=assets_dir,
        output_assets_dir=output_dir / "assets",
        referenced_images=referenced_images,
        generate_syntax_css=True,
    )

    # 4. Normalize projects and group by category
    disciplines = site_data.get("disciplines", [])
    projects = build_project_models(
        raw_projects,
        image_map=image_map,
        disciplines_registry=disciplines,
        base_url=base_url,
        strict=strict,
    )
    categories = group_by_category(projects)

    used_discipline_ids = {d for p in projects for d in p.disciplines}
    active_disciplines = [d for d in disciplines if d["id"] in used_discipline_ids]
    now_year = datetime.date.today().year

    # 5. Setup Jinja template environment
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["url_for"] = lambda name, project=None: _url_for(name, project=project, base_url=base_url)
    env.globals["asset_url"] = lambda path: _asset_url(path, base_url=base_url)
    env.globals["base_url"] = base_url

    # 6. Render index.html
    index_html = env.get_template("index.html").render(
        site=current_site,
        home=current_home,
        work=current_work,
        categories=categories,
        projects=projects,
        featured_projects=[p for p in projects if p.featured],
        disciplines=disciplines,
        active_disciplines=active_disciplines,
        intersection=current_intersection,
        about=current_about,
        now_year=now_year,
    )
    _write_if_changed(output_dir / "index.html", index_html)

    # 7. Render archive page (work.html) if template exists
    if (templates_dir / "work.html").exists():
        work_dir = output_dir / "work"
        work_dir.mkdir(parents=True, exist_ok=True)
        work_html = env.get_template("work.html").render(
            site=current_site,
            work=current_work,
            projects=projects,
            disciplines=disciplines,
            active_disciplines=active_disciplines,
            now_year=now_year,
        )
        _write_if_changed(work_dir / "index.html", work_html)

    # 8. Render project detail pages
    project_template = env.get_template("project.html")
    expected_slugs: set[str] = {"work"}

    for project in projects:
        expected_slugs.add(project.slug)
        project_dir = output_dir / project.slug
        project_dir.mkdir(parents=True, exist_ok=True)
        html = project_template.render(
            site=current_site,
            project=project,
            now_year=now_year,
        )
        _write_if_changed(project_dir / "index.html", html)

    # Clean up orphaned project directories
    for child in output_dir.iterdir():
        if child.is_dir() and child.name != "assets" and child.name not in expected_slugs:
            import shutil
            shutil.rmtree(child, ignore_errors=True)

    # 9. Render 404.html if template exists
    if (templates_dir / "404.html").exists():
        html_404 = env.get_template("404.html").render(
            site=current_site,
            now_year=now_year,
        )
        _write_if_changed(output_dir / "404.html", html_404)

    # 9. Generate sitemap.xml
    sitemap_xml = _generate_sitemap_xml(projects, current_site, base_url=base_url)
    _write_if_changed(output_dir / "sitemap.xml", sitemap_xml)

    print(
        f"Built {len(projects)} project(s) across {len(categories)} "
        f"categor{'y' if len(categories) == 1 else 'ies'} -> {output_dir}"
    )
    return projects
