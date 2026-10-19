"""
Development server with live-reload support.

Watches content/, templates/, assets/, and src/ for changes:
- In-process incremental rebuild on content, template, copy, and asset changes
- Clean process restart via os.execv on src/ changes
- Serves the generated static site with livereload websocket injection
"""

from __future__ import annotations

import functools
import http.server
import os
import sys
import webbrowser
from pathlib import Path
from typing import Any

from livereload import Server

from .builder import build
from .loader import load_site_config


def serve(
    *,
    content_dir: str | Path,
    templates_dir: str | Path,
    assets_dir: str | Path,
    output_dir: str | Path,
    src_dir: str | Path,
    site_data: dict[str, Any] | None = None,
    base_url: str | None = None,
    port: int = 8000,
    host: str = "127.0.0.1",
    watch: bool = True,
    open_browser: bool = False,
    # Backward compatibility kwargs (ignored if site_data is used)
    main_file: Path | None = None,
    site: dict[str, Any] | None = None,
    home: dict[str, Any] | None = None,
    work: dict[str, Any] | None = None,
    intersection: dict[str, Any] | None = None,
    about: dict[str, Any] | None = None,
) -> None:
    content_dir = Path(content_dir)
    templates_dir = Path(templates_dir)
    assets_dir = Path(assets_dir)
    output_dir = Path(output_dir)
    src_dir = Path(src_dir)

    def run_rebuild() -> None:
        try:
            # Re-read _site.yaml dynamically on each rebuild
            current_config = site_data if site_data is not None else load_site_config(content_dir)
            build(
                content_dir=content_dir,
                templates_dir=templates_dir,
                assets_dir=assets_dir,
                output_dir=output_dir,
                site_data=current_config,
                base_url=base_url,
            )
        except Exception as exc:
            print(f"[live-reload] Build error: {exc}")

    if not watch:
        print(f"Building site to {output_dir}...")
        run_rebuild()

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

    # Initial build before starting server
    print(f"Building site to {output_dir}...")
    run_rebuild()

    server = Server()

    def should_ignore(filepath: str) -> bool:
        name = Path(filepath).name
        return (
            name.startswith((".", "~"))
            or name.endswith((".swp", ".tmp", ".pyc"))
            or "__pycache__" in filepath
        )

    def on_src_change() -> None:
        print("\n[live-reload] Detected changes in src/. Restarting server process...\n")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # Watchers
    if content_dir.exists():
        server.watch(str(content_dir), run_rebuild, ignore=should_ignore)
    if templates_dir.exists():
        server.watch(str(templates_dir), run_rebuild, ignore=should_ignore)
    if assets_dir.exists():
        server.watch(str(assets_dir), run_rebuild, ignore=should_ignore)
    if src_dir.exists():
        server.watch(str(src_dir), on_src_change, ignore=should_ignore)

    print(f"\nServing site with live-reload at http://{host}:{port}/")
    print("Watching for changes in content/, templates/, assets/, and src/...")
    print("Press Ctrl+C to stop.\n")

    server.serve(
        root=str(output_dir),
        host=host,
        port=port,
        open_url_delay=1 if open_browser else None,
        restart_delay=0,
    )
