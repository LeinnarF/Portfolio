"""Small helpers shared across the build pipeline."""

from __future__ import annotations

import re
import urllib.parse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Project


def asset_url(path: str, base_url: str = "") -> str:
    """
    Turn a path under assets/ (e.g. 'images/uiux/shot.png') into a
    properly quoted and base_url-prefixed URL.
    """
    clean_base = base_url.rstrip("/") if base_url else ""
    # Quote individual path segments while keeping '/' safe
    encoded_path = urllib.parse.quote(path.lstrip("/"), safe="/:@=&?+$,")
    return f"{clean_base}/assets/{encoded_path}"


def url_for(name: str, project: Project | None = None, base_url: str = "") -> str:
    """
    Generate an internal site URL with base_url prefix.
    """
    clean_base = base_url.rstrip("/") if base_url else ""
    if name == "project":
        if project is None:
            raise ValueError("url_for('project', ...) requires a project argument")
        return f"{clean_base}/{project.slug}/"
    elif name == "index":
        return f"{clean_base}/" if clean_base else "/"
    return f"{clean_base}/{name.lstrip('/')}"


def slugify(text: str) -> str:
    """
    Normalize a string into a URL-safe slug: lowercase, alphanumerics
    joined by single hyphens. Used as the fallback when a content file
    doesn't set an explicit `slug` in its front matter.
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "untitled"
