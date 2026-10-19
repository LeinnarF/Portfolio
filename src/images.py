"""
Image optimization and asset synchronization pipeline.

Features:
- WebP conversion and max-width resizing via Pillow
- Hash/mtime caching so unchanged images are not re-processed
- Only referenced images (covers and inline markdown embeds) are built
- Incremental syncing for non-image assets (CSS, JS, fonts)
- Cleanup of orphaned output files
- Automated Pygments syntax highlighting stylesheet generation
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps
from pygments.formatters import HtmlFormatter


OPTIMIZABLE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def normalize_image_relpath(path: str) -> str:
    """
    Ensure relative path under assets is consistent.
    E.g. 'images/cover/test2.png', or 'test1.png' -> 'images/test1.png'.
    """
    clean = path.strip().lstrip("/")
    if not clean.startswith("images/") and not clean.startswith("css/") and not clean.startswith("js/"):
        return f"images/{clean}"
    return clean


def find_source_file(assets_dir: Path, rel_path: str) -> Path | None:
    """Find the source file in assets_dir given a relative path."""
    candidates = [
        assets_dir / rel_path,
        assets_dir / "images" / rel_path,
        assets_dir / rel_path.lstrip("/"),
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def optimize_single_image(
    source_file: Path,
    target_file: Path,
    max_width: int = 1600,
) -> tuple[int, int]:
    """
    Convert an image to WebP with max-width bounding and quality=80.
    Returns (width, height) of the resulting image.
    Uses mtime caching to skip unchanged files.
    """
    target_file.parent.mkdir(parents=True, exist_ok=True)

    # Check cache: if target exists and is newer than source, skip re-encoding
    if target_file.exists() and target_file.stat().st_mtime >= source_file.stat().st_mtime:
        try:
            with Image.open(target_file) as im:
                return im.size
        except Exception:
            pass

    try:
        with Image.open(source_file) as im:
            im = ImageOps.exif_transpose(im)
            orig_w, orig_h = im.size

            if orig_w > max_width:
                aspect = orig_h / orig_w
                new_w = max_width
                new_h = max(1, int(max_width * aspect))
                im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            else:
                new_w, new_h = orig_w, orig_h

            # Convert mode if needed for WebP
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if "transparency" in im.info or im.mode == "P" else "RGB")

            im.save(target_file, "WEBP", quality=80, method=6)
            return new_w, new_h
    except Exception as exc:
        print(f"[images] Warning: Failed to optimize {source_file.name}: {exc}. Copying as-is.")
        shutil.copy2(source_file, target_file)
        return (0, 0)


def sync_assets(
    assets_dir: Path,
    output_assets_dir: Path,
    referenced_images: set[str],
    generate_syntax_css: bool = True,
) -> dict[str, tuple[str, int, int]]:
    """
    Incrementally sync assets to output_assets_dir:
    - Only optimize/copy referenced images
    - Sync all non-image assets (CSS, JS, docs, etc.)
    - Generate Pygments syntax.css
    - Remove orphaned assets in output_assets_dir

    Returns a mapping:
      normalized_ref_path -> (target_rel_path, width, height)
    """
    assets_dir = Path(assets_dir)
    output_assets_dir = Path(output_assets_dir)
    output_assets_dir.mkdir(parents=True, exist_ok=True)

    expected_output_files: set[Path] = set()
    image_map: dict[str, tuple[str, int, int]] = {}

    # 1. Process referenced images
    for ref in referenced_images:
        norm_ref = normalize_image_relpath(ref)
        src_file = find_source_file(assets_dir, norm_ref)
        if not src_file:
            print(f"[images] Warning: Referenced asset not found: '{ref}' (resolved to '{norm_ref}')")
            continue

        ext = src_file.suffix.lower()
        if ext in OPTIMIZABLE_EXTENSIONS:
            # Change extension to .webp
            target_rel = Path(norm_ref).with_suffix(".webp").as_posix()
            target_file = output_assets_dir / target_rel
            w, h = optimize_single_image(src_file, target_file)
        else:
            # Non-optimizable image (e.g. svg, gif)
            target_rel = norm_ref
            target_file = output_assets_dir / target_rel
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if not target_file.exists() or src_file.stat().st_mtime > target_file.stat().st_mtime:
                shutil.copy2(src_file, target_file)
            w, h = (0, 0)

        expected_output_files.add(target_file.resolve())
        image_map[ref] = (target_rel, w, h)
        image_map[norm_ref] = (target_rel, w, h)
        # Also map without leading images/ if applicable
        if norm_ref.startswith("images/"):
            bare = norm_ref[len("images/"):]
            image_map[bare] = (target_rel, w, h)

    # 2. Sync non-image assets (CSS, JS, fonts, PDF, etc.)
    if assets_dir.exists():
        for path in assets_dir.rglob("*"):
            if not path.is_file():
                continue
            # Skip unreferenced images under images/
            rel_to_assets = path.relative_to(assets_dir).as_posix()
            if rel_to_assets.startswith("images/"):
                continue

            target_file = output_assets_dir / rel_to_assets
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if not target_file.exists() or path.stat().st_mtime > target_file.stat().st_mtime:
                shutil.copy2(path, target_file)
            expected_output_files.add(target_file.resolve())

    # 3. Generate Pygments syntax.css
    if generate_syntax_css:
        syntax_css_file = output_assets_dir / "css" / "syntax.css"
        syntax_css_file.parent.mkdir(parents=True, exist_ok=True)
        if not syntax_css_file.exists():
            formatter = HtmlFormatter(style="friendly")
            css_content = formatter.get_style_defs(".codehilite")
            syntax_css_file.write_text(css_content, encoding="utf-8")
        expected_output_files.add(syntax_css_file.resolve())

    # 4. Remove orphaned files in output_assets_dir
    for out_file in output_assets_dir.rglob("*"):
        if out_file.is_file() and out_file.resolve() not in expected_output_files:
            try:
                out_file.unlink()
            except OSError:
                pass

    return image_map
