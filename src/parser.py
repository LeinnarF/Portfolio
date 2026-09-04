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
style embed syntax) — just the bare filename, no folder needed. It's
always resolved to assets/images/<filename>, same as Obsidian resolving
![[...]] against a single attachments folder regardless of where the
note lives. This replaces a front-matter `gallery` list — images live
exactly where they're relevant in the write-up instead of being pinned
to a fixed spot on the page.

Keeping this parser dumb on purpose — it doesn't know about the Project
model or validation rules. That lives in models.py / loader.py, so this
file can be reused for any Markdown-with-front-matter source, not just
project pages.
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

import markdown
import yaml

from .utils import asset_url

# Matches:  ---\n <yaml> \n---\n <body>
# DOTALL so `.` matches newlines inside the yaml block and the body.
_FRONT_MATTER_RE = re.compile(r"^[ \t]*---[ \t]*\n(.*?\n)---[ \t]*\n(.*)$", re.DOTALL)

# Matches ![[path]] or ![[path|caption]] — Obsidian-style embed syntax.
# Path can't contain '|' or ']'; caption (optional) runs up to the closing ']]'.
_INLINE_IMAGE_RE = re.compile(r"!\[\[\s*([^|\]]+?)\s*(?:\|\s*(.+?)\s*)?\]\]")

# All inline-embedded images live flat under assets/images/, mirroring how
# Obsidian resolves ![[filename]] against a single attachments folder
# regardless of where the note lives — no category subfolder needed.
_IMAGES_SUBDIR = "images"

_MARKDOWN_EXTENSIONS = [
    "fenced_code",  # ```python ... ``` blocks
    "tables",  # pipe tables
    "codehilite",  # syntax highlighting (pairs with a pygments CSS theme)
    "toc",  # adds id="" to headings, harmless if unused
]


class ParseError(Exception):
    """Raised when a content file is missing or has malformed front matter."""


def _render_inline_images(body: str) -> str:
    """
    Replace ![[filename]] / ![[filename|caption]] tokens with a <figure>
    block, always resolved under assets/images/.

    Runs on the raw Markdown *before* it's converted to HTML. The output
    is a block-level HTML tag on its own line, which Python-Markdown
    passes through unwrapped (not stuffed inside a <p>) as long as it's
    surrounded by blank lines — which is how this syntax is meant to be
    used (on its own line, not inline mid-sentence).
    """

    def _replace(match: re.Match[str]) -> str:
        raw_path = match.group(1).strip()
        caption = match.group(2).strip() if match.group(2) else None

        # Obsidian-style: just a bare filename, always resolved under
        # assets/images/. Strip a leading 'images/' if someone writes it
        # anyway, so it doesn't double up.
        path = raw_path.lstrip("/")
        if path.startswith(f"{_IMAGES_SUBDIR}/"):
            path = path[len(_IMAGES_SUBDIR) + 1:]
        full_path = f"{_IMAGES_SUBDIR}/{path}"

        alt_text = caption or Path(path).stem.replace("-", " ").replace("_", " ")
        src = asset_url(full_path)

        parts = [
            '<figure class="gallery-item">',
            f'<img src="{html.escape(src)}" alt="{html.escape(alt_text)}">',
        ]
        if caption:
            parts.append(f"<figcaption>{html.escape(caption)}</figcaption>")
        parts.append("</figure>")
        return "\n".join(parts)

    return _INLINE_IMAGE_RE.sub(_replace, body)


def parse_markdown_file(path: str | Path) -> tuple[dict[str, Any], str]:
    """
    Read a Markdown file with YAML front matter and return (metadata, html).

    Raises ParseError if the file has no front matter block or the YAML
    in it doesn't parse.
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

    body = _render_inline_images(body_raw.strip())
    html_body = markdown.markdown(body, extensions=_MARKDOWN_EXTENSIONS)

    return metadata, html_body

