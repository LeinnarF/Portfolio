"""
Parses a single content/<slug>.md file into (metadata dict, html body).

Expected file shape:

    ---
    title: Project Title
    summary: One-line summary for the index card.
    technologies: [Python, Pandas]
    ---

    ## Overview

    Markdown content here...

    ![[eda-plot.png|Distribution of ratings before cleaning]]
    ![[eda-plot.png|Distribution of ratings before cleaning|500]]
    ![[eda-plot.png|Distribution of ratings before cleaning|500x100]]
    ![[eda-plot.png|Distribution of ratings before cleaning|80%]]
    ![[eda-plot.png|Distribution of ratings before cleaning|100%x30%]]

    More content after the image...

Inline images use `![[filename]]`, `![[filename|caption]]`, or
`![[filename|caption|size]]` (Obsidian-style embed syntax).
The size parameter can be in pixels (e.g. `500`, `500x100`) or percentage
(e.g. `80%`, `80%x90%`, `100%x30%`).
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any, Callable, NamedTuple

import markdown
import yaml

from .utils import asset_url

# Matches:  ---\n <yaml> \n---\n <body>
_FRONT_MATTER_RE = re.compile(r"^[ \t]*---[ \t]*\n(.*?\n)---[ \t]*\n(.*)$", re.DOTALL)

# Matches ![[path]] or ![[path|...]] — Obsidian-style embed syntax.
_INLINE_IMAGE_RE = re.compile(r"!\[\[\s*([^|\]]+?)\s*(?:\|(.*?))?\]\]")

# Matches dimensions in pixels (500, 500px) or percentage (80%, 100%).
_DIM_PATTERN = r"(\d+(?:\.\d+)?)\s*(%|px)?"
_SIZE_RE = re.compile(rf"^\s*{_DIM_PATTERN}(?:\s*[xX]\s*{_DIM_PATTERN})?\s*$")

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


class ImageSize(NamedTuple):
    w_val: float
    w_unit: str  # "px" or "%"
    h_val: float | None = None
    h_unit: str | None = None  # "px" or "%" or None


def _format_num(n: float) -> str:
    """Format float into compact string without trailing zeros for integers."""
    return str(int(n)) if n.is_integer() else f"{n:g}"


def _parse_size(val: str) -> ImageSize | None:
    """
    Parse a size token into an ImageSize.
    Supports pixels ('500', '500x100') and percentages ('80%', '80%x90%', '100%x30%').
    """
    if not val:
        return None
    m = _SIZE_RE.match(val)
    if not m:
        return None
    w_val = float(m.group(1))
    w_unit = m.group(2) or "px"

    h_val = float(m.group(3)) if m.group(3) else None
    h_unit = (m.group(4) or "px") if m.group(3) else None

    if w_val <= 0 or (h_val is not None and h_val <= 0):
        return None

    return ImageSize(w_val=w_val, w_unit=w_unit, h_val=h_val, h_unit=h_unit)


def _parse_embed_params(params_str: str | None) -> tuple[str | None, ImageSize | None]:
    """
    Parse the parameters following the image path in an embed tag.
    Returns (caption, custom_size).

    Supports:
        - ![[path]] -> (None, None)
        - ![[path|caption]] -> (caption, None)
        - ![[path|size]] -> (None, size)
        - ![[path|caption|size]] -> (caption, size)
        - ![[path||size]] -> (None, size)
    where size can be in pixels ('500', '500x100') or percentages ('80%', '80%x90%', '100%x30%').
    """
    if params_str is None:
        return None, None

    parts = [p.strip() for p in params_str.split("|")]
    caption: str | None = None
    custom_size: ImageSize | None = None

    if len(parts) == 1:
        size = _parse_size(parts[0])
        if size:
            custom_size = size
        else:
            caption = parts[0] or None
    elif len(parts) == 2:
        # Standard: caption | size (or empty caption | size)
        size = _parse_size(parts[1])
        if size:
            caption = parts[0] or None
            custom_size = size
        else:
            # Check if inverted: size | caption
            size_0 = _parse_size(parts[0])
            if size_0:
                custom_size = size_0
                caption = parts[1] or None
            else:
                caption = f"{parts[0]}|{parts[1]}"
    else:
        # 3 or more parts: e.g. caption with pipes | size
        size = _parse_size(parts[-1])
        if size:
            custom_size = size
            caption = " | ".join(parts[:-1]).strip() or None
        else:
            caption = " | ".join(parts).strip() or None

    return caption, custom_size


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
        refs.add(path)
    return refs


def _render_inline_images(
    body: str,
    image_map: dict[str, tuple[str, int, int]] | None = None,
    base_url: str = "",
) -> str:
    """
    Replace ![[filename]] / ![[filename|caption]] / ![[filename|caption|size]] tokens
    with an optimized <figure> block.
    """

    def _replace(match: re.Match[str]) -> str:
        raw_path = match.group(1).strip()
        params_str = match.group(2)
        caption, custom_size = _parse_embed_params(params_str)

        path = raw_path.lstrip("/")
        if path.startswith(f"{_IMAGES_SUBDIR}/"):
            path = path[len(_IMAGES_SUBDIR) + 1:]
        full_path = f"{_IMAGES_SUBDIR}/{path}"

        target_path = full_path
        orig_width = 0
        orig_height = 0

        if image_map:
            # Check mappings
            info = (
                image_map.get(raw_path)
                or image_map.get(full_path)
                or image_map.get(path)
            )
            if info:
                target_path, orig_width, orig_height = info

        alt_text = caption or Path(path).stem.replace("-", " ").replace("_", " ")
        src = asset_url(target_path, base_url=base_url)

        img_attrs = [
            f'src="{html.escape(src)}"',
            f'alt="{html.escape(alt_text)}"',
            'loading="lazy"',
            'decoding="async"',
        ]

        figure_classes = ["gallery-item"]

        if custom_size is not None:
            figure_classes.append("is-resized")
            w_val, w_unit = custom_size.w_val, custom_size.w_unit
            h_val, h_unit = custom_size.h_val, custom_size.h_unit

            if w_unit == "px":
                w_str = f"{_format_num(w_val)}px"
                img_attrs.append(f'width="{int(w_val)}"')
                if h_val is None:
                    # Width in px, height auto (aspect ratio retained)
                    if orig_width > 0 and orig_height > 0:
                        calc_h = max(1, round(w_val * orig_height / orig_width))
                        img_attrs.append(f'height="{calc_h}"')
                    img_attrs.append(
                        f'style="width: {w_str}; max-width: 100%; height: auto;"'
                    )
                elif h_unit == "px":
                    # Width in px, height in px (aspect ratio changed)
                    img_attrs.append(f'height="{int(h_val)}"')
                    img_attrs.append(
                        f'style="width: {w_str}; max-width: 100%; height: {int(h_val)}px;"'
                    )
                else:  # h_unit == "%"
                    if orig_width > 0 and orig_height > 0:
                        calc_h = max(1, round(w_val * (orig_height / orig_width) * (h_val / 100)))
                        img_attrs.append(f'height="{calc_h}"')
                        img_attrs.append(
                            f'style="width: {w_str}; max-width: 100%; height: {calc_h}px;"'
                        )
                    else:
                        img_attrs.append(
                            f'style="width: {w_str}; max-width: 100%; height: auto; aspect-ratio: 100 / {_format_num(h_val)};"'
                        )
            else:  # w_unit == "%"
                w_str = f"{_format_num(w_val)}%"
                if h_val is None:
                    # Single percentage: width in %, height auto (aspect ratio retained)
                    if orig_width > 0 and orig_height > 0:
                        img_attrs.append(f'width="{orig_width}"')
                        img_attrs.append(f'height="{orig_height}"')
                    img_attrs.append(
                        f'style="width: {w_str}; max-width: 100%; height: auto;"'
                    )
                elif h_unit == "%":
                    # Both in percentage: e.g. 80%x90% or 100%x30%
                    if orig_width > 0 and orig_height > 0:
                        calc_w = max(1, round(orig_width * (w_val / 100)))
                        calc_h = max(1, round(orig_height * (h_val / 100)))
                        img_attrs.append(f'width="{calc_w}"')
                        img_attrs.append(f'height="{calc_h}"')
                        ratio = (orig_width * w_val) / (orig_height * h_val)
                        img_attrs.append(
                            f'style="width: {w_str}; max-width: 100%; height: auto; aspect-ratio: {round(ratio, 4)};"'
                        )
                    else:
                        ratio_str = f"{_format_num(w_val)} / {_format_num(h_val)}"
                        img_attrs.append(
                            f'style="width: {w_str}; max-width: 100%; height: auto; aspect-ratio: {ratio_str};"'
                        )
                else:  # h_unit == "px"
                    img_attrs.append(f'height="{int(h_val)}"')
                    img_attrs.append(
                        f'style="width: {w_str}; max-width: 100%; height: {int(h_val)}px;"'
                    )
        elif orig_width and orig_height:
            img_attrs.append(f'width="{orig_width}"')
            img_attrs.append(f'height="{orig_height}"')

        parts = [
            f'<figure class="{" ".join(figure_classes)}">',
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
