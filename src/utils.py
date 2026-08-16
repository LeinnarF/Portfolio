"""Small helpers shared across the build pipeline."""

from __future__ import annotations


def asset_url(path: str) -> str:
    """
    Turn a path under assets/ (e.g. 'images/uiux/shot.png') into the
    site-relative URL it's served at ('/assets/images/uiux/shot.png').
    """
    return f"/assets/{path.lstrip('/')}"
