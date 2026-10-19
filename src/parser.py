"""
Parses a single content/<type>/<slug>.md file into (metadata dict, html body).

Expected file shape:

    ---
    title: Project Title
    summary: One-line summary for the index card.
    technologies: [Python, Pandas]
    ---

    ## Overview

    Markdown content here...

    ![[eda-plot.png|Distribution of ratings before cleaning]]

    More content after the image...

Inline images use `![[filename]]` or `![[filename|caption]]` (Obsidian-
style embed syntax).
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any, Callable

import markdown
import yaml

from .utils import asset_url

# Matches:  ---\n <yaml> \n---\n <body>
_FRONT_MATTER_RE = re.compile(r"^[ \t]*---[ \t]*\n(.*?\n)---[ \t]*\n(.*)$", re.DOTALL)

# Matches ![[path]] or ![[path|caption]] — Obsidian-style embed syntax.
_INLINE_IMAGE_RE = re.compile(r"!\[\[\s*([^|\]]+?)\s*(?:\|\s*(.+?)\s*)?\]\]")

_IMAGES_SUBDIR = "images"

_MARKDOWN_EXTENSIONS = [
    "fenced_code",  # ```python ... ``` blocks
    "tables",  # pipe tables
    "codehilite",  # syntax highlighting (pairs with pygments)
    "toc",  # adds id="" to headings
]

# Reusable Markdown parser instance (call reset() before each render)
_MD_PARSER = markdown.Markdown(extensions=_MARKDOWN_EXTENSIONS)


class ParseError(Exception):
    """Raised when a content file is missing or has malformed front matter."""


def extract_inline_image_refs(body: str) -> set[str]:
    """Return all raw image reference paths inside ![[...]] tags."""
    refs: set[str] = set()
    for match in _INLINE_IMAGE_RE.finditer(body):
        raw_path = match.group(1).strip()
        path = raw_path.lstrip("/")
        if path.startswith(f"{_IMAGES_SUBDIR}/"):
            path = path[len(_IMAGES_SUBDIR) + 1:]
        refs.add(f"{_IMAGES_SUBDIR}/{path}")
        refs.add(raw_path)
    return refs


def _render_inline_images(
    body: str,
    image_map: dict[str, tuple[str, int, int]] | None = None,
    base_url: str = "",
) -> str:
    """
    Replace ![[filename]] / ![[filename|caption]] tokens with an optimized <figure> block.
    """

    def _replace(match: re.Match[str]) -> str:
        raw_path = match.group(1).strip()
        caption = match.group(2).strip() if match.group(2) else None

        path = raw_path.lstrip("/")
        if path.startswith(f"{_IMAGES_SUBDIR}/"):
            path = path[len(_IMAGES_SUBDIR) + 1:]
        full_path = f"{_IMAGES_SUBDIR}/{path}"

        target_path = full_path
        width = 0
        height = 0

        if image_map:
            # Check mappings
            info = (
                image_map.get(raw_path)
                or image_map.get(full_path)
                or image_map.get(path)
            )
            if info:
                target_path, width, height = info

        alt_text = caption or Path(path).stem.replace("-", " ").replace("_", " ")
        src = asset_url(target_path, base_url=base_url)

        img_attrs = [
            f'src="{html.escape(src)}"',
            f'alt="{html.escape(alt_text)}"',
            'loading="lazy"',
            'decoding="async"',
        ]
        if width and height:
            img_attrs.append(f'width="{width}"')
            img_attrs.append(f'height="{height}"')

        parts = [
            '<figure class="gallery-item">',
            f'<img {" ".join(img_attrs)}>',
        ]
        if caption:
            parts.append(f"<figcaption>{html.escape(caption)}</figcaption>")
        parts.append("</figure>")
        return "\n".join(parts)

    return _INLINE_IMAGE_RE.sub(_replace, body)


def parse_front_matter_and_body(path: str | Path) -> tuple[dict[str, Any], str]:
    """
    Read a Markdown file and return (metadata, raw_body).
    """
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ParseError(f"Could not read {path}: {exc}") from exc

    match = _FRONT_MATTER_RE.match(raw)
    if not match:
        raise ParseError(
            f"{path} has no YAML front matter block. "
            f"Expected the file to start with a line of '---'."
        )

    front_matter_raw, body_raw = match.groups()

    try:
        metadata = yaml.safe_load(front_matter_raw) or {}
    except yaml.YAMLError as exc:
        raise ParseError(f"Invalid YAML front matter in {path}: {exc}") from exc

    if not isinstance(metadata, dict):
        raise ParseError(
            f"Front matter in {path} did not parse to a mapping "
            f"(got {type(metadata).__name__})."
        )

    return metadata, body_raw.strip()


def render_markdown_body(
    body_raw: str,
    image_map: dict[str, tuple[str, int, int]] | None = None,
    base_url: str = "",
) -> str:
    """Render markdown body to HTML, resolving inline images."""
    body_with_images = _render_inline_images(body_raw, image_map=image_map, base_url=base_url)
    _MD_PARSER.reset()
    return _MD_PARSER.convert(body_with_images)


def parse_markdown_file(
    path: str | Path,
    image_map: dict[str, tuple[str, int, int]] | None = None,
    base_url: str = "",
) -> tuple[dict[str, Any], str]:
    """
    Read a Markdown file with YAML front matter and return (metadata, html).
    """
    metadata, body_raw = parse_front_matter_and_body(path)
    html_body = render_markdown_body(body_raw, image_map=image_map, base_url=base_url)
    return metadata, html_body
