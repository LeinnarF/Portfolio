"""
Portfolio Static Site Generator & Dev Server CLI.

Usage:
    python main.py build [--base-url /subpath] [--strict]
    python main.py serve [--port 8000] [--host 127.0.0.1] [--no-watch] [--open]

Site configuration and copy (hero text, about section, footer links) are
defined in `content/_site.yaml`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.builder import build
from src.server import serve

ROOT = Path(__file__).parent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Static portfolio site generator and dev server."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build
    build_parser = subparsers.add_parser("build", help="Build the static site to static/")
    build_parser.add_argument(
        "--base-url",
        default=None,
        help="Base URL prefix for deployment (e.g. '/Portfolio' or 'https://user.github.io/Portfolio')",
    )
    build_parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with non-zero status on validation or parsing warnings",
    )

    # serve
    serve_parser = subparsers.add_parser(
        "serve",
        help="Serve the static site locally with live-reload",
    )
    serve_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000)",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--base-url",
        default=None,
        help="Base URL prefix for serving",
    )
    serve_parser.add_argument(
        "--no-watch",
        dest="watch",
        action="store_false",
        default=True,
        help="Disable live reloading and watch mode",
    )
    serve_parser.add_argument(
        "--open",
        action="store_true",
        default=False,
        help="Open the site in your default browser on start",
    )

    args = parser.parse_args()

    content_dir = ROOT / "content"
    templates_dir = ROOT / "templates"
    assets_dir = ROOT / "assets"
    output_dir = ROOT / "static"
    src_dir = ROOT / "src"

    if args.command == "build":
        try:
            build(
                content_dir=content_dir,
                templates_dir=templates_dir,
                assets_dir=assets_dir,
                output_dir=output_dir,
                base_url=args.base_url,
                strict=args.strict,
            )
        except Exception as exc:
            if args.strict:
                sys.exit(f"Build failed in strict mode: {exc}")
            raise
    elif args.command == "serve":
        serve(
            content_dir=content_dir,
            templates_dir=templates_dir,
            assets_dir=assets_dir,
            output_dir=output_dir,
            src_dir=src_dir,
            base_url=args.base_url,
            port=args.port,
            host=args.host,
            watch=args.watch,
            open_browser=args.open,
        )


if __name__ == "__main__":
    main()
