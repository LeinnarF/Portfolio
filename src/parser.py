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

Keeping this parser dumb on purpose — it doesn't know about the Project
model or validation rules. That lives in models.py / loader.py, so this
file can be reused for any Markdown-with-front-matter source, not just
project pages.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import markdown
import yaml

# Matches:  ---\n <yaml> \n---\n <body>
# DOTALL so `.` matches newlines inside the yaml block and the body.
_FRONT_MATTER_RE = re.compile(r"^[ \t]*---[ \t]*\n(.*?\n)---[ \t]*\n(.*)$", re.DOTALL)

_MARKDOWN_EXTENSIONS = [
    "fenced_code",  # ```python ... ``` blocks
    "tables",  # pipe tables
    "codehilite",  # syntax highlighting (pairs with a pygments CSS theme)
    "toc",  # adds id="" to headings, harmless if unused
]


class ParseError(Exception):
    """Raised when a content file is missing or has malformed front matter."""


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

    html = markdown.markdown(body_raw.strip(), extensions=_MARKDOWN_EXTENSIONS)

    return metadata, html
