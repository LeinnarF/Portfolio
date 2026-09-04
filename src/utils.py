"""Small helpers shared across the build pipeline."""

from __future__ import annotations


def asset_url(path: str) -> str:
    """
    Turn a path under assets/ (e.g. 'images/uiux/shot.png') into the
    site-relative URL it's served at ('/assets/images/uiux/shot.png').
    """
    return f"/assets/{path.lstrip('/')}"


def slugify(text: str) -> str:
    """
    Normalize a string into a URL-safe slug: lowercase, alphanumerics
    joined by single hyphens. Used as the fallback when a content file
    doesn't set an explicit `slug` in its front matter — so a note named
    "Internship Project.md" still builds a clean /internship-project/
    URL instead of one with a literal space and capital letters in it.
    """
    import re

    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "untitled"
