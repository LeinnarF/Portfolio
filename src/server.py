"""
Development server with live-reload support.

Watches content/, templates/, assets/, src/, and main.py for changes,
rebuilds the static site on the fly, and automatically reloads connected browser tabs.
"""

from __future__ import annotations

import functools
import http.server
import importlib
import runpy
import sys
import webbrowser
from pathlib import Path
from typing import Any

from livereload import Server

from .builder import build


def serve(
    *,
    content_dir: Path,
    templates_dir: Path,
    assets_dir: Path,
    output_dir: Path,
    src_dir: Path,
    main_file: Path,
    site: dict[str, Any],
    home: dict[str, Any],
    work: dict[str, Any],
    intersection: dict[str, Any],
    about: dict[str, Any],
    port: int = 8000,
    host: str = "127.0.0.1",
    watch: bool = True,
    open_browser: bool = False,
) -> None:
    """
    Serve the static site locally.

    If watch is True, watches source directories and re-builds with live-reload.
    If watch is False, serves the static directory via standard HTTP server.
    """
    content_dir = Path(content_dir)
    templates_dir = Path(templates_dir)
    assets_dir = Path(assets_dir)
    output_dir = Path(output_dir)
    src_dir = Path(src_dir)
    main_file = Path(main_file)

    if not watch:
        print(f"Building site to {output_dir}...")
        build(
            content_dir=content_dir,
            templates_dir=templates_dir,
            assets_dir=assets_dir,
            output_dir=output_dir,
            site=site,
            home=home,
            work=work,
            intersection=intersection,
            about=about,
        )

        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(output_dir))
        with http.server.ThreadingHTTPServer((host, port), handler) as httpd:
            print(f"\nServing static site on http://{host}:{port}/ (watching disabled)")
            print("Press Ctrl+C to stop.\n")
            if open_browser:
                webbrowser.open(f"http://{host}:{port}/")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
        return

    server = Server()

    def rebuild() -> None:
        try:
            # Reload src modules in case build logic was modified
            for mod_name in ["src.models", "src.utils", "src.parser", "src.loader", "src.builder"]:
                if mod_name in sys.modules:
                    importlib.reload(sys.modules[mod_name])

            # Dynamically fetch site copy if main_file is updated
            current_site = site
            current_home = home
            current_work = work
            current_intersection = intersection
            current_about = about

            if main_file.exists():
                try:
                    data = runpy.run_path(str(main_file))
                    current_site = data.get("SITE", current_site)
                    current_home = data.get("HOME", current_home)
                    current_work = data.get("WORK", current_work)
                    current_intersection = data.get("INTERSECTION", current_intersection)
                    current_about = data.get("ABOUT", current_about)
                except Exception as exc:
                    print(f"[live-reload] Warning: could not reload copy from {main_file.name}: {exc}")

            from .builder import build as run_build

            run_build(
                content_dir=content_dir,
                templates_dir=templates_dir,
                assets_dir=assets_dir,
                output_dir=output_dir,
                site=current_site,
                home=current_home,
                work=current_work,
                intersection=current_intersection,
                about=current_about,
            )
        except Exception as exc:
            print(f"[live-reload] Build error: {exc}")

    # Initial build before starting server
    print(f"Building site to {output_dir}...")
    rebuild()

    def should_ignore(filepath: str) -> bool:
        name = Path(filepath).name
        return (
            name.startswith((".", "~"))
            or name.endswith((".swp", ".tmp", ".pyc"))
            or "__pycache__" in filepath
        )

    # Register watchers
    if content_dir.exists():
        server.watch(str(content_dir), rebuild, ignore=should_ignore)
    if templates_dir.exists():
        server.watch(str(templates_dir), rebuild, ignore=should_ignore)
    if assets_dir.exists():
        server.watch(str(assets_dir), rebuild, ignore=should_ignore)
    if src_dir.exists():
        server.watch(str(src_dir), rebuild, ignore=should_ignore)
    if main_file.exists():
        server.watch(str(main_file), rebuild, ignore=should_ignore)

    print(f"\nServing site with live-reload at http://{host}:{port}/")
    print("Watching for changes in content/, templates/, assets/, src/, and main.py...")
    print("Press Ctrl+C to stop.\n")

    server.serve(
        root=str(output_dir),
        host=host,
        port=port,
        open_url_delay=1 if open_browser else None,
        restart_delay=0,
    )
