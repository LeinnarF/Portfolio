"""
Walks content/*.md (and optional content/<type>/*.md), parses each file,
and normalizes the result into Project objects.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .models import CATEGORY_LABELS, Project
from .parser import (
    ParseError,
    extract_inline_image_refs,
    parse_front_matter_and_body,
    render_markdown_body,
)
from .utils import slugify


def load_site_config(content_dir: str | Path) -> dict[str, Any]:
    """
    Load site-wide copy and settings from content/_site.yaml.
    """
    content_dir = Path(content_dir)
    site_file = content_dir / "_site.yaml"
    if not site_file.exists():
        site_file = content_dir / "_site.yml"

    if not site_file.exists():
        return {}

    try:
        data = yaml.safe_load(site_file.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            return data
    except Exception as exc:
        print(f"[loader] Warning: could not parse {site_file.name}: {exc}")

    return {}


def discover_content_files(content_dir: str | Path) -> list[tuple[Path, str]]:
    """
    Discover all (markdown_file_path, project_type) pairs in content_dir.
    Supports:
    - Single flat folder: all projects directly in content/*.md
    - Nested category folders: content/<type>/*.md (for backwards compatibility)
    """
    content_dir = Path(content_dir)
    discovered: list[tuple[Path, str]] = []

    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory not found: {content_dir}")

    # 1. Flat projects directly in content/ (single folder, no subsections)
    for md_file in sorted(content_dir.glob("*.md")):
        if md_file.name.startswith((".", "_")):
            continue
        discovered.append((md_file, "project"))

    # 2. Projects inside subdirectories (content/<type>/*.md)
    for type_dir in sorted(p for p in content_dir.iterdir() if p.is_dir()):
        if type_dir.name.startswith((".", "_")):
            continue
        project_type = type_dir.name
        for md_file in sorted(type_dir.glob("*.md")):
            if md_file.name.startswith((".", "_")):
                continue
            discovered.append((md_file, project_type))

    return discovered


def collect_content_and_images(
    content_dir: str | Path,
    strict: bool = False,
) -> tuple[list[dict[str, Any]], set[str]]:
    """
    First pass: parse front matter and extract all referenced images
    across all valid project content files.
    """
    raw_projects: list[dict[str, Any]] = []
    referenced_images: set[str] = set()

    for md_file, project_type in discover_content_files(content_dir):
        try:
            metadata, body_raw = parse_front_matter_and_body(md_file)
        except ParseError as exc:
            msg = f"[loader] Skipping {md_file}: {exc}"
            if strict:
                raise ParseError(msg) from exc
            print(msg)
            continue

        metadata.setdefault("slug", slugify(md_file.stem))
        if "type" not in metadata or not metadata["type"]:
            metadata["type"] = project_type
        metadata["_body_raw"] = body_raw
        metadata["_source_file"] = md_file

        if metadata.get("cover_image"):
            referenced_images.add(str(metadata["cover_image"]))

        inline_refs = extract_inline_image_refs(body_raw)
        referenced_images.update(inline_refs)

        raw_projects.append(metadata)

    return raw_projects, referenced_images


def build_project_models(
    raw_projects: list[dict[str, Any]],
    image_map: dict[str, tuple[str, int, int]] | None = None,
    disciplines_registry: list[dict[str, Any]] | None = None,
    base_url: str = "",
    strict: bool = False,
) -> list[Project]:
    """
    Second pass: render markdown bodies with optimized image paths and
    validate into Project model instances.
    """
    projects: list[Project] = []
    registry_map = {d["id"]: d.get("label", d["id"]) for d in (disciplines_registry or [])}

    for raw in raw_projects:
        data = dict(raw)
        body_raw = data.pop("_body_raw", "")
        source_file = data.pop("_source_file", Path(data.get("slug", "unknown")))

        # Validate and normalize disciplines
        project_disciplines = data.get("disciplines")
        if project_disciplines is None:
            # Fallback to type if specified, otherwise empty
            default_disc = data.get("type")
            if default_disc and default_disc != "project":
                project_disciplines = [default_disc]
            else:
                project_disciplines = []
            data["disciplines"] = project_disciplines
        elif isinstance(project_disciplines, str):
            project_disciplines = [project_disciplines]
            data["disciplines"] = project_disciplines

        if registry_map:
            for disc in project_disciplines:
                if disc not in registry_map:
                    msg = (
                        f"[loader] Unknown discipline '{disc}' in {source_file}. "
                        f"Allowed disciplines: {list(registry_map.keys())}"
                    )
                    if strict:
                        raise ValueError(msg)
                    print(msg)

        data["discipline_labels"] = [
            registry_map.get(d, CATEGORY_LABELS.get(d, d.replace("-", " ").title()))
            for d in project_disciplines
        ]

        if not data.get("year") and data.get("date"):
            data["year"] = str(data["date"]).split("-")[0]

        # Update cover_image if mapped
        cover = data.get("cover_image")
        if cover and image_map:
            target_info = (
                image_map.get(cover)
                or image_map.get(f"images/{cover}")
                or image_map.get(cover.lstrip("/"))
            )
            if target_info:
                data["cover_image"] = target_info[0]
                if target_info[1] and target_info[2]:
                    data["cover_width"] = target_info[1]
                    data["cover_height"] = target_info[2]

        html_content = render_markdown_body(body_raw, image_map=image_map, base_url=base_url)
        data["content"] = html_content

        try:
            project = Project(**data)
        except ValidationError as exc:
            msg = f"[loader] Skipping {source_file}, invalid front matter:\n{exc}"
            if strict:
                raise ValidationError(msg) from exc
            print(msg)
            continue

        if project.draft:
            continue

        projects.append(project)

    projects.sort(key=lambda p: (not p.featured, p.order, p.title.lower()))
    return projects


def load_projects(
    content_dir: str | Path,
    image_map: dict[str, tuple[str, int, int]] | None = None,
    disciplines_registry: list[dict[str, Any]] | None = None,
    base_url: str = "",
    strict: bool = False,
) -> list[Project]:
    """
    Convenience loader that executes both passes.
    """
    raw_projects, _ = collect_content_and_images(content_dir, strict=strict)
    return build_project_models(
        raw_projects,
        image_map=image_map,
        disciplines_registry=disciplines_registry,
        base_url=base_url,
        strict=strict,
    )


def group_by_category(projects: list[Project]) -> list[dict[str, Any]]:
    """
    Turn a flat project list into the `categories` structure, grouped by primary discipline.
    """
    grouped: dict[str, list[Project]] = {}
    for p in projects:
        grouped.setdefault(p.category_id, []).append(p)

    return [
        {
            "id": cat_id,
            "label": CATEGORY_LABELS.get(cat_id, cat_id.replace("-", " ").upper()),
            "projects": projs,
        }
        for cat_id, projs in grouped.items()
    ]
